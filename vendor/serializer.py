from rest_framework import serializers
from .models import Vendor
from userauth.serializer import UserSerializer

class VendorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Vendor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VendorSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.fields.pop('user', None)


# Vendor Create Serializer
class VendorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['user', 'image', 'name', 'description', 'mobile', 'active']