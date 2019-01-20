from rest_auth.views import LoginView
from rest_auth.serializers import UserDetailsSerializer
from django.utils.six import text_type
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
#from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class JWTLoginView(LoginView):

    def login(self):
        self.user = self.serializer.validated_data['user']

        self.token = RefreshToken.for_user(self.user)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()

    def get_response(self):

        user_data = UserDetailsSerializer(self.user, context={'request': self.request}).data

        # Alternative approach: Feed login information to simplejwt serializer
        #token_serializer = TokenObtainPairSerializer(data=self.request.data,context={'request': self.request})
        #assert(token_serializer.is_valid())
        #token_data = token_serializer.validated_data

        data = {
            'user': user_data,
            #'refresh': token_data['refresh'],
            #'access': token_data['access'],
            'refresh': text_type(self.token),
            'access': text_type(self.token.access_token)
        }            

        return Response(data, status=status.HTTP_200_OK)