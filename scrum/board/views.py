# *-* coding:utf-8 *-*
from django.contrib.auth import get_user_model
from rest_framework import authentication, permissions, viewsets, filters
from .forms import TaskFilter, SprintFilter
from .models import Sprint, Task
from .serializers import SprintSerializer, TaskSerializer, UserSerializer

User = get_user_model()

class DefaultMixin(object):
	'''Configurações default para autenticação, permissões, filtragem e paginação da view '''
	authentication_classes = (
		authentication.BasicAuthentication,
		authentication.TokenAuthentication,
	)
	permission_classes = (
		permissions.IsAuthenticated,
	)

	paginated_by = 25
	paginated_by_param = 'page_size'
	max_paginate_by = 100

	filter_backends = (
		filters.DjangoFilterBackend,
		filters.SearchFilter,
		filters.OrderingFilter,
	)

class SprintViewSet(DefaultMixin, viewsets.ModelViewSet):
	'''Endpoint da API para listar e criar sprints'''
	queryset = Sprint.objects.order_by('end')
	serializer_class = SprintSerializer
	filter_class = SprintFilter
	search_fields = ('name',)
	ordering_fields = ('end', 'name',)

class TaskViewSet(DefaultMixin, viewsets.ModelViewSet):
	'''Endpoint da API para listar e criar tarefas'''
	queryset = Task.objects.all()
	serializer_class = TaskSerializer
	filter_class = TaskFilter
	search_fields = ('name', 'description,')
	ordering_fields = ('name', 'order', 'started', 'due', 'completed',)

class UserViewSet(DefaultMixin, viewsets.ReadOnlyModelViewSet):
	lookup_field = User.USERNAME_FIELD
	lookup_url_kwarg = User.USERNAME_FIELD
	queryset = User.objects.order_by(User.USERNAME_FIELD)
	serializer_class = UserSerializer
	search_fields = (User.USERNAME_FIELD)