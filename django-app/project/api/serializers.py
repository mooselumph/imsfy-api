from django.contrib.auth.models import User
from project.api.models import Article, Sentence
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')
        

class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    
    sentences = serializers.HyperlinkedIdentityField(many=False, view_name='article-sentences', read_only=True)
    
    class Meta:
        model = Article
        fields = ('url', 'id', 'remote_url', 'title', 'sentences')

class SentenceSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Sentence
        fields = ('order','content','article')
    
        
class ArticleImportSerializer(serializers.Serializer):
    
    remote_url = serializers.URLField()
    title = serializers.CharField()
    content = serializers.CharField(style={'base_template': 'textarea.html'})
    blocks = serializers.JSONField()
    
    
class SentenceLookupSerializer(serializers.Serializer):
    
    sentences = serializers.JSONField()
    
    
class TokenizerSerializer(serializers.Serializer):
    
    tokenizer = serializers.ChoiceField(choices=['ipadic','naist-jdic','unidic','unidic-kanaaccent','jumandic'])
    sentence = serializers.CharField(style={'base_template': 'textarea.html'})