from django.contrib import admin
from .models import User, UserProfile

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','full_name','email','phone')
    search_fields = ('username','email','phone')
    list_filter = ('is_staff', 'is_active')
    ordering = ('-date_joined',)

admin.site.register(User ,UserAdmin)

class  UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name','gender', 'country')
    search_fields = ('full_name' ,'country')
    ordering = ('-date',)
    list_filter = ('country',)
    readonly_fields = ['pid']



admin.site.register(UserProfile, UserProfileAdmin)