# *-* coding: utf-8 *-*

'''Arquivo settings.py'''

import sys, os
from django.conf import settings

DEBUG = os.environ.get('DEBUG','on') == 'on'
SECRET_KEY = os.environ.get('SECRET_KEY', '{{ secret_key}}')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS','localhost').split(',')

settings.configure(
	DEBUG = DEBUG,
	SECRET_KEY=SECRET_KEY,
	ALLOWED_HOSTS = ALLOWED_HOSTS,
	ROOT_URLCONF=__name__,
	MIDDLEWARE_CLASSES=(
		'django.middleware.common.CommonMiddleware',
		'django.middleware.csrf.CsrfViewMiddleware',
		'django.middleware.clickjacking.XFrameOptionsMiddleware',
	),
)

'''Arquivo views.py'''
from django.http import HttpResponse

def index(request):
	return HttpResponse("Olá mundo")

'''Arquivo urls.py'''
from django.conf.urls import url

urlpatterns = (url(r'^$', index), )

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

'''Arquivo manage.py'''
if __name__ == "__main__":
	from django.core.management import execute_from_command_line
	if len(sys.argv) > 0:
		execute_from_command_line(sys.argv)