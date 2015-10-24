# *-* coding: utf-8 *-*
import django_filters
from django.contrib.auth import get_user_model
from .models import Task, Sprint

User = get_user_model()

class NullFilter(django_filters.BooleanFilter):
    '''Filtra de acordo com um campo definido como nulo ou nao'''

    def filter(self, qs, value):
        if value is not None:
            return qs.filter(**{'%s__isnull'% self.name: value})
        return qs

class TaskFilter(django_filters.FilterSet):

    backlog = NullFilter(name='sprint')#caso o backlog seja true trara os resultados com o Sprint nulo

    class Meta:
        model = Task
        fields = ('sprint', 'status', 'assigned',)

    def __init__(self, *args, **kwargs):
        django_filters.FilterSet.__init__(self, *args, **kwargs) #Python 2
        # only Python 3
        #super().__init__(*args, **kwargs)
        self.filters['assigned'].extra.update({'to_field_name': User.USERNAME_FIELD })#Filtragem será feita pelo campo username

class SprintFilter(django_filters.FilterSet):
    end_min = django_filters.DateFilter(name='end', lookup_type='gte')#maior ou igual
    end_max = django_filters.DateFilter(name='end', lookup_type='lte')#menor ou igual

    class Meta:
        model = Sprint
        fields = ('end_min', 'end_max',)
