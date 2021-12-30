from rest_framework import serializers
from primeflix_app.models import Category, Theme, Product, Review, Customer, Order, OrderLine, ShippingAddress



class ReviewSerializer(serializers.ModelSerializer):
    review_user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        # fields = "__all__"
        exclude = ('product',)


class ProductSerializer(serializers.ModelSerializer):
    # len_title = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    theme = serializers.StringRelatedField(read_only=True)
    
    
    class Meta:
        model = Product
        fields = "__all__"
        # fields = ['id', 'name', 'description', 'active'] 
        # exclude = ['active']
        # exclude = ('average_rating','number_ratings',)
        read_only_fields = ('average_rating', 'number_ratings')
        
    def get_len_title(self, object):
        return len(object.title)
        
    # def validate(self, data):
    #     if (data['title'] == data['description']):
    #         raise serializers.ValidationError("Title and description should be different")
    #     else:
    #         return data
        
    def validate_title(self, value):
        if (len(value) < 2):
            raise serializers.ValidationError("Title is too short")
        else:
            return value



# class StreamPlatformListSerializer(serializers.ModelSerializer):
#     products = ProductSerializer(many=True, read_only=True)
        
#     class Meta:
#         model = StreamPlatformList
#         fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
        
    class Meta:
        model = Category
        fields = "__all__"
        # exclude = ('name',)
     
        
class ThemeSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
        
    class Meta:
        model = Theme
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    # product = ProductSerializer(many=True, read_only=True)
        
    class Meta:
        model = Customer
        fields = "__all__"
        


class OrderLineSerializer(serializers.ModelSerializer):
    # customer = serializers.StringRelatedField(read_only=True)
    order = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderLine
        fields = "__all__"
        # exclude = ('orderLine_user',)
    

class OrderSerializer(serializers.ModelSerializer):
    order_lines = OrderLineSerializer(many=True, read_only=True)
    # customer = serializers.StringRelatedField(read_only=True)
        
    class Meta:
        model = Order
        fields = "__all__"   
        # exclude = ('customer',)
    
class ShippingAddressSerializer(serializers.ModelSerializer):
    # customer = CustomerSerializer(read_only=True)
    order = OrderSerializer(many=True, read_only=True)
        
    class Meta:
        model = ShippingAddress
        fields = "__all__"
        

# def name_length(value):
#         if (len(value) < 2):
#             raise serializers.ValidationError("Name is too short")

# class WatchListSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     name = serializers.CharField(validators = [name_length])
#     description = serializers.CharField()
#     active = serializers.BooleanField()
    
#     def create(self, validated_data):
#         return WatchList.objects.create(**validated_data)
    
#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.description = validated_data.get('description', instance.description)
#         instance.active = validated_data.get('active', instance.active)
#         instance.save()
#         return instance
     
#     def validate(self, data):
#         if (data['name'] == data['description']):
#             raise serializers.ValidationError("Name and description should be different")
#         else:
#             return data
            
#     # def validate_name(self, value):
#     #     if (len(value) < 2):
#     #         raise serializers.ValidationError("Name is too short")
#     #     else:
#     #         return value
    
    