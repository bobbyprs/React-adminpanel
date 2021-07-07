from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.core.mail import send_mail,EmailMessage
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.fields import ReadOnlyField
from django.db.models import Q
from multiselectfield import MultiSelectField



# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self,email,username,is_active,password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("User must have an username")
    
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            # phone_number=phone_number,
            password=password,
        )
        
        
        user.set_password(password)
        # send_mail(
        #     'Subject',
        #     use_password,
        #     settings.DEFAULT_FROM_EMAIL,
        #     [email],
        #     fail_silently=False,
        # )
        user.is_active =True
        user.save(using=self._db)
        return user
        
    def create_superuser(self,username, email,password):

        if not email:
            raise ValueError("Users must have an email address")

        if not username:
            raise ValueError("User must have an username")

        user = self.create_user(
           email=self.normalize_email(email),
            username=username,
            password=password,
            # phone_number=phone_number,
            is_active= True,
            
            )
        user.set_password(password)
       
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        # user.is_active = True
        user.save(using=self._db)
        return user

class AdminManager(BaseUserManager):

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args,**kwargs).filter(Q(type__contains = User.Types.ADMIN))


    def create_user(self,email,username,phone_number,is_active,password,is_superuser):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("User must have an username")
        if not phone_number:
            raise  ValueError("User must have an phone number")
        

        user =self.model(
            email=self.normalize_email(email),
            username=username,
            phone_number=phone_number,
            password=password,
            
        )
        user.set_password(password)
        # send_mail(
        #     'Subject',
        #     use_password,
        #     settings.DEFAULT_FROM_EMAIL,
        #     [email],
        #     fail_silently=False,
        # )
        user.is_active =True
        user.is_superuser = True
        user.type =User.Types.ADMIN
        user.save(using=self._db)
        
        return user


class StaffManager(BaseUserManager):

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args,**kwargs).filter(Q(type__contains = User.Types.STAFF))


    def create_user(self,email,username,phone_number,is_active,is_staff,password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("User must have an username")
        if not phone_number:
            raise  ValueError("User must have an phone number")
        

        user =self.model(
            email=self.normalize_email(email),
            username=username,
            phone_number=phone_number,
            
        )
        
        use_password=get_random_string(length=12)
        user.set_password(use_password)
        send_mail(
            'Subject',
            use_password,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        user.is_active =True
        user.is_staff=True
        user.type =User.Types.STAFF
        user.save(using=self._db)
        
        return user

class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=60,null=True,blank=True,unique=True)
    email = models.EmailField(verbose_name="email",max_length=60,unique=True)
    phone_number =  PhoneNumberField(null=True,blank=True)
    password = models.CharField(max_length=120,null=False,blank=False)
    date_joined =models.DateTimeField(verbose_name='date_joined',auto_now_add=True)
    last_login =models.DateTimeField(verbose_name="last_login",auto_now=True)
    is_admin =models.BooleanField(default=False)
    is_active =models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',default=True)
    is_staff =models.BooleanField(default=False)
    is_superuser =models.BooleanField(default=False)

    class Types(models.TextChoices):
        ADMIN = "Admin","ADMIN"
        STAFF = "Staff","STAFF"

    default_type = Types.STAFF

    type = MultiSelectField(choices=Types.choices, default=[], null=True, blank=True)


    USERNAME_FIELD ='email'
    REQUIRED_FIELDS =['username']
    objects =UserManager()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.id:
            self.type = self.default_type
            # self.type.append(self.default_type)
        return super().save(*args, **kwargs)

    def has_perm(self,perm,obj=None):
        return self.is_admin
        
    def has_module_perms(self,app_lable):
        return True

class Admin(User):
    default_type = User.Types.ADMIN
    objects = AdminManager()

    class Meta:
        proxy = True

class Staff(User):
    default_type = User.Types.STAFF
    objects = StaffManager()

    class Meta:
        proxy = True
class Clinical(models.Model):
    # owner = models.ForeignKey('login.User',on_delete=models.CASCADE,related_name='posts',null=True,blank=True)
    name = models.CharField(max_length=80,null=True,blank=True)
    disease=models.CharField(max_length=60)
    minrank=models.IntegerField()
    maxrank=models.IntegerField()
    url =models.CharField(max_length=600)
    date_created = models.DateTimeField(auto_now_add=True,verbose_name='date_joined')

    def __str__(self) :
        return self.disease