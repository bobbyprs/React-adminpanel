from django.contrib import admin
from .models import Admin, Clinical, Staff, User
from django.contrib.auth.admin import UserAdmin
import pprint
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session


class UsersAdmin(UserAdmin):
    list_display = ('username','email','date_joined','last_login','is_active','is_staff')
    search_fields =('email','username')
    readonly_fields =('id','date_joined','last_login','password')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ( 'username','email','phone_number','is_active')}
        ),
        
    )

    filter_horizontal =()
    list_filter =('email','username')
    fieldsets =()

# class SessionAdmin(admin.ModelAdmin):
#     def _session_data(self, obj):
#         return pprint.pformat(obj.get_decoded()).replace('\n', '<br>\n')
#     _session_data.allow_tags=True
#     list_display = ['session_key', '_session_data', 'expire_date']
#     readonly_fields = ['_session_data']
#     exclude = ['session_data']

# admin.site.register(Session, SessionAdmin)
# Register your models here.
admin.site.register(User)
admin.site.register(Staff)
admin.site.register(Admin)
admin.site.register(Clinical)