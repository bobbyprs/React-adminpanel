# from enum import unique
from django.contrib.sessions import models
from django.contrib.sessions.models import Session
from rest_framework import fields, serializers
from rest_framework.views import APIView
from .models import Admin, Clinical, Staff, User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    is_active =serializers.BooleanField(default=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = User
        fields =['id','username','email','password','date_joined','phone_number','last_login','is_active']
        extra_kwargs ={'password':{
            'write_only':True,      
        }}

    def create(self,validated_data):
        users=User.objects.create_user(**validated_data)
        return users

class StaffSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(
    #         required=True,
    #         validators=[UniqueValidator(queryset=Staff.objects.all())]
    #         )
    is_active =serializers.BooleanField(default=True)
    is_staff =serializers.BooleanField(default=True)
    
    class Meta:
        model = Staff
        fields =['id','username','email','phone_number','is_active','is_staff']
        extra_kwargs ={'password':{
            'write_only':True,
           
        }}

    def create(self,validated_data):
        staff=Staff.objects.create_user(**validated_data)
        return staff

class AdminSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=Admin.objects.all())]
            )
    is_active =serializers.BooleanField(default=True)
    is_superuser =serializers.BooleanField(default=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = Admin
        fields =['id','username', 'password','email','date_joined','phone_number','last_login','is_active','is_superuser']
        extra_kwargs ={'password':{
            'write_only':True,
        }}

    def create(self,validated_data):
        admin=Admin.objects.create_user(**validated_data)
        Session.objects.create(admin=admin)
        return admin

class ClinicalSerializer(serializers.ModelSerializer):

    # owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Clinical
        fields =['name','id','disease','minrank','maxrank','url']