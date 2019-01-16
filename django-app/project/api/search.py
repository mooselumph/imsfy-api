from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import connections, Search, Document, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text, Integer
    
from hashlib import md5

connections.create_connection(hosts=['es:9200'])

kuromoji = analyzer('kuromoji',
    tokenizer="kuromoji_tokenizer",
    filter=["kuromoji_part_of_speech", "ja_stop"],
    char_filter=["html_strip"]
)

import re

def segment_sentences(content):
    # Split sentences at explicit newlines, english and japanese end of sentence markers.
    sentences = re.findall(r"((?:(?:「.+?」)?.*?)+[\n\.\?!。？！]+)",content+"\n") 
    return sentences
        
    
class Sentence(InnerDoc):
    content = Text(analyzer=kuromoji)
    order = Integer()
    viewers = Integer()
    
    def add_viewer(self, userId):
        self.viewers.append(User(id=userId))
                

class Article(Document):
    url = Keyword()
    latest = Boolean()
    added = Date()
    checksum = Keyword()
    title = Text()
    sentences = Nested(Sentence)    
    viewers = Integer()
        
    def add_sentences(self,sentences):
        order = 0
        for sentence in sentences:
            if (sentence['type']=='sentence'):
                self.sentences.append(Sentence(content=sentence['text'],order=order))
            order = order + 1
            
    def has_viewer(self,userId):
        return userId in self.viewers
            
    def add_viewer(self,userId):
        if self.viewers is None:
            self.viewers = [userId]
        elif not self.has_viewer(userId):
            self.viewers.append(userId)
            
    def remove_viewer(self,userId):
        if self.has_viewer(userId):
            self.viewers.remove(userId)
    
    def analyze_sentences(self):
    
        ic = IndicesClient(Elasticsearch())
        
        sentences = []        
        for sentence in self.sentences:
            r = ic.analyze(body={'tokenizer':'kuromoji_tokenizer','filter':[],'char_filter':['html_strip'],'text':sentence.content})
            tokens = [token['token'] for token in r['tokens']]
            sentences.append({'order':sentence.order,'tokens':tokens})
            
        return sentences
            
    class Index:
        name = 'articles'
        
    def save(self, ** kwargs):
    
        if self.added is None:
            self.added = datetime.utcnow()
        if self.latest is None:
            self.latest = True
            
        return super().save(** kwargs)
     
     
def index_article(userId,url,title,content,sentences):

    # Calculate checksum
    signature = title + content
    checksum = md5( signature.encode("utf-8") ).hexdigest()
        
    s = Article.search()  
    s = s.filter('term', url=url).filter('term', latest=True)
    
    response = s.execute()
    existed = bool(response)
    
    if existed:
        article = response[0]
        identical = article.checksum == checksum
    else:
        identical = False

    # Check exact article already exists
    created = not existed or not identical
    if created:
        if existed:
        
            # Change previous article latest status to False, remove current user if they are attached
            article.remove_viewer(userId)
            article.latest = False
            article.save()

        article = Article(title=title, checksum=checksum, url=url)
        article.add_sentences(sentences)
        

    # Attach viewer and save
    article.add_viewer(userId)    
    article.save()
        
    return {'created':created,'existed':existed,'identical':identical,'article':article}

    
def bulk_index():
    Article.init()
    #es = Elasticsearch()
    #bulk(client=es, actions=(b.indexing() for b in models.BlogPost.objects.all().iterator()))

def reset_index():
    es = Elasticsearch(host='es')
    es.indices.delete(index='articles', ignore=[400, 404])
    Article.init()

 
def sentence_search(term):

    es = Elasticsearch(host='es')

    q = {
        "_source" : False,
        "query": {
            "nested": {
                "path": "sentences",
                    "query": {
                        "bool": {
                            "must": [{ "match": { "sentences.content": term } }]
                        }
                    },
                "inner_hits" : {}
            }
        }
    }
    
    res = es.search(index='articles', body=q)
    
    articles = res['hits']['hits']
    sentences = []
    
    def parse_sentence(hit):        
        return {'articleId':hit['_id'],'score':hit['_score'],'content':hit['_source']['content']}
    
    for article in articles:
        hits = article['inner_hits']['sentences']['hits']['hits']
        sentences = sentences + [parse_sentence(hit) for hit in hits]
    
        
    return sentences
    