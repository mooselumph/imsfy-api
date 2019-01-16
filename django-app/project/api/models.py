from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.
class Article(models.Model):    
    remote_url = models.URLField()
    #latest = models.BooleanField(default=True)
    added = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    es_id = models.CharField(max_length=100)

    class Meta:
        ordering = ('added',)
        
class Sentence(models.Model):
    order = models.IntegerField()
    content = JSONField()
    article = models.ForeignKey(Article,related_name='sentences',on_delete=models.CASCADE)
    
    class Meta:
        ordering = ('order',)
        
def import_article(url,es_id,title,sentences):

    article = Article(remote_url=url,title=title,es_id=es_id)
    article.save()
    
    order = 0
    for s in sentences:
        article.sentences.create(order=order,content=dict(s))
        order = order + 1