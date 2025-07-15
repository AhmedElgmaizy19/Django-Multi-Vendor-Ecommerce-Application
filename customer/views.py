from django.shortcuts import get_object_or_404
from rest_framework import generics , status 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import stripe.error
from  store.serializer import *
from store.models import (
    Product , Category, Cart, CartOrder, 
     CartOrderItem, ProductFAQ, 
     Review, WishList, Coupon ,
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
from userauth.models import UserProfile
from userauth.serializer import UserProfileSerializer


# Create your views here.
class OrderAPIView(generics.ListAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return CartOrder.objects.filter(buyer=user, payment_status=CartOrder.PaymentsType.PAID).select_related('buyer').prefetch_related('vendor')
        else:
            return CartOrder.objects.none()
    

class DetailOrderAPIview(generics.RetrieveAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        order_oid = self.kwargs['order_oid']
        qs = CartOrder.objects.select_related('buyer').prefetch_related('vendor')
        if user.is_authenticated:
            return qs.get(buyer=user,oid=order_oid,payment_status=CartOrder.PaymentsType.PAID)
        else:
            return CartOrder.objects.none()
        
        
class ProfileAPIView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    
    def get_object(self):
        user = self.request.user
        user_profile  = get_object_or_404(UserProfile.objects.select_related('user'),  user=user)
        return user_profile
    
    

class WishListAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WishlistCreateSerializer
        return  WishlistSerializer
    
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return WishList.objects.filter(user=user).select_related('product')
        else:
            return WishList.objects.none()
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # The user is passed via the context, so no need to pass it to save().
        serializer.save()

        # The serializer's create method sets a `created` attribute.
        if getattr(serializer, 'created', True):
            return Response({"message": "Item added to wishlist successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Item removed from wishlist successfully."}, status=status.HTTP_200_OK)
    
    

class NotificationAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Notifications.objects.filter(user=user,seen=False).select_related('user','vendor','order','order_item')
        else:
            return Notifications.objects.none()
    
    # def get(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    


class MarkNotificationAPIViewAsSeen(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        notification_id = self.kwargs['notification_id']
        if user.is_authenticated:
            return Notifications.objects.get(user=user, id=notification_id)
        else:
            raise NotFound("Notification not found.")
    
    def get(self, request, *args, **kwargs):
        notification_obj = self.get_object()
        if notification_obj.seen:
            return Response({"message": "Notification already marked as seen."}, status=status.HTTP_200_OK)
        # Mark the notification as seen
        notification_obj.seen = True
        notification_obj.save()
        return Response({"message": "Notification marked as seen."}, status=status.HTTP_200_OK)
    

    
