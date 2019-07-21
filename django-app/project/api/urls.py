from django.conf.urls import url, include
from rest_framework import routers
from project.api import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .auth.views import JWTLoginView

# Routers
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'article', views.ArticleViewSet)


# Auth
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^auth/login/$',JWTLoginView.as_view(), name='rest_login'), # This needs to come before rest_auth.urls
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/registration/', include('rest_auth.registration.urls')),
    url(r'^auth/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^auth/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^auth/token/verify/$', TokenVerifyView.as_view(), name='token_verify'),
]

# Import
urlpatterns += [
    url(r'^import/article/$',views.ArticleImport.as_view(),name='import-article'), 
]

# Encounter Information
urlpatterns += [
    url(r'^encounter/article/(?P<article_id>\w+)/sentence/(?P<sentence_num>\w+)/$',views.SentenceEncounter.as_view(),name='sentence-encounter'), 
    url(r'^encounter/article/(?P<article_id>\w+)/sentence/(?P<sentence_num>\w+)/word/(?P<word>\w+)/$',views.WordEncounter.as_view(),name='word-encounter'), 
]

# Sentence Search (All Paginated)
urlpatterns += [
    url(r'^phrase/(?P<word>\w+)/sentences/$',views.SentenceByPhrase.as_view(),name='sentences-by-phrase'), # For development
    url(r'^word/(?P<word>\w+)/sentences/$',views.SentenceByWord.as_view(),name='sentences-by-word'), 
    url(r'^word/(?P<word>\w+)/articles/$',views.ArticleByWord.as_view(),name='articles-by-word'), 
    url(r'^word/(?P<word>\w+)/article/(?P<article_id>\w+)/sentences/$',views.SentenceByArticleAndWord.as_view(),name='sentences-by-article-and-word'), 
]

# Development
urlpatterns += [ 
    url(r'^tokenize/',views.Tokenizer.as_view(),name='tokenizer'),
]