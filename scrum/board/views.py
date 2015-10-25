# *-* coding:utf-8 *-*
import requests
import hashlib
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner
from rest_framework import authentication, permissions, viewsets, filters
from rest_framework.renderers import JSONRenderer
from .forms import TaskFilter, SprintFilter
from .models import Sprint, Task
from .serializers import SprintSerializer, TaskSerializer, UserSerializer

User = get_user_model()

class UpdateHookMixin(object):
    '''Clase Mixin para enviar informacoes sobre atualização ao servidor de websocket.'''

    def _build_hook_url(self, obj):
        '''Definindo o endpoint que será utilizado'''
        if isinstance(obj, User):
            model = 'user'
        else:
            model = obj.__class__.__name__.lower()
        return '{}://{}/{}/{}'.format(
            'https' if settings.WATERCOOLER_SECURE else 'http',
            settings.WATERCOOLER_SERVER, model, obj.pk
        )

    def _send_hook_request(self, obj, method):
        url = self._build_hook_url(obj)
        if method in ('POST', 'PUT'):
            #compõe o corpo
            serializer = self.get_serializer(obj)
            rendererer = JSONRenderer()
            context = {'request': self.request}
            body = rendererer.render(serializer.data, renderer_context=context)
        else:
            body = None
        headers = {
            'content-type': 'application/json',
            'X-Signature': self._build_hook_signature(method, url, body)
        }
        try:
            s = requests.Session()
            requisicao = requests.Request(method, url, data=body, headers=headers)
            prepared = requisicao.prepare()
            response = s.send(prepared, timeout=0.5)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            # Host não pôde ser resolvido ou a conexão foi recusada
            pass
        except requests.exceptions.Timeout:
            # Solicitação expirou
            pass
        except requests.exceptions.RequestException:
            # Servidor respondeu com código de status 4XX ou 5XX
            pass

    def _build_hook_signature(self, method, url, body):
        signer = TimestampSigner(settings.WATERCOOLER_SECRET)
        value = '{method}:{url}:{body}'.format(
            method = method.lower(),
            url=url,
            body=hashlib.sha256(body or b'').hexdigest()
        )
        return signer.sign(value)

    def perform_create(self, serializer):
        method = 'POST'
        obj = serializer.save()
        self._send_hook_request(obj, method)

    def perform_update(self, serializer):
        obj = serializer.save()
        self._send_hook_request(obj, 'PUT')

    def perform_destroy(self, obj):
        self._send_hook_request(obj, 'DELETE')


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

class SprintViewSet(DefaultMixin, UpdateHookMixin, viewsets.ModelViewSet):
    '''Endpoint da API para listar e criar sprints'''
    queryset = Sprint.objects.order_by('end')
    serializer_class = SprintSerializer
    filter_class = SprintFilter
    search_fields = ('name',)
    ordering_fields = ('end', 'name',)

class TaskViewSet(DefaultMixin, UpdateHookMixin, viewsets.ModelViewSet):
    '''Endpoint da API para listar e criar tarefas'''
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_class = TaskFilter
    search_fields = ('name', 'description,')
    ordering_fields = ('name', 'order', 'started', 'due', 'completed',)

class UserViewSet(DefaultMixin, UpdateHookMixin, viewsets.ReadOnlyModelViewSet):
    '''Endpoint da API para listar usuários'''
    lookup_field = User.USERNAME_FIELD
    lookup_url_kwarg = User.USERNAME_FIELD
    queryset = User.objects.order_by(User.USERNAME_FIELD)
    serializer_class = UserSerializer
    search_fields = (User.USERNAME_FIELD)
