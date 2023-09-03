from rest_framework import serializers
from .models import Category, MenuItem, Cart
from django.contrib.auth.models import User

class CategorySerialiser(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerialiser(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class CartSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField(method_name='calculate_price')
    
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price', 'total_price']

    def calculate_price(self, product:Cart):
        return product.unit_price * product.quantity