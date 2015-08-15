# *-* coding: utf-8 *-*

import sys, os
from django.conf import settings

DEBUG = os.environ.get('DEBUG','on') == 'on'
SECRET_KEY = os.environ.get('SECRET_KEY', '^x0piqf_f_sor!bs+c!98ctj6ge4=dqvuetgjalo6ldqg=-wq*')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS','localhost').split(',')

BASE_DIR = os.path.dirname(__file__)

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
	INSTALLED_APPS=(
		'django.contrib.staticfiles',
	),
	TEMPLATE_DIRS=(
		os.path.join(BASE_DIR, 'templates'),
	),
	STATICFILES_DIRS=(
		os.path.join(BASE_DIR, 'static'),
	),
	STATIC_URL='/static/',
)

from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.views.decorators.http import etag
from django.shortcuts import render
from django.core.cache import cache
from django import forms
from io import BytesIO
from PIL import Image, ImageDraw
import hashlib

class ImageForm(forms.Form):
	'''Formulário para validar o placeholder de imagem solicitado'''
	heigth = forms.IntegerField(min_value=1, max_value=2000)
	width = forms.IntegerField(min_value=1, max_value=2000)

	def generate(self, image_format='PNG'):
		'''Gera a imagem do tipo especificado'''
		heigth = self.cleaned_data['heigth']
		width = self.cleaned_data['width']
		key = "{}.{}.{}".format(width,heigth,image_format)
		content = cache.get(key)
		if content is None:
			image = Image.new('RGB',(width, heigth))
			draw = ImageDraw.Draw(image)
			text = "{}x{}".format(width,heigth)
			textwidth, textheigth = draw.textsize(text)
			if textwidth < width and textheigth < heigth:
				texttop = (heigth - textheigth) // 2
				textleft = (width - textwidth) // 2
				draw.text((textleft,texttop), text, fill = (255,255,255))
			content = BytesIO()
			image.save(content, image_format)
			content.seek(0)
			cache.set(key, content, 60 * 60)
		return content

def generate_etag(request, width, heigth):
	content = 'Placeholder: {0} x {1}'.format(width, heigth)
	return hashlib.sha1(content.encode('utf-8')).hexdigest()

@etag(generate_etag)
def placeholder(request, width, heigth):
	form = ImageForm({'heigth':heigth, 'width':width})
	if form.is_valid():
		heigth = form.cleaned_data['heigth']
		width = form.cleaned_data['width']
		image = form.generate()
		return HttpResponse(image, content_type='image/png')
	return HttpResponseBadRequest('Requisição Inválida')

def index(request):
	example = reverse('placeholder', kwargs={'width':50, 'heigth':50})
	context = {
		'example': request.build_absolute_uri(example)
	}
	return render(request, 'home.html', context)

from django.conf.urls import url

urlpatterns = (
	url(r'^image/(?P<width>[0-9]+)x(?P<heigth>[0-9]+)/$', placeholder, name="placeholder"),
	url(r'^$', index, name="homepage"),
	)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

if __name__ == "__main__":
	from django.core.management import execute_from_command_line
	if len(sys.argv) > 0:
		execute_from_command_line(sys.argv)
