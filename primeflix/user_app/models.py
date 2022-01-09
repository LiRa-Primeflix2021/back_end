from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from primeflix_app.models import  User, Order

#
# a new order is created if a user has been created
#
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    
    if created:
        Token.objects.create(user=instance)
        Order.objects.create(order_user=instance)
        # if instance.email == None:            
            # Customer.objects.create(user=instance, email=instance.email)
            # Order.objects.create(customer=Customer.objects.get(email=instance.email))          
        # else: 
            # Customer.objects.create(user=instance, email=instance.username)
            # Order.objects.create(customer=Customer.objects.get(email=instance.username))          
        