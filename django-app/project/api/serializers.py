from django.contrib.auth.models import User
from rest_framework import serializers

from project.api import models

from project.api.functions import get_word_stats

#
# For Viewsets
# 

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
        model = models.Article
        fields = ('url', 'id', 'remote_url', 'title', 'sentences', 'words')

class SentenceSerializer(serializers.ModelSerializer):
    #sentence = serializers.SerializerMethodField()
    viewed = serializers.SerializerMethodField()

    class Meta:
        model = models.Sentence
        fields = ('order','category','elements','viewed')

    def get_viewed(self, obj):
        return self.context['request'].user.sentence_set.filter(pk=obj.pk).exists()

class ArticleWordsSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = models.Article
        fields = ('stats',)

    def get_stats(self, obj):

        words = obj.words
        user = self.context['request'].user
        stats = get_word_stats(user,words)

        return stats

#
# For Article Import
#
        
class ArticleImportSerializer(serializers.Serializer):
    
    remote_url = serializers.URLField()
    title = serializers.CharField()
    content = serializers.CharField(style={'base_template': 'textarea.html'})
    blocks = serializers.JSONField()

#
# For Search Capability
#  

class SentenceByWordSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = models.Sentence
        fields = ('article','order','category','elements','stats')

    def get_stats(self, obj):

        words = obj.words
        user = self.context['request'].user
        stats = get_word_stats(user,words)

        return stats

from project.api.functions import sentence_by_article

class ArticleByWordSerializer(serializers.ModelSerializer):

    selected_sentences = serializers.SerializerMethodField()
    count = serializers.IntegerField()

    class Meta:
        model = models.Article
        fields = ('id','title','count','selected_sentences')

    def get_selected_sentences(self,obj):

        sentences = sentence_by_article(self.context['request'].user,obj,self.context['word'])[:3]

        serializer = SentenceByWordSerializer(sentences,many=True,context=self.context)
        return serializer.data

class SentenceByPhraseSerializer(serializers.Serializer):
    
    sentences = serializers.JSONField()

#
# For Word and Sentence Encounters
#

class SentenceEncounterSerializer(serializers.Serializer):
    
    cumulative = serializers.BooleanField()

#
# For Dictionary
#


class FormSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Form
        fields = ('category','characters','information','priority','restriction')

class GlossSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Gloss
        fields = ('text',)
        
class SenseSerializer(serializers.ModelSerializer):
    glosses = GlossSerializer(many=True, read_only=True)

    class Meta:
        model = models.Sense
        fields = ('glosses','pos','field','misc')


class DictionaryLookupSerializer(serializers.ModelSerializer):
    forms = FormSerializer(many=True, read_only=True)
    senses = SenseSerializer(many=True, read_only=True)

    class Meta:
        model = models.Word
        fields = ('forms','senses')

#
# Tokenization
#

class TokenizerSerializer(serializers.Serializer):
    
    tokenizer = serializers.ChoiceField(choices=['ipadic','naist-jdic','unidic','unidic-kanaaccent','jumandic'])
    sentence = serializers.CharField(style={'base_template': 'textarea.html'})
   