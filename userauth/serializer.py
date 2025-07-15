from rest_framework import serializers
from .models import User , UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

# login 
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['full_name'] = getattr(user, 'full_name', '') # # getattr is used to safely get an attribute. # If the attribute doesn't exist, it returns the default value instead of raising an error.
        token['email'] = getattr(user, 'email', '')
        token['phone'] = getattr(user, 'phone', '')
        token['username'] = getattr(user, 'username', '') 
        
        vendor_id = getattr(getattr(user, 'vendor', None), 'id', 0)
        token['vendor_id'] = vendor_id

        return token
            
   

        # token['full_name'] = user.full_name 
        # token['email'] = user.email 
        # token[' phone'] = user. phone 
        
        # try:
        #     token['vendor_id'] = user.vendor.id
        # except:
        #     token['vendor_id'] = 0
        


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'password1', 'password2']

    def validate(self, attrs):
        if attrs.get('password1') != attrs.get('password2'):
            raise serializers.ValidationError({'password': "Passwords don't match"})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('Phone already exists')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password1', None) # return value and remove it from  dict
        validated_data.pop('password2', None)
        user = User(
            full_name=validated_data.get('full_name', ''),
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            username=validated_data.get('email', '').split('@')[0] if validated_data.get('email') else ''
        )
        if password:
            user.set_password(password)
        user.save()
        return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','phone','email','full_name']




class PasswordChangeSerializer(serializers.Serializer):
    otp = serializers.CharField()
    uidb64 = serializers.CharField()
    reset_token = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)



# user profile
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model =UserProfile
        fields = '__all__'
        
    

    
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['user'] = UserSerializer(instance.user).data
    #     return response  =====> equal to this  user = UserSerializer(read_only=True) same result