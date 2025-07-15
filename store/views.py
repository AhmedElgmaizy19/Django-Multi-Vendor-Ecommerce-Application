from django.shortcuts import get_object_or_404
from rest_framework import generics , status 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import stripe.error
from .serializer import *
from .models import (
    Product , Category, Cart, CartOrder, 
     CartOrderItem,
     Review,Coupon ,
)
from rest_framework.exceptions import NotFound
from   utils.utilis import Utilis
from utils import notification
from utils.base_url import base_url
from decouple import config
import stripe
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from backend_prj import settings


# stripe key
stripe.api_key = config('STRIPE_KEY')
# Create your views here.


# view all product endpoint
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.select_related('category', 'vendor')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
# view spacefic product endpoint
class ProductListAPIDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('category', 'vendor')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        slug = self.kwargs['slug']
        return Product.objects.get(slug=slug)


# view all category endpoint
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    


# add to cart endpoint

class CartAPIView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CartCreateSerializer
        return CartSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the cart instance
        cart = serializer.save(user=request.user)

        # Return response with cart_id
        return Response({
            'message': 'Item added to cart',
            'cart_id': str(cart.cart_id)  # مهم يكون str لأنه UUID
        }, status=status.HTTP_201_CREATED)


# list cart endpoint
class CartListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    
    def get_queryset(self):
        cart_id = self.request.data.get('cart_id', None)
        user= self.request.user
        
        if cart_id:
            return Cart.objects.filter(user=user,cart_id=cart_id).select_related('user', 'product')
        else:
           return Cart.objects.filter(user=user).select_related('user', 'product') 
    

# get totl of prices in cart endpoint
class CartTotalView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
   
    
    
    def get_queryset(self):
        cart_id = self.request.data.get('cart_id', None)
        user = self.request.user
        if cart_id:
            return Cart.objects.filter(user=user, cart_id=cart_id).select_related('user', 'product')
        else:
            return Cart.objects.filter(user=user).select_related('user', 'product')
    
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({'message': 'Cart is empty'}, status=status.HTTP_404_NOT_FOUND)
        
        
        total_shipping = 0.0
        total_tax = 0.0
        total_service_fee = 0.0
        total_sub_total = 0.0
        total_total = 0.00
        
        
        for cart_item in queryset:
            total_shipping += float(Utilis.calculate_shipping(cart_item))
            total_tax += float(Utilis.calculate_total_tax(cart_item))
            total_service_fee +=  float(Utilis.calculate_total_service_fee(cart_item))
            total_sub_total +=  float(Utilis.calculate_total_sub_total(cart_item))
            total_total +=  float(Utilis.calculate_total(cart_item))
            
            
        data = {
                'shipping':total_shipping,
                'tax':total_tax,
                'service_fee':total_service_fee,
                'sub_total':total_sub_total,
                'total':total_total,
            } 
        
        
        return Response({
            'message': 'Cart retrieved successfully',
            'totals': data
        }, status=status.HTTP_200_OK)
        

# delete item in cart endpoint
class DeleteAPIView(generics.DestroyAPIView):
    queryset = Cart.objects.select_related('user', 'product')
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    
    def get_object(self):
        user = self.request.user
        cart_id = self.request.data.get('cart_id',None)
        item_id  =self.kwargs['item_id']
        if not cart_id:
            raise NotFound("Cart ID is required")
        
        try:
          cart_item = Cart.objects.get(id=item_id,user=user,cart_id=cart_id)  
        except Cart.DoesNotExist:
             raise NotFound('Cart item not found')
        

        return cart_item


# create cartorder endpoint
class cartOrderAPIView(generics.CreateAPIView):
    queryset = CartOrder.objects.all()
    serializer_class = CartOrderCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        cart_order = serializer.save()
        data = CartOrderCreateSerializer(cart_order).data
        return Response(
            {
                "order_oid": cart_order.oid,  # assuming you have an oid field
                "cart_order": data
            },
            status=status.HTTP_201_CREATED
        )
    
# view order checkout endpoint
class CheckOutApiView(generics.RetrieveAPIView):
    serializer_class = CartOrderSerializer
    lookup_field = 'oid'
    permission_classes = [IsAuthenticated]
    queryset = CartOrder.objects.select_related('buyer').prefetch_related('vendor')
    def get_object(self):
            order_oid = self.kwargs['order_id']
            order = get_object_or_404(
                CartOrder.objects.select_related('buyer').prefetch_related('vendor'),
                oid=order_oid
            )
            return order
               
# create coupon endpoint
class CouponApiView(generics.CreateAPIView):
    serializer_class = CouponSerializer
    queryset = Coupon.objects.select_related('vendor').prefetch_related('user_by')
    permission_classes = [IsAuthenticated]
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        cart_order = serializer.save()
        data = CouponSerializer(cart_order).data
        return Response(
            {
                "message": 'cupon is activated',  # assuming you have an oid field
                "data": data
            },
            status=status.HTTP_201_CREATED
        )
    
    
class StripCheckoutAPIView(generics.CreateAPIView):
    serializer_class = CartOrderCreateSerializer
    permission_classes = [IsAuthenticated]
    
    


    def create(self,*args, **kwargs):
        order_oid = self.kwargs['order_id']
        order = get_object_or_404(CartOrder.objects.select_related('buyer').prefetch_related('vendor'),oid=order_oid)
        
        if not order:
            return Response({'message':"order not found"},status=status.HTTP_404_NOT_FOUND)
        try:
            print("DB payment_status:", order.payment_status)
            print("Expected:", order.PaymentsType.PENDING)
            checkout_session =  stripe.checkout.Session.create(
                customer_email=order.email,
                payment_method_types = ['card'],
                line_items=[
                    {
                        'price_data':{
                            'currency':'usd',
                            'product_data':{
                                'name': order.full_name
                            },
                            'unit_amount':int(order.total * 100)
                        },
                        'quantity':1,
                    },
                ],
                
                mode='payment',
                success_url = f'http://localhost:5173/payment-sucsess/{order.oid}?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url= f'http://localhost:5173/payment-failed/{order.oid}?session_id={{CHECKOUT_SESSION_ID}}'
            )
            
            order.stripe_session_id = checkout_session.id
            order.save()
            return Response({'checkout_url': checkout_session.url}, status=status.HTTP_200_OK)
        except stripe.error.StripeErorr as e:
            return Response({'error': f'something went wrong please try again: {str(e)}'})
            
        

class PaymentSuccsessAPIView(generics.CreateAPIView):
    serializer_class = CartOrderCreateSerializer
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        paylod = request.data
        
        order_oid = paylod['order_oid']
        session_id = paylod['session_id']
        
        order =  get_object_or_404(CartOrder.objects.select_related('buyer').prefetch_related('vendor'),oid=order_oid)
        order_item = CartOrderItem.objects.filter(order=order)
       
        if session_id != 'null':
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
               
                if order.payment_status == order.PaymentsType.PENDING:
                    order.payment_status = order.PaymentsType.PAID
                    order.save()
                    # send notification
                    if order.buyer !=None:
                       notification.send_notification(user=order.buyer, order=order)
                    
                    # send notification to vendor
                    for item in order_item:
                        notification.send_notification(vendor=item.vendor, order_item=item)
                        # send Email to vendor
                        # context = {
                        #     'order': order,
                        #     'order_item': item
                        # }
                        # subject = 'new order detail'
                        # text_body = render_to_string('email/vendor_order_information.txt', context)
                        # html_body = render_to_string('email/vendor_order_information.html', context)
                        # message = EmailMultiAlternatives(
                        #     subject=subject,
                        #     from_email=settings.DEFAULT_FROM_EMAIL,
                        #     to=[item.vendor.user.email],
                        #     body=text_body,
                        # )
                        # message.attach_alternative(html_body, 'text/html')
                        # message.send()

                                        
                    # send Email to buyer
                    # context = {
                    #     'order': order,
                    #     'order_items': order_item
                    # }
                    # subject = 'order placed successfully'
                    
                    # text_body = render_to_string('email/customer_order_information.txt', context)
                    # html_body = render_to_string('email/customer_order_information.html', context)
                    # message = EmailMultiAlternatives(
                    #     subject=subject,
                    #     from_email=settings.DEFAULT_FROM_EMAIL,
                    #     to=[order.email],
                    #     body=text_body,
                    # )
                    
                    # message.attach_alternative(html_body, 'text/html')
                    # message.send()
                    
                    return Response({'message': 'payment successful'})
                else:
                    return Response({'message': 'already paid'}) 

            elif session.payment_status == 'unpaid':
                order.payment_status = order.PaymentsType.PENDING
                order.save()
                return Response({'message': 'your Invoice is UnPaid'})

            elif session.payment_status == 'no_payment_required':
                order.payment_status = order.PaymentsType.PROCESSING
                order.save()
                return Response({'message': 'No payment required'})

            else:
                order.payment_status = order.PaymentsType.CANCELED 
                order.save()
                return Response({'message': 'An Error Occurred. Try Again'}) 
        else:
            return Response({'message': 'Invalid Session '})
        
        
class ProductReviewListAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        return Review.objects.filter(product=product).select_related('user', 'product')
    

class ProductReviewCreateAPIView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]
    
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Save the review instance
        review = serializer.save()
        
        # Return response with review data
        return Response({
            'message': 'Review created successfully',
            'review': ReviewSerializer(review).data
        }, status=status.HTTP_201_CREATED)
        


class SerachProudctApiView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        query = self.request.GET.get('query')
        if not query:
            return Product.objects.none()
        return Product.objects.filter(status=Product.ProductType.PUBLISHED, title__icontains=query)
    
        
    

    