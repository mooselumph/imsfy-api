from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from project.api.serializers import (
    UserSerializer, 
    ArticleSerializer, 
    ArticleWordsSerializer,
    RawSentenceSerializer, 
    SentenceSerializer, 
    ArticleImportSerializer, 
    SentenceLookupSerializer, 
    TokenizerSerializer,
    SentenceEncounterSerializer
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, renderers

from project.api.models import Article, import_article
from project.api.permissions import IsOwnerOrReadOnly

from project.api.search import index_article
from project.api.search import sentence_search

# from rest_framework_jwt.authentication import JSONWebTokenAuthentication as JWT

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    
    
class ArticleViewSet(viewsets.ModelViewSet):
    """
    View to list all users in the system.

    * Only admin users are able to access this view.
    """
    
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # For development
    @action(detail=True,url_path='raw-sentences')
    def raw_sentences(self, request, *args, **kwargs):
        article = self.get_object()
        sentences = article.sentences.all()
        serializer = RawSentenceSerializer(sentences,many=True,context={'request': request})
        return Response(serializer.data)

    @action(detail=True)
    def sentences(self, request, *args, **kwargs):
        article = self.get_object()
        sentences = article.sentences.all()
        serializer = SentenceSerializer(sentences,many=True,context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True)
    def words(self, request, *args, **kwargs):
        article = self.get_object()
        serializer = ArticleWordsSerializer(article,many=False,context={'request': request})
        return Response(serializer.data)

from project.api.analysis import get_sentences

class ArticleImport(APIView):
    """
    View to list all users in the system.

    * Only admin users are able to access this view.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ArticleImportSerializer

    def post(self, request, format=None):
        """
        Return a list of all users.
        """
        serializer = ArticleImportSerializer(data=request.data)
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

# For development
class RawSentenceLookup(APIView):
    """
    View to list all users in the system.

    * Only admin users are able to access this view.
    """
    #permission_classes = (permissions.IsAdminUser,)
    serializer_class = SentenceSerializer

    def get(self, request, word, format=None):

        sentences = sentence_search(word)   
        data = {"sentences":sentences}    
            
        serializer = SentenceLookupSerializer(data=data)
        
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SentenceLookup(APIView):
    """
    View to list all users in the system.

    * Only admin users are able to access this view.
    """
    #permission_classes = (permissions.IsAdminUser,)
    serializer_class = SentenceSerializer

    def get(self, request, word, format=None):

        userId = request.user.id

        sentences = sentence_search(word,userId)   
        data = {"sentences":sentences}    
            
        serializer = SentenceLookupSerializer(data=data)
        
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from project.api.functions import add_encounter, remove_encounter

class WordEncounter(APIView):

    def post(self, request, article_id, sentence_num, word, format=None):

        # Add Encounter for Word
        user = request.user
        add_encounter(user,int(article_id),int(sentence_num),word)

        return Response({}, status=status.HTTP_201_CREATED)


class SentenceEncounter(APIView):

    serializer_class = SentenceEncounterSerializer

    def post(self, request, article_id, sentence_num, format=None):

        # Add Encounters for Words in Sentence and Add User to Search Index
        user = request.user
        serializer = SentenceEncounterSerializer(data=request.data)
        if serializer.is_valid():

            add_encounter(user,int(article_id),int(sentence_num),cumulative=serializer.data['cumulative'])

            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        

    def delete(self, request, article_id, sentence_num, format=None):
        
        # Remove Encounters for Words in Sentence and Remove User from Search Index
        user = request.user
        remove_encounter(user,int(article_id),int(sentence_num))

        
from project.api.analysis import tokenize_text       
        

class Tokenizer(APIView):
    """
    View to list all users in the system.

    * Only admin users are able to access this view.
    """
    #permission_classes = (permissions.IsAdminUser,)
    serializer_class = TokenizerSerializer

    renderer_classes = (renderers.BrowsableAPIRenderer,renderers.TemplateHTMLRenderer,)
    
    def post(self, request, format=None):
    
            
        serializer = TokenizerSerializer(data=request.data)
        
        if serializer.is_valid():
        
            type = serializer.data['tokenizer']
            text = serializer.data['sentence']
        
            tokens = tokenize_text(text)
            
            return render(request, 'tokenizer.html', {'tokens': tokens})
            #return Response({'tokens': tokens}, template_name='tokenizer.html')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

