from django.contrib import admin
from .models import *
# Register your models here.

class GalleryInline(admin.TabularInline):
    model = Gallery
    extra= 1
    

class SpecificationInline(admin.TabularInline):
    model = Specification
    extra= 1
    


class SizeInline(admin.TabularInline):
    model = Size
    extra= 1
    
    
class ColorInline(admin.TabularInline):
    model = Color
    extra= 1


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title' ,'active', 'slug',)
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title',   'category', 'price', 'old_price', 'stock_quantity', 'shipping_amount', 'status', 'featured',  'date')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'category', 'vendor')
    search_fields = ('title', 'description')
    list_editable = ('featured',)
    ordering = ('-date',)
    inlines = [GalleryInline, SpecificationInline, SizeInline, ColorInline]
    readonly_fields = ['pid']
admin.site.register(Product, ProductAdmin)


class CartOrderAdmin(admin.ModelAdmin):
    list_display = ('oid',   'payment_status', 'total',)
   
   
admin.site.register(CartOrder,CartOrderAdmin)





admin.site.register(Cart)
# admin.site.register(CartOrder)
admin.site.register(CartOrderItem)
admin.site.register([ProductFAQ,Review,WishList,Notifications,Coupon,Tax])
