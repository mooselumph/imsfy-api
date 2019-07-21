from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, renderers

from project.api import serializers
from project.api import models

from project.api.permissions import IsOwnerOrReadOnly


# from rest_framework_jwt.authentication import JSONWebTokenAuthentication as JWT

#
# Utilities
#

from rest_framework.pagination import LimitOffsetPagination

class SmallResultsSetPagination(LimitOffsetPagination):
    default_limit = 5


#
# Viewsets (Not yet paginated)
# 

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
class ArticleViewSet(viewsets.ModelViewSet):
    """
    View to list all articles.
    """
    
    queryset = models.Article.objects.all()
    serializer_class = serializers.ArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @action(detail=True)
    def sentences(self, request, *args, **kwargs):
        article = self.get_object()
        sentences = article.sentences.all()
        serializer = serializers.SentenceSerializer(sentences,many=True,context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True)
    def words(self, request, *args, **kwargs):
        article = self.get_object()
        serializer = serializers.ArticleWordsSerializer(article,many=False,context={'request': request})
        return Response(serializer.data)

#
# Import
#

from project.api.search import index_article
from project.api.models import import_article
from project.api.analysis import get_sentences

class ArticleImport(APIView):
    """
    View to import an article
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ArticleImportSerializer

    def post(self, request, format=None):
        """
        Return a list of all users.
        """
        serializer = serializers.ArticleImportSerializer(data=request.data)
        if serializer.is_valid():
            
            userId = request.user.id
            data = serializer.validated_data

            # Perform Sentence Segmentation
            sentences,words = get_sentences(data['blocks'])

            # Index article, if not already within index            
            result = index_article(userId,data['remote_url'],data['title'],data['content'],sentences)
            
            # Add article to database
            if result['created']:
                a = result['article']
                import_article(data['remote_url'],a.meta.id,data['title'],sentences,words)

            del result['article']
                
            return Response({'result':result,'data':data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
#  Search Views
#

from project.api.search import sentence_by_phrase

class SentenceByPhrase(APIView):
    """
    Look up a sentence based on a phrase. Does not make use of paging. Makes use of Elasticsearch capability.
    """
    #permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.SentenceByPhraseSerializer

    def get(self, request, word, format=None):

        userId = request.user.id

        sentences = sentence_by_phrase(word,userId)   
        data = {"sentences":sentences}    
            
        serializer = serializers.SentenceByPhraseSerializer(data=data)
        
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from project.api.functions import sentence_by_word

class SentenceByWordOrig(APIView):
    """
    Look up a sentence by a word. Does not make use of paging. (Deprecated)
    """
    #permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.SentenceByWordSerializer

    def get(self, request, word, format=None):

        sentences = sentence_by_word(request.user,word)   
            
        serializer = serializers.SentenceByWordSerializer(sentences,many=True,context={'request': request})
        
        return Response(serializer.data)

class SentenceByWord(ListAPIView):
    """
    Look up sentence by word. 
    """
    #permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.SentenceByWordSerializer
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):

        sentences = sentence_by_word(self.request.user,self.kwargs['word'])
        return sentences

from project.api.functions import article_by_word

class ArticleByWord(ListAPIView):

    """
    List all articles containing a word, sorted by number of sentences viewed by user. 
    """

    serializer_class = serializers.ArticleByWordSerializer
    pagination_class = SmallResultsSetPagination

    def get_serializer_context(self):
        return {'request':self.request,'word': self.kwargs['word']}

    def get_queryset(self):

        articles = article_by_word(self.request.user,self.kwargs['word'])
        return articles

from project.api.functions import sentence_by_article

class SentenceByArticleAndWord(ListAPIView):
    """
    List sentences containing word for a given article. 
    """

    serializer_class = serializers.SentenceByWordSerializer
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):

        sentences = sentence_by_article(self.request.user,self.kwargs['article_id'],self.kwargs['word'])
        return sentences


#
# Word and Sentence Encounters
#

from project.api.functions import add_encounter, remove_encounter

class WordEncounter(APIView):
    """
    Allows registration of an encounter with a specific word.
    """

    def post(self, request, article_id, sentence_num, word, format=None):

        # Add Encounter for Word
        user = request.user
        add_encounter(user,int(article_id),int(sentence_num),word)

        return Response({}, status=status.HTTP_201_CREATED)


class SentenceEncounter(APIView):
    """
    Allows registration of an encounter with a sentence.
    """

    serializer_class = serializers.SentenceEncounterSerializer

    def post(self, request, article_id, sentence_num, format=None):

        # Add Encounters for Words in Sentence and Add User to Search Index
        user = request.user
        serializer = serializers.SentenceEncounterSerializer(data=request.data)
        if serializer.is_valid():

            add_encounter(user,int(article_id),int(sentence_num),cumulative=serializer.data['cumulative'])

            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, article_id, sentence_num, format=None):
        
        # Remove Encounters for Words in Sentence and Remove User from Search Index
        user = request.user
        remove_encounter(user,int(article_id),int(sentence_num))


#
# Tokenization (For development)
#
        
from project.api.analysis import tokenize_text_old      
        

class Tokenizer(APIView):
    """
    Tokenize an arbitrary text input
    """
    #permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.TokenizerSerializer

    renderer_classes = (renderers.BrowsableAPIRenderer,renderers.TemplateHTMLRenderer,)
    
    def post(self, request, format=None):
    
            
        serializer = serializers.TokenizerSerializer(data=request.data)
        
        if serializer.is_valid():
        
            type = serializer.data['tokenizer']
            text = serializer.data['sentence']
        
            tokens = tokenize_text_old(text)
            
            return render(request, 'tokenizer.html', {'tokens': tokens})
            #return Response({'tokens': tokens}, template_name='tokenizer.html')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

