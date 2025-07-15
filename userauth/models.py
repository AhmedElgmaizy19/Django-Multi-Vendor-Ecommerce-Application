from django.db import models
from django.contrib.auth.models import AbstractUser
from shortuuid.django_fields import ShortUUIDField

# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=25, unique=True)
    otp = models.CharField(max_length=25, null=True,blank=True)
    reset_token  = models.CharField(max_length=255, null=True, blank=True)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super(User, self).save(*args, **kwargs)
        




     
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    full_name = models.CharField(max_length=50,null=True, blank=True)
    profile_picture = models.FileField(upload_to='images/', null=True, blank=True)
    gender = models.CharField(max_length=10,)
    address = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=50, null=True,  blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    pid = ShortUUIDField(
        length=10,
        alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        unique=True,
        editable=False
    )
    def __str__(self):
        if self.full_name:
           return self.user.full_name
        else:
            return self.user.username
        
    def save(self, *args, **kwargs):
        if  not self.full_name:
            self.full_name = self.user.full_name
        super(UserProfile, self).save(*args, **kwargs)
        
