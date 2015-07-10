# *-* coding: utf-8 *-*
import os, json
from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.template import Template, Context
from django.template.loader_tags import BlockNode 
from django.utils._os import safe_join

def get_page_or_404(name):
	try:
		file_path = safe_join(settings.SITE_PAGES_DIRECTORY, name)
	except ValueError:
		raise Http404('Página não encontrada')
	else:
		if not os.path.exists(file_path):
			raise Http404('Página não encontrada')

	with open(file_path, 'r') as arquivo:
		page = Template(arquivo.read())
	meta = None
	for i, node in enumerate(list(page.nodelist)):
		if isinstance(node, BlockNode) and node.name == 'context':
			meta = page.nodelist.pop(i)
			break
	page._meta = meta
	return page

def page(request, slug='index'):
	file_name = '{}.html'.format(slug)
	page = get_page_or_404(file_name)
	context = {
		'slug': slug,
		'page': page,
	}
	if page._meta is not None:
		meta = page._meta.render(Context())
		extra_context = json.loads(meta)
		context.update(extra_context)
	return render(request, 'page.html', context)