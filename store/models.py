from django.db import models
from vendor.models import Vendor
from userauth.models import User,UserProfile
from shortuuid.django_fields import ShortUUIDField
from django.utils.text import slugify
import uuid
# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=50)
    image = models.FileField(upload_to='category',blank=True,null=True,default='category.jpg')
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['title']
        
    

    def __str__(self):
        return str(self.title)

   
   
class Product(models.Model):
    
    class ProductType(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        DISABLED = 'disabled', 'Disabled'
        IN_REVIEW = 'in_review', 'In Review'
        PUBLISHED = 'published', 'Published'
        
    title = models.CharField(max_length=50)
    image = models.FileField(upload_to='products',blank=True,null=True,default='product.jpg')
    description = models.TextField(null=True,blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True , null=True)
    price = models.DecimalField( max_digits=12, decimal_places=2,default=0)
    old_price = models.DecimalField( max_digits=12, decimal_places=2,default=0)
    stock_quantity = models.PositiveIntegerField(default=1)
    in_stock = models.BooleanField(default=True)
    shipping_amount = models.DecimalField( max_digits=12, decimal_places=2,default=0)
    status = models.CharField(max_length=14,choices=ProductType.choices,default=ProductType.PUBLISHED)
    featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=1)
    rating = models.PositiveIntegerField(default=1)
    vendor = models.ForeignKey(Vendor,  on_delete=models.CASCADE)
    pid = ShortUUIDField(
        length=10,
        alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        max_length=12,
        unique=True,
        editable=False
    )
    
    slug = models.SlugField(unique=True,max_length=255)
    date =  models.DateTimeField(auto_now_add=True)
    
    

    def __str__(self):
        return self.title

    
    def product_rating(self):
        product_rating = Review.objects.filter(product=self, active=True).aggregate(models.Avg('rating'))
        return product_rating['rating__avg'] if product_rating['rating__avg'] else 0
    
    def rating_count(self):
        return Review.objects.filter(product=self,active=True).count()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs)  # Save first to get an ID
        self.rating = self.product_rating()
        super(Product, self).save(update_fields=['rating']) 
        
    
    def gallery(self):
        return Gallery.objects.filter(product=self)
    
    def color(self):
        return  Color.objects.filter(product=self)
    
    def specification(self):
        return Specification.objects.filter(product=self)
    
    def size(self):
        return  Size.objects.filter(product=self)
    
      
   
    
class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.FileField(upload_to='gallery', blank=True, null=True, default='gallery.jpg')
    active = models.BooleanField(default=True)
    gid = ShortUUIDField(
        length=10,
        alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        max_length=12,
        unique=True,
        editable=False
    )

    def __str__(self):
        return self.product.title
    
    class Meta:
        verbose_name_plural = 'product images'


class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,)
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Size(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,)
    name= models.CharField(max_length=255)
    price = models.DecimalField( max_digits=12, decimal_places=2,default=0)
 
    def __str__(self):
        return self.name


class Color(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,)
    name= models.CharField(max_length=255)
    color_code = models.CharField(max_length=255)

    def __str__(self):
        return self.name



class Cart(models.Model):
    product = models.ForeignKey(Product,verbose_name='product', on_delete=models.CASCADE,)
    user = models.ForeignKey(User, verbose_name=("user"), on_delete=models.CASCADE)
    price = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    sub_total = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField( max_digits=12, decimal_places=2, default=12.00)
    service_fee = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    tax_fee = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    country = models.CharField(max_length=20,blank=True,null=True)
    size = models.CharField(max_length=20,blank=True,null=True)
    color = models.CharField(max_length=20,blank=True,null=True)
    cart_id =models.UUIDField(
        default=uuid.uuid4,
        editable=False,
       db_index=True,
        verbose_name='Cart ID'
    )
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.cart_id}- {self.product.title} - {self.user.full_name}'
    
class CartOrder(models.Model):
    
    class PaymentsType(models.TextChoices):
        PAID = 'paid', 'Paid'
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        CANCELED = 'canceled', 'Canceled'
    
    
    class OrderType(models.TextChoices):
        PENDING = 'pending', 'Pending'
        FULFILLED = 'fulfilled', 'Fulfilled'
        CANCELED = 'canceled', 'Canceled'
        
    
    vendor = models.ManyToManyField(Vendor, blank=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    sub_total = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    service_fee = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    tax_fee = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20,choices=PaymentsType,default=PaymentsType.PENDING)
    order_status = models.CharField(max_length=20,choices=OrderType,default=OrderType.PENDING)
    
    # coupons
    initial_total = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    saved = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    
    # Bio data
    full_name =  models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(max_length=254,null=True,blank=True)
    mobile =  models.CharField(max_length=50,null=True,blank=True)
    
    # Shipping address
    address = models.CharField(max_length=100,null=True,blank=True)
    city= models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    stripe_session_id = models.CharField(max_length=150,null=True,blank=True)
    oid = ShortUUIDField(
        length=10,
        alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        unique=True,
        editable=False
    )
    date = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f'{self.oid} - {self.buyer.full_name}' 
    

class CartOrderItem(models.Model):
    order = models.ForeignKey( CartOrder,related_name='order_item' ,on_delete=models.CASCADE)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=0)
    sub_total = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    service_fee = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    tax_fee = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    country = models.CharField(max_length=20,blank=True,null=True)
    
    # coupons
    coupon = models.ManyToManyField("store.Coupon", blank=True)
    initial_total = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    saved = models.DecimalField( max_digits=12, decimal_places=2, default=0)
    
    oid = ShortUUIDField(
        length=10,
        alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        unique=True,
        editable=False
    )
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.oid}' 


class ProductFAQ(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, null=True, blank=True)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Question by {self.user.username} on {self.product.title}'
    class Meta:
        verbose_name_plural = 'Product FAQs'
        ordering = ['-date']    
        
    
    
class Review(models.Model):
    
    Rating = (
        (1,'1 star'),
        (2,'2 star'),
        (3,'3 star'),
        (4,'4 star'),
        (5,'5 star'),
        

    )
        
        
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE )
    rating = models.PositiveIntegerField(default=0 , choices=Rating)
    review = models.TextField(blank=True, null=True)
    replay = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Review by {self.user.username} on {self.product.title}'
    
    class Meta:
        verbose_name_plural = 'Product Reviews'
        ordering = ['-date']
        
    def profile(self):
        return UserProfile.objects.get(user = self.user)
    
    
class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.product.title}'
    
    class Meta:
        verbose_name_plural = 'Wish Lists'
        ordering = ['-date']
        

class Notifications(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL,null=True,blank=True)
    order = models.ForeignKey(CartOrder,on_delete=models.SET_NULL,null=True,blank=True)
    order_item = models.ForeignKey(CartOrderItem,on_delete=models.SET_NULL,null=True,blank=True)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        if self.order:
            return self.order.oid
        return f"Notifiaction- {self.pk}"
    

class Coupon(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    user_by = models.ManyToManyField(User, blank=True)
    code = models.CharField(max_length=250)
    discount = models.IntegerField(default=1)
    active= models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.code
    
    
class Tax(models.Model):
    country = models.CharField(max_length=50)
    rate = models.IntegerField(default=5 , help_text='number added here are in percintage')
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.country

 