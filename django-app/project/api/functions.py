# Functions that span both search and models

from project.api.models import Article, Encounter
from project.api.search import Article as ArticleIndex

def add_encounter(user,article_id,sentence_num,word=None,cumulative=True):

    start = 0 if cumulative else sentence_num

    article = Article.objects.get(id=article_id)
    sentences = article.sentences.filter(order__in=range(start,sentence_num+1))

    for sentence in sentences:

        method = 'word' if word else 'sentence'
        words = [word] if word else sentence.words

        for w in words:

            try: 
                encounter = Encounter.objects.get(user=user,word=w)
            except: 
                encounter = Encounter(user=user,word=w)
                encounter.save()

            encounter.sentences.add(sentence)

        # Register viewer of sentence in Database
        sentence.viewers.add(user)

    # Register viewer of sentence in Search Index
    if method == 'sentence':
        article_es = ArticleIndex.search().query('match',_id=article.es_id).execute()
        if len(article_es):
            for order in range(start,sentence_num+1):
                article_es[0].sentences[order].add_viewer(user.id)
            article_es[0].save()

def remove_encounter(user,article_id,sentence_num,word=None):

    article = Article.objects.get(id=article_id)
    sentence = article.sentences.get(order=sentence_num)

    encounters = Encounter.objects.filter(sentences=sentence)

    for encounter in encounters:
        encounter.sentences.remove(sentence)

    # Deregister viewer of sentence in Database
    sentence.viewers.remove(user)

    # Deregister viewers of sentence in Search Inex
    article_es = ArticleIndex.search().query('match',_id=article.es_id).execute()
    if len(article_es):
        article_es[0].sentences[sentence.order].remove_viewer(user.id)


def get_word_stats(user,words):

    stats = {}

    for word in words:

        stats[word] = learning_curve(user,word)

    return stats


        

from django.utils import timezone
from math import exp

def learning_curve(user,word):
    
    rating = 0

    try:
        encounter = Encounter.objects.get(user=user,word=word)
    except:
        encounter = None

    if encounter:
        count = encounter.sentences.count()
        
        time_factor = (timezone.now() - encounter.last_seen).total_seconds()/1e6
        rating = count*exp(-time_factor)

    return rating


from project.api.models import Sentence

def sentence_by_word(user,word):

    encounters = Encounter.objects.filter(user=user,word=word)

    sentences = Sentence.objects.filter(encounter__in=encounters)

    #sentences = [encounter.sentences for encounter in encounters]
    #sentences = list(set(sentences))    
        
    return sentences