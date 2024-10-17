from rest_framework import serializers
from .models import Product, Bundle


class ProductDataSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image_url = serializers.URLField()

class ProductListSerializer(serializers.Serializer):
    products = ProductDataSerializer(many=True)