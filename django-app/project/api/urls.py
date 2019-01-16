from django.conf.urls import url, include
from rest_framework import routers
from project.api import views
from rest_framework_jwt.views import refresh_jwt_token

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'article', views.ArticleViewSet)

#article_sentences = ArticleViewSet.as_view({'get': 'sentences'})

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^refresh-token/', refresh_jwt_token),
    url(r'^import/article/$',views.ArticleImport.as_view(),name='import-article'),
    url(r'^word/(?P<word>\w+)/sentences/$',views.SentenceLookup.as_view(),name='sentence-by-word'),
    url(r'^tokenize/',views.Tokenizer.as_view(),name='tokenizer'),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls')),
]