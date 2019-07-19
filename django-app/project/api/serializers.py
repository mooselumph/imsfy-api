from django.contrib.auth.models import User
from project.api.models import Article, Sentence, Word
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')
        

class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    
    # view-name determines the name of the @action method defined in ArticleViewSet that is called. 
    # Format: 'article-METHODNAME'
    # See https://www.django-rest-framework.org/api-guide/routers/ for details
    sentences = serializers.HyperlinkedIdentityField(many=False, view_name='article-sentences', read_only=True)
    words = serializers.HyperlinkedIdentityField(many=False, view_name='article-words', read_only=True)

    class Meta:
        model = Article
        fields = ('url', 'id', 'remote_url', 'title', 'sentences', 'words')

from project.api.functions import get_word_stats

class ArticleWordsSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('stats',)

    def get_stats(self, obj):

        words = obj.words
        user = self.context['request'].user
        stats = get_word_stats(user,words)

        return stats

class SentenceSerializer(serializers.ModelSerializer):
    #sentence = serializers.SerializerMethodField()
    viewed = serializers.SerializerMethodField()

    class Meta:
        model = Sentence
        fields = ('order','category','elements','viewed')

    def get_viewed(self, obj):
        return self.context['request'].user.sentence_set.filter(pk=obj.pk).exists()


        
class ArticleImportSerializer(serializers.Serializer):
    
    remote_url = serializers.URLField()
    title = serializers.CharField()
    content = serializers.CharField(style={'base_template': 'textarea.html'})
    blocks = serializers.JSONField()
    

class SentenceByWordSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Sentence
        fields = ('article','order','category','elements','stats')

    def get_stats(self, obj):

        words = obj.words
        user = self.context['request'].user
        stats = get_word_stats(user,words)

        return stats

    
class SentenceByPhraseSerializer(serializers.Serializer):
    
    sentences = serializers.JSONField()
    

class SentenceEncounterSerializer(serializers.Serializer):
    
    cumulative = serializers.BooleanField()
    
class TokenizerSerializer(serializers.Serializer):
    
    tokenizer = serializers.ChoiceField(choices=['ipadic','naist-jdic','unidic','unidic-kanaaccent','jumandic'])
    sentence = serializers.CharField(style={'base_template': 'textarea.html'})

