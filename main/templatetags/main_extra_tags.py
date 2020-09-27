from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return Group.objects.get(name=group_name) in user.groups.all()


@register.filter
def get_field_data(field_data, field_id):
    return field_data[field_id] if field_id in field_data.keys() else None
