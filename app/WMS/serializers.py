from rest_framework import serializers
from core.models import Tag, Category, Product, DeliveryOrder, Stock


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category objects"""

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product objects"""
    categories = CategorySerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Product
        fields = ('id', 'title', 'categories', 'tags', 'weight',
                  'price', 'link')
        read_only_fields = ('id',)


class ProductDetailSerializer(ProductSerializer):
    """Serialize a product detail"""
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading image to product"""

    class Meta:
        model = Product
        fields = ('id', 'image')
        read_only_fields = ('id',)


class DeliveryOrderSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryOrder objects"""
    products = ProductSerializer(many=True)

    class Meta:
        model = DeliveryOrder
        fields = ('id', 'deliveryNumber', 'sentFrom', 'sentTo', 'fullAddress',
                  'contactPerson', 'price', 'products')
        read_only_fields = ('id',)


class DeliveryOrderDetailSerializer(DeliveryOrderSerializer):
    """Serialize a DeliveryOrder detail"""
    products = ProductSerializer(many=True, read_only=True)


class StockSerializer(serializers.ModelSerializer):
    """Serializer for DeliveryOrder objects"""
    products = ProductSerializer(many=True)

    class Meta:
        model = Stock
        fields = ('id', 'StockNo', 'Quantity', 'Location', 'products')
        read_only_fields = ('id',)


class StockDetailSerializer(StockSerializer):
    """Serialize a DeliveryOrder detail"""
    products = ProductSerializer(many=True, read_only=True)
