from django.contrib import admin
from .models import Vendor

# Register your models here.

class VendorAdmin(admin.ModelAdmin):
    list_display = ('name','user', 'mobile', 'active', 'date')
    list_filter = ('active', 'date')
    search_fields = ('name', 'mobile')

    # def has_add_permission(self, request):
    #     return request.user.is_superuser
    
    # def has_change_permission(self, request, obj=None):
    #     return request.user.is_superuser
    
    # def has_delete_permission(self, request, obj=None):
    #     return request.user.is_superuser
    
    
admin.site.register(Vendor, VendorAdmin)