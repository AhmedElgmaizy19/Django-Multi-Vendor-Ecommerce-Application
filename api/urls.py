from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from userauth import views as user_auth_views
from store import views as store_views
from customer import views as customer_views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
# router.register(r'user/user-profile', user_auth_views.userprofileView, basename='userprofile')

# router.register('cart', store_views.Cart, basename='cart')



urlpatterns = [
    # user authentication
    path('user/token/',user_auth_views.MyTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('user/token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
    path('user/register/',user_auth_views.RegisterView.as_view(),name='Register'),
    path('user/password-rest/<str:email>',user_auth_views.PasswordRestEmailVerify.as_view(),name='Password Rest'),
    path('user/password-change/',user_auth_views.PasswordChangeView.as_view(),name='Password change'),
    path('user/profile/', user_auth_views.UserPofileAPIView.as_view(), name='user-profile'),
    
    # store Endpoints
    
     path('products/', store_views.ProductListAPIView.as_view(),name='List Product'),
     path('products/<slug>/', store_views.ProductListAPIDetailView.as_view(),name='Product-Detail'),
    
    path('category/', store_views.CategoryListAPIView.as_view(),name='List Category'),
    
    path('cart/add-to-cart', store_views.CartAPIView.as_view(),name='cart'),
    path('cart/cart-list/', store_views.CartListView.as_view(),name='cart'),
    path('cart/cart-total/', store_views.CartTotalView.as_view(),name='cart'),
    path('cart/delete-cart/<int:item_id>', store_views.DeleteAPIView.as_view(),name='cart'),
    
    
    path('cart-order/',store_views.cartOrderAPIView.as_view(),name='cartOrder'),
    
    path('checkout/<str:order_id>', store_views.CheckOutApiView.as_view(), name='checkout'),
    
    path('coupon/', store_views.CouponApiView.as_view(), name='coupon'),
    
    # checkout stripe
    path('stripe-checkout/<str:order_id>', store_views.StripCheckoutAPIView.as_view(),name='stripe-checkout'),
    path('stripe-checkout/checkout-success/<str:order_id>', store_views.PaymentSuccsessAPIView.as_view(),name='stripe-checkout'),
    
    #review endpoint
    path('review/get-review/<product_id>', store_views.ProductReviewListAPIView.as_view(),name='Review'),
    path('review/create-review/', store_views.ProductReviewCreateAPIView.as_view(),name='create-review'),
    
    
    # search product endpoint
      path('search/', store_views.SerachProudctApiView.as_view(),name='serach-product'),
      
      
    # customers endpoints
      path('customer/get-orders/', customer_views.OrderAPIView.as_view(),name='odrders'),
      path('customer/order-detail/<order_oid>', customer_views.DetailOrderAPIview.as_view(),name='odrders'),
      path('customer/Profile/', customer_views.ProfileAPIView.as_view(),name='customer profile'),
      path('customer/wishlist/', customer_views.WishListAPIView.as_view(),name='customer wishlist'),
      path('customer/notifications/', customer_views.NotificationAPIView.as_view(),name='customer notifications'),
      path('customer/mark-notification/<notification_id>', customer_views.MarkNotificationAPIViewAsSeen.as_view(),name='customer notification'),
      
      
      
      
      
    
    
    
    
    

    
    
]

urlpatterns += router.urls