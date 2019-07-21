from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.auth.models import User

# Basic Models

class Article(models.Model):    
    remote_url = models.URLField()
    #latest = models.BooleanField(default=True)
    added = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    es_id = models.CharField(max_length=100)
    words = JSONField(default=dict)

    class Meta:
        ordering = ('added',)
        
class Sentence(models.Model):
    order = models.IntegerField()
    category = models.CharField(max_length=100,default='sentence')
    text = models.TextField(blank=True)
    words = JSONField(default=dict)
    elements = JSONField(default=dict)
    article = models.ForeignKey(Article,related_name='sentences',on_delete=models.CASCADE)
    viewers = models.ManyToManyField(User)
    
    class Meta:
        ordering = ('order',)

# Encounters

class Encounter(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    word = models.CharField(max_length=100,default='')
    sentences = models.ManyToManyField(Sentence)
    last_seen = models.DateTimeField(auto_now=True)

# JMdict

class Word(models.Model):
    id = models.AutoField(primary_key=True)

class Form(models.Model):
    order = models.IntegerField()
    category = models.CharField(max_length=100,default='')
    word = models.ForeignKey(Word,on_delete=models.CASCADE)
    characters = models.CharField(max_length=100,default='')
    information = models.CharField(max_length=1000,default='')
    priority = models.CharField(max_length=100,default='')
    freq_order = JSONField(default=dict)
    restriction = models.CharField(max_length=100,default='')

    class Meta:
        ordering = ('order',)
    

class Sense(models.Model):
    order = models.IntegerField()
    word = models.ForeignKey(Word,on_delete=models.CASCADE)
    restriction = models.CharField(max_length=100,default='')
    xref = models.CharField(max_length=100,default='')
    antonym = models.CharField(max_length=100,default='')
    pos = models.CharField(max_length=100,default='')
    field = models.CharField(max_length=100,default='')
    misc = models.CharField(max_length=500,default='')
    source_lang = models.CharField(max_length=100,default='')
    source_word = models.CharField(max_length=100,default='')
    sense_information = models.CharField(max_length=1000,default='')

    class Meta:
        ordering = ('order',)

class Gloss(models.Model):
    order = models.IntegerField()
    sense = models.ForeignKey(Sense,on_delete=models.CASCADE)
    text = models.CharField(max_length=1000,default='')

    class Meta:
        ordering = ('order',)


# Utility Functions (TODO: move to functions.py)

def import_article(url,es_id,title,sentences,words):

    article = Article(remote_url=url,title=title,es_id=es_id,words=words)
    article.save()
    
    order = 0
    for s in sentences:

        article.sentences.create(order=order,**s)
        order = order + 1

