from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter()
def to_int(value):
    return int(value)
    
@register.filter()
def name(user_id):
    if user_id > 0 :
        user = User.objects.get(id=user_id)
        return user.first_name
    else : 
        return ""