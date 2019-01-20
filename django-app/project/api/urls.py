from django.conf.urls import url, include
from rest_framework import routers
from project.api import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .auth.views import JWTLoginView

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'article', views.ArticleViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/login/$',JWTLoginView.as_view(), name='rest_login'),
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/registration/', include('rest_auth.registration.urls')),
    url(r'^auth/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^auth/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^auth/token/verify/$', TokenVerifyView.as_view(), name='token_verify'),
    url(r'^import/article/$',views.ArticleImport.as_view(),name='import-article'),
    url(r'^word/(?P<word>\w+)/sentences/$',views.SentenceLookup.as_view(),name='sentence-by-word'),
    url(r'^tokenize/',views.Tokenizer.as_view(),name='tokenizer'),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls')),
]