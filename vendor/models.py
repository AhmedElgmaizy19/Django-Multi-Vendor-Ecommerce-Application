from django.db import models
from userauth.models import User
from django.utils.text import slugify

# Create your models here.

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50,help_text='shop name')
    image = models.FileField(upload_to='vendor', default='vendoor.jpg',blank=True, null=True)
    description = models.TextField(null=True,blank=True)
    mobile = models.CharField(max_length=15,help_text='shop mobile number', blank=True, null=True , unique=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True,max_length=500)
    
    class Meta:
        verbose_name_plural = 'Vendors'
        ordering = ['-date']
        
        
    def __str__(self):
        if self.name:
            return str(self.name)
        
    
    
    def save(self, *args, **kwargs):
        if self.slug == '' or self.slug == None:
            self.slug =slugify(self.name)
        
        super(Vendor,self).save(*args, **kwargs)