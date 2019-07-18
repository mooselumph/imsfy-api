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

        for word in words:

            encounter = Encounter.objects.filter(user=user,word=word)
            if len(encounter) == 0:
                encounter = Encounter(user=user,word=word)
            else:
                encounter = encounter[0]

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
