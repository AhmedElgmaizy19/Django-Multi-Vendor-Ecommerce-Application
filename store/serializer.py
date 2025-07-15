from rest_framework import serializers
from .models import *
from userauth.serializer import UserSerializer, UserProfileSerializer
from vendor.serializer import VendorSerializer 
from decimal import Decimal
from django.shortcuts import get_object_or_404

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = '__all__'


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'


#  proudct serializer for read and wrie

class ProductSerializer(serializers.ModelSerializer):
    gallery = GallerySerializer(many=True, read_only=True)
    specification = SpecificationSerializer(many=True, read_only=True)
    size = SizeSerializer(many=True, read_only=True)
    color = ColorSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    vendor =  VendorSerializer(read_only=True)
    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "image",
            "description",
            "category",
            "price",
            "old_price",
            "shipping_amount", 
            "stock_quantity",
            "in_stock",
            "status",  
            "featured",
            "views",
            "rating",
            "vendor",
            "pid",
            "slug",
            "date",
            "gallery",
            "specification",
            "size",
            "color",
            "product_rating",
            "rating_count",
        ]
        
    def __init__(self, *args, **kwargs):
        super(ProductSerializer, self).__init__(*args, **kwargs)
        
        request = self.context.get('request')
        if request and request.method == 'POST':
            # عند الإنشاء، نزيل الـ nested serializers
            self.fields.pop('gallery', None)
            self.fields.pop('specifications', None)
            self.fields.pop('sizes', None)
            self.fields.pop('colors', None)


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "title",
            "image",
            "description",
            "category",
            "price",
            "old_price",
            "shipping_amount",
            "stock_quantity",
            "in_stock",
            "status",
            "featured",
            "vendor",
        ]



# Define a serializer for the ProductFaq model
class ProductFaqSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductFAQ
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductFaqSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.fields.pop('product', None)


# Product FAQ Create Serializer
class ProductFaqCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFAQ
        fields = ['product', 'user', 'email', 'question', 'answer']



# Define a serializer for the CartOrderItem model
class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(CartSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.fields.pop('product', None)


# Cart Create Serializer
class CartCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    country = serializers.CharField(write_only=True)
    cart_id = serializers.UUIDField(read_only=True) 
    class Meta:
        model = Cart
        fields = ['product_id','cart_id' , 'price', 'quantity', 'shipping_amount',
                  'color', 'size', 'country']

    def validate(self, attrs):
        try:
            product = Product.objects.get(id=attrs['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")

        attrs['product'] = product

        tax = Tax.objects.filter(country=attrs['country']).first()
        attrs['tax_rate'] = Decimal(tax.rate / 100) if tax else Decimal('0')

        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        cart_id = self.context['request'].data.get('cart_id', None)
        DEFAULT_SHIPPING = Decimal('5.00')
        shipping_amount = validated_data['shipping_amount'] =  5.00
        if not user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated.")

        if not cart_id:
            cart_id = uuid.uuid4()

        product = validated_data.pop('product')
        tax_rate = validated_data.pop('tax_rate')
        shipping_amount = Decimal(validated_data.get('shipping_amount', DEFAULT_SHIPPING))
        price = Decimal(validated_data['price'])
        quantity = int(validated_data['quantity'])
        color = validated_data['color']
        size = validated_data['size']
        country = validated_data['country']

        # نجيب الكارت الموجود بنفس التفاصيل
        try:
            cart = Cart.objects.get(
                cart_id=cart_id,
                user=user,
                product=product,
                color=color,
                size=size
            )
            # لو نفس الكمية خلاص، ما تعملش أي حاجة أو رجعه
            if cart.quantity == quantity:
                return cart

            # لو الكمية مختلفة، نحدثه
            sub_total = price * quantity
            shipping_total = shipping_amount * quantity
            service_fee = shipping_total * Decimal('0.05')
            tax_fee = sub_total * tax_rate
            total = sub_total + shipping_total + service_fee + tax_fee

            cart.price = price
            cart.quantity = quantity
            cart.sub_total = sub_total
            cart.shipping_amount = shipping_total
            cart.service_fee = service_fee
            cart.tax_fee = tax_fee
            cart.country = country
            cart.total = total
            cart.save()

            return cart

        except Cart.DoesNotExist:
            # مفيش كارت بنفس البيانات، نعمل واحد جديد
            sub_total = price * quantity
            shipping_total = shipping_amount * quantity
            service_fee = shipping_total * Decimal('0.05')
            tax_fee = sub_total * tax_rate
            total = sub_total + shipping_total + service_fee + tax_fee

            cart = Cart.objects.create(
                cart_id=cart_id,
                user=user,
                product=product,
                color=color,
                size=size,
                price=price,
                quantity=quantity,
                sub_total=sub_total,
                shipping_amount=shipping_total,
                service_fee=service_fee,
                tax_fee=tax_fee,
                country=country,
                total=total
            )
            return cart


  

# Define a serializer for the CartOrderItem model
class CartOrderItemSerializer(serializers.ModelSerializer):
    Product = ProductSerializer(read_only=True)

    class Meta:
        model = CartOrderItem
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(CartOrderItemSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.fields.pop('product', None)
            
            
            
class CartOrderItemCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CartOrderItem
        fields = '__all__'
    
    


# Define a serializer for the CartOrder model
class CartOrderSerializer(serializers.ModelSerializer):
    order_item = CartOrderItemSerializer(many=True, read_only=True)
    date = serializers.SerializerMethodField()

    class Meta:
        model = CartOrder
        fields = '__all__'

    
    def get_date(self, obj):
        return obj.date.date().isoformat()  # أو obj.date.strftime('%Y-%m-%d'
    def __init__(self, *args, **kwargs):
        super(CartOrderSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.fields.pop('order_item', None)


# CartOrder Create Serializer
class CartOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartOrder
        fields = '__all__'
        read_only_fields = ['buyer','cart_id']
    
    
    def create(self, validated_data):
        user = self.context['request'].user
        cart_id = self.context['request'].data.get('cart_id', None)

        if not user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated.")
        
        validated_data['buyer'] = user
       
        cart_order = CartOrder.objects.create(**validated_data)
        
        # إذا كان cart_id موجودًا، نربطه بالطلب
        cart_item = Cart.objects.filter( user=user , cart_id=cart_id,)
        
        if not cart_item.exists():
                raise serializers.ValidationError("No cart items found for this user and cart_id.")
        
        total_shipping = Decimal('0.0')
        total_tax = Decimal('0.0')
        total_service_fee = Decimal('0.0')
        total_sub_total = Decimal('0.0')
        initial_total = Decimal('0.0')
        total_total = Decimal('0.0')
        
        if cart_item:
            for item in cart_item:
                CartOrderItem.objects.create(
                   order=cart_order,
                    Product=item.product,
                    quantity=item.quantity,
                    sub_total=item.sub_total,
                    shipping_amount=item.shipping_amount,
                    service_fee=item.service_fee,
                    tax_fee=item.tax_fee,
                    total=item.total,
                    initial_total=item.total,
                    vendor = item.product.vendor
                )
            
                total_shipping += item.shipping_amount
                total_tax += item.tax_fee
                total_service_fee +=item.service_fee
                total_sub_total += item.sub_total
                initial_total += item.total
                total_total += item.total
                
                cart_order.vendor.add(item.product.vendor)
        
        cart_order.shipping_amount = total_shipping
        cart_order.tax_fee = total_tax
        cart_order.service_fee = total_service_fee
        cart_order.sub_total = total_sub_total
        cart_order.initial_total = initial_total
        cart_order.total = total_total
        cart_order.save()
        return cart_order


        
       

# Define a serializer for the Review model
class ReviewSerializer(serializers.ModelSerializer):
    # product = ProductSerializer(read_only=True)
    profile = UserProfileSerializer(read_only=True)
    # user = UserSerializer(read_only=True) 
    date = serializers.SerializerMethodField()
    class Meta:
        
        model = Review
        fields = ['id', 'profile', 'product', 'rating', 'review', 'date']

    def get_date(self, obj):
        return obj.date.date().isoformat()  # أو obj.date.strftime('%Y-%m-%d'
    
    def __init__(self, *args, **kwargs):
        super(ReviewSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.fields.pop('product', None)
            self.fields.pop('profile', None)


# Review Create Serializer
class ReviewCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Review
        fields = ["product_id", "user", "rating", "review","date"]

    
    def create(self, validated_data):
        user = self.context['request'].user
        # product_id = self.context['request'].data.get('product_id', None)
        
        if not user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated.")
        
        product_id = validated_data['product_id']
        rating  = validated_data['rating']
        review  = validated_data['review']
        product = get_object_or_404(Product, id=product_id)
        
        review = Review.objects.create(
            user=user,
            product=product,
            rating= rating ,
            review =review ,
            active=True,
        )
        
        return review


# Define a serializer for the Wishlist model
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = WishList
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(WishlistSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.fields.pop('product', None)


# Wishlist Create Serializer
class WishlistCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)

    class Meta: 
        model = WishList
        fields = ['id', 'user', 'product', 'product_id']
        read_only_fields = ['id', 'user', 'product']
        
    def create(self, validated_data):
        user = self.context['request'].user
        product_id = validated_data['product_id']
        product = get_object_or_404(Product, id=product_id)

        # Use get_or_create for atomicity and to easily determine if the item was created.
        wishlist_item, created = WishList.objects.get_or_create(
            user=user, product=product
        )
        
        # Set a flag on the serializer instance to indicate the action performed.
        # The view can use this flag to return a custom response message.
        self.created = created
        if not created:
            # If the item already existed (was not created), delete it.
            wishlist_item.delete()
            
        return wishlist_item


# Define a serializer for the Coupon model
class CouponSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    user_by = UserSerializer(read_only=True,many=True)
    class Meta:
        model = Coupon
        fields = ['vendor','user_by','code','discount','active']
    
    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated.")

        order_oid = self.context['request'].data.get('order_oid', None)
        if not order_oid:
            raise serializers.ValidationError("Order OID is required.")

        try:
            orders = CartOrder.objects.get(oid=order_oid, buyer=user)
        except CartOrder.DoesNotExist:
            raise serializers.ValidationError("Order not found or does not belong to the user.")

        coupon = Coupon.objects.filter(code=validated_data['code']).first()
        if not coupon:
            raise serializers.ValidationError("Coupon does not exist.")

        order_items = CartOrderItem.objects.filter(order=orders)
        if not order_items.exists():
            raise serializers.ValidationError("Order Item Does Not Exist.")

        activated = False
        for order_item in order_items:
            # تأكد إن المنتج تابع لنفس البائع اللي عمل الكوبون
            if order_item.Product.vendor != coupon.vendor:
                continue

            # تجاهل لو الكوبون متطبق على العنصر ده بالفعل
            if order_item.coupon.filter(id=coupon.id).exists():
                continue

            # احسب الخصم لكن تأكد إنه ما يزيدش عن السعر
            discount = order_item.total * coupon.discount / 100
            discount = min(discount, order_item.total)  # لا يتجاوز السعر

            # طبق الخصم على العنصر
            order_item.total = max(order_item.total - discount, 0)
            order_item.sub_total = max(order_item.sub_total- discount, 0)
            order_item.saved += discount
            order_item.coupon.add(coupon)
            order_item.save()

            # طبق الخصم على الطلب كله
            orders.total = max(orders.total - discount, 0)
            orders.sub_total = max(orders.sub_total - discount, 0)
            orders.saved += discount

            activated = True

        orders.save()

        if activated:
            coupon.user_by.add(user)
            return coupon
        else:
            raise serializers.ValidationError("Coupon is already applied or not applicable.")



# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'