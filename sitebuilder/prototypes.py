#!/usr/bin/env python
# *-* coding: utf-8 *-*
import os
import sys
from django.conf import settings

BASE_DIR = os.path.dirname(__file__)

settings.configure(
	DEBUG=True,
	SECRET_KEY='secret_key',
	ROOT_URLCONF='sitebuilder.urls',
	MIDDLEWARE_CLASSES=(),
	INSTALLED_APPS=(
		'django.contrib.staticfiles',
		'sitebuilder',
		'compressor',
	),
	COMPRESS_ENABLED=True,
	STATIC_URL='/static/',
	STATIC_ROOT=os.path.join(BASE_DIR, '_build','static'),
	SITE_PAGES_DIRECTORY=os.path.join(BASE_DIR, 'pages'),
	SITE_OUTPUT_DIRECTORY=os.path.join(BASE_DIR, '_build'),
	STATICFILES_FINDERS=(
		'django.contrib.staticfiles.finders.FileSystemFinder',
		'django.contrib.staticfiles.finders.AppDirectoriesFinder',
		'compressor.finders.CompressorFinder',
	),
)

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
