from typing import ValuesView
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2',]
        extra_kwargs = {
            'password' : {'write_only' : True}
        }
        
    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        
        if (password != password2):
            raise serializers.ValidationError({'error' : 'passwords should be same'})
        
        # if User.objects.filter(email=self.validated_data['email']).exists():
        #     raise serializers.ValidationError({'error' : 'email already exists'})
        
        temp_user = User(email=self.validated_data['email'], username=self.validated_data['username'])
        # temp_user = User(username=self.validated_data['username'])
        temp_user.set_password(password)
        temp_user.save()
        
        return temp_user
    
    
  
class UpdateProfileSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
        
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',  'email', 'password', 'password2',]
        
    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        
        if (password != password2):
            raise serializers.ValidationError({'error' : 'passwords are different'})
        
        temp_user = User.objects.get(username=self.validated_data['username'])
        temp_user.first_name = self.validated_data['first_name']
        temp_user.last_name = self.validated_data['last_name']
        temp_user.email = self.validated_data['email']
        temp_user.set_password(password)
        temp_user.save()

        return temp_user