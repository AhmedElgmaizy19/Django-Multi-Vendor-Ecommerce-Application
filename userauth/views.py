from .models import User , UserProfile
from .serializer import MyTokenObtainPairSerializer ,RegisterSerializer , UserSerializer , UserProfileSerializer , PasswordChangeSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics , viewsets
from rest_framework.permissions import IsAuthenticated , AllowAny
from utils.utilis import Utilis
from utils.base_url import base_url
from rest_framework.views import Response ,status

# Create your views here.

# login endpoint
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
# register endpoint  
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    
class PasswordRestEmailVerify(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    
    def get_object(self):
        email = self.kwargs['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise generics.exceptions.NotFound("User with this email does not exist.")
        
        if user:
            user.otp = Utilis.genrate_otp()
            user.save(update_fields=['otp'])
            
            uidb64 = user.pk
 
            otp = user.otp
            link = f'{base_url}create-new-password?otp={otp}&uidb64={uidb64}'
            print(f'link === {link}')
            
        return user
    
    

class PasswordChangeView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordChangeSerializer  

    def create(self, request, *args, **kwargs):
        payload = request.data

        otp = payload.get('otp')
        uidb64 = payload.get('uidb64')
        reset_token  = payload.get('reset_token')
        password = payload.get('password')

        try:
            user = User.objects.get(id=uidb64, otp=otp)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid OTP or user.'}, status=status.HTTP_400_BAD_REQUEST)

        # Optionally check reset_token here

        user.set_password(password)
        user.otp = ''
        user.reset_token  = ''
        user.save()

        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)



class UserPofileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user.userprofile

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
