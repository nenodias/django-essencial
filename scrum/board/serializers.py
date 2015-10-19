# *-* coding:utf-8 *-*
from datetime import date
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Sprint, Task
User = get_user_model()

class SprintSerializer(serializers.ModelSerializer):
	links = serializers.SerializerMethodField()

	class Meta:
		model = Sprint
		fields = ('id', 'name', 'description', 'end' ,'links',)

	def get_links(self, obj):
		request = self.context['request']
		return {
			'self':reverse('sprint-detail', kwargs={'pk':obj.pk}, request=request),
			'tasks':reverse('task-list', request=request) + '?sprint={}'.format(obj.pk),
			'channel': '{proto}://{server}/{channel}'.format(
				proto='wss' if settings.WATERCOOLER_SECURE else 'ws',
				server=settings.WATERCOOLER_SERVER,
				channel=obj.pk
			),
		}

	def validate_end(self, value):
		new = not self.instance
		changed = self.instance and self.instance.end != end_date
		if (new or changed) and (value < date.today()):
			msg = _('End date cannot be in the past')
			raise serializers.ValidationError(msg)
		return value

class TaskSerializer(serializers.ModelSerializer):
	status_display = serializers.SerializerMethodField()
	links = serializers.SerializerMethodField()
	assigned = serializers.SlugRelatedField(slug_field=User.USERNAME_FIELD, required=False, queryset=User.objects.all())
	class Meta:
		model = Task
		fields = ('id', 'name', 'description', 'sprint', 'status', 'status_display', 'order', 'assigned', 'started', 'due', 'completed','links',)

	def get_status_display(self, obj):
		return obj.get_status_display()

	def get_links(self, obj):
		request = self.context['request']
		links = {
			'self':reverse('task-detail', kwargs={'pk':obj.pk}, request=request),
		}
		if obj.sprint_id:
			links['sprint'] = reverse('sprint-detail', kwargs={"pk":obj.sprint_id}, request=request)
		if obj.assigned:
			links['assigned'] = reverse('user-detail', kwargs={User.USERNAME_FIELD:obj.assigned}, request=request)
		return links

	def validate_sprint(self, value):
		if self.instance and self.instance.pk:
			if value != self.instance.sprint:
				if self.instance.status == Task.STATUS_DONE:
					msg = _('Cannot change the sprint of a completed task.')
					raise serializers.ValidationError(msg)
				if value and value.end < date.today():
					msg = _('Cannot assign taks to past sprints')
					raise serializers.ValidationError(msg)
			else:
				if value and value.end < date.today():
					msg = _('Cannot add taks tp past sprints')
					raise serializers.ValidationError(msg)
			return value
	def validate(self, data):
		sprint = data.get('sprint')
		status = data.get('status', Task.STATUS_TODO)
		started = data.get('started')
		completed = data.get('completed')
		msg = None
		if not sprint and (status != Task.STATUS_TODO):
			msg = _('Backlog taks must have "Not Started" status')
		if started and (status == Task.STATUS_TODO):
			msg = _('Started date cannot be set for not started tasks')
		if completed and (status != Task.STATUS_DONE):
			msg = _('Completed date cannot be set for uncompleted tasks')
		if msg:
			raise serializers.ValidationError(msg)
		return data


class UserSerializer(serializers.ModelSerializer):
	links = serializers.SerializerMethodField()
	full_name = serializers.CharField(source='get_full_name', read_only=True)

	class Meta:
		model = User
		fields = ('id', User.USERNAME_FIELD, 'full_name', 'is_active','links',)

	def get_links(self, obj):
		request = self.context['request']
		username = obj.get_username()
		return {
			'self':reverse('user-detail', kwargs={User.USERNAME_FIELD : username}, request=request),
			'tasks': '{}?assigned={}'.format(reverse('task-list', request=request), username)
		}
