from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from project.api.serializers import UserSerializer, ArticleSerializer, SentenceSerializer, ArticleImportSerializer, SentenceLookupSerializer, TokenizerSerializer

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

    @action(detail=True)
    def sentences(self, request, *args, **kwargs):
        article = self.get_object()
        sentences = article.sentences.all()
        serializer = SentenceSerializer(sentences,many=True,context={'request': request})
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
            sentences = get_sentences(data['blocks'])

            # Index article, if not already within index            
            result = index_article(userId,data['remote_url'],data['title'],data['content'],sentences)
            
            # Add article to database
            if result['created']:
                a = result['article']
                import_article(data['remote_url'],a.meta.id,data['title'],sentences)

            del result['article']
                
            return Response({'result':result,'data':data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SentenceLookup(APIView):
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
