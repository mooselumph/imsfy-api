from django.contrib.auth.models import User
from project.api.models import Article, Sentence
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')
        

class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    
    # view-name determines the name of the @action method defined in ArticleViewSet that is called. 
    # Format: 'article-METHODNAME'
    # See https://www.django-rest-framework.org/api-guide/routers/ for details
    raw_sentences = serializers.HyperlinkedIdentityField(many=False, view_name='article-raw-sentences', read_only=True)
    sentences = serializers.HyperlinkedIdentityField(many=False, view_name='article-sentences', read_only=True)
    words = serializers.HyperlinkedIdentityField(many=False, view_name='article-words', read_only=True)

    class Meta:
        model = Article
        fields = ('url', 'id', 'remote_url', 'title', 'raw_sentences', 'sentences', 'words')

class ArticleWordsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ('words',)


class RawSentenceSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Sentence
        fields = ('order','content','article')

# This serializer must take the sentence object and user and provide the customized output

class SentenceSerializer(serializers.ModelSerializer):
    sentence = serializers.SerializerMethodField()

    class Meta:
        model = Sentence
        fields = ('sentence',)

    # get_<name-of-field>
    def get_sentence(self, obj):
        user = self.context['request'].user
        return obj.get_loaded_json(user)

        
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