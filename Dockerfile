 FROM python:3
 ENV PYTHONUNBUFFERED 1
 
 # Instal Mecab
 RUN apt-get update && apt-get -qq -y install curl 
 RUN apt-get -qq -y install mecab mecab-ipadic-utf8 mecab-jumandic-utf8 libmecab-dev swig

 # Install Django
 WORKDIR /opt/django-app
 ADD requirements.txt /opt/django-app
 RUN pip install -r requirements.txt
 
 ADD django-app /opt/django-app
  