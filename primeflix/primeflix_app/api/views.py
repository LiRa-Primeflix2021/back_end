# from re import search
from django.conf import settings
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.exceptions import APIException, ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from primeflix_app.models import Theme, Product, Review, Order, OrderLine, ShippingAddress
from primeflix_app.api.serializers import ThemeSerializer, ProductSerializer, ReviewSerializer, OrderSerializer, OrderLineSerializer, ShippingAddressSerializer
from primeflix_app.api.permissions import IsReviewUserOrReadOnly, IsOrderLineUser, IsOrderUser
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.urls import reverse
import stripe
import json
import datetime
from datetime import date
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# shipping address managament
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    
class ShippingAddressDetails(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            temp_shippingAddress = ShippingAddress.objects.get(shippingAddress_user=request.user)
        except ShippingAddress.DoesNotExist:
            return Response('Error : Shipping Address doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
        
        serializer = ShippingAddressSerializer(temp_shippingAddress)
        return Response(serializer.data)
     
    def post(self, request, format=None):
        quertsyet_temp_shippingAddress = ShippingAddress.objects.filter(shippingAddress_user=request.user)
        
        if quertsyet_temp_shippingAddress.exists():
            raise ValidationError("you have already an address")
        
        else: 
            serializer = ShippingAddressSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['shippingAddress_user'] = request.user 
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        temp_shippingAddress = ShippingAddress.objects.get(shippingAddress_user=request.user)
        serializer = ShippingAddressSerializer(temp_shippingAddress, data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors) 
    
    def delete(self, request):       
            temp_shippingAddress = ShippingAddress.objects.get(shippingAddress_user=request.user)
            temp_shippingAddress.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)    
                         


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# payment and stock managament
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


@api_view(['GET', 'POST'])
def CreateCheckoutSessionView(request):
    permission_classes = [IsAuthenticated]

    temp_order = Order.objects.get(order_user=request.user, order_paid=False)
    queryset_Orderlines = OrderLine.objects.filter(order__order_user=request.user, order=temp_order)
   
    if (request.user != temp_order.order_user):
                raise ValidationError("denied")
    
    if queryset_Orderlines.exists():
        
        if (request.method == 'POST'): 
            temp_line_items = []
            
            for orderline in queryset_Orderlines:
                temp_line_items.append({'price_data': {'currency': 'eur', 'product_data': {'name': orderline.product.title,},'unit_amount': int((orderline.product.price)*100),},'quantity': orderline.quantity,},)

            session = stripe.checkout.Session.create(
                line_items=temp_line_items,
                metadata={
                "customer": temp_order.id
                },
                mode='payment',
                success_url= request.data['success_url'],
                # success_url='http://127.0.0.1:8000/store/product/list/',
                # cancel_url='http://127.0.0.1:8000/store/order/',
                cancel_url=request.data['cancel_url'],
            )
                        
            temp_order.payment_intent = session.payment_intent
            temp_order.save()
          
        return HttpResponse(session.url, session.payment_status)

    return HttpResponse("no product in cart")



# 
# event listener from stripe
# if session is complete -> update stock + set amount
#
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        
        session = event['data']['object']
        payment_intent = session["payment_intent"]        
        temp_order = Order.objects.get(payment_intent=payment_intent)
        queryset = Order.objects.filter(order_user=temp_order.order_user)
        queryset.count()
        
        if temp_order.payment_intent == payment_intent:
            temp_order.order_paid = True
            temp_order.transaction_id=queryset.count()
            temp_order.date_ordered=datetime.datetime.now()
            temp_order.order_amount=temp_order.get_total_order
            temp_order.save() 
            
            new_order = Order(order_user=temp_order.order_user)
            new_order.save() 
            
            queryset_orderlines = OrderLine.objects.filter(order = temp_order)
            for orderline in queryset_orderlines:
                temp_product = Product.objects.get(pk=orderline.product.id)
                temp_product.quantity = temp_product.quantity - orderline.quantity
                temp_product.save()
            
            print('alleluia')
            
    elif event['type'] == 'payment_intent.payment_failed':
        raise ValueError('payment failed')  
           

    return HttpResponse(status=200)


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# reviews management
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class ReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(product=pk)
        
        
# 
# only one review from an user for a product
# update rating after a new review
#
class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.all()
    
    def perform_create(self, serializer):
        pk = self.kwargs['pk']
        temp_product = Product.objects.get(pk=pk)
    
        temp_review_user = self.request.user
        review_queryset = Review.objects.filter(product=temp_product, review_user=temp_review_user)
        
        if (review_queryset.exists()):
            raise ValidationError("you have already reviewed this product")
        
        if (temp_product.number_ratings == 0):
            temp_product.average_rating = serializer.validated_data['rating']
        else:
            temp_product.average_rating = ((temp_product.average_rating * temp_product.number_ratings ) + float(serializer.validated_data['rating'])) / float(temp_product.number_ratings + 1) 

        temp_product.number_ratings = temp_product.number_ratings + 1
        
        temp_product.save()  
        
          
        if(serializer.is_valid()):
            
            serializer.validated_data['product'] = temp_product        
            serializer.validated_data['active'] = True
            serializer.save(product=temp_product, review_user=temp_review_user)    
        else:
            return Response(serializer.errors)   
  
  
# 
# only one review from an user for a product
# update rating after updating or deleting a review
#   
class ReviewDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewUserOrReadOnly]
    
    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        temp_review = Review.objects.get(pk=pk)
        temp_product = Product.objects.get(pk=temp_review.product.id)
        
        if(temp_product.number_ratings > 1):      
            temp_product.average_rating = ((temp_product.average_rating * temp_product.number_ratings ) - temp_review.rating) / (temp_product.number_ratings - 1)
        else:
             temp_product.average_rating = 0
             
        temp_product.number_ratings = temp_product.number_ratings - 1 
        temp_product.save()
        return self.destroy(request, *args, **kwargs)
    
    
    def perform_update(self, serializer):
        pk = self.kwargs['pk']
        temp_review = Review.objects.get(pk=pk)
        temp_product = Product.objects.get(pk=temp_review.product.id)
        
        if(temp_product.number_ratings > 0):      
            temp_product.average_rating = ((temp_product.average_rating * temp_product.number_ratings ) - temp_review.rating + serializer.validated_data['rating']) / temp_product.number_ratings
        else:
            temp_product.average_rating = temp_review.rating
             
        temp_product.save()  
        
        if(serializer.is_valid()):
            
            serializer.validated_data['product'] = temp_product        
            serializer.validated_data['active'] = True
            serializer.save(product=temp_product)     
        else:
            return Response(serializer.errors) 
        

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Orders and Orderlines management 
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

      
class OrdersPaid(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer    

    def get_queryset(self):
        queryset_order = Order.objects.filter(order_user=self.request.user, order_paid=True)
        if queryset_order.exists():
            if (self.request.user != queryset_order[0].order_user):
                raise ValidationError("denied")
        if queryset_order.exists():
            return queryset_order
        else:
            raise ValidationError("no order paid")
    

#
# current cart (not paid!) + cart lines
# 
class OrderDetails(APIView):
    permission_classes = [IsOrderUser]

    def get(self, request):        
        order_query = Order.objects.filter(order_user=self.request.user, order_paid=False)
        if order_query.exists():      
            if (self.request.user != order_query[0].order_user):
                raise ValidationError("denied")
            try:
                temp_order = Order.objects.get(order_user=self.request.user, order_paid=False)
            except Order.DoesNotExist:
                return Response('Error : Order doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
            
            serializer = OrderSerializer(temp_order)
            
            
            
            
            return Response(serializer.data)     


# 
# current cart lines 
#    
class OrderLines(generics.ListCreateAPIView):
    permission_classes = [IsOrderLineUser]
    serializer_class = OrderLineSerializer
    
    def get_queryset(self):
        
        queryset_order = Order.objects.filter(order_user=self.request.user, order_paid=False)
        if queryset_order.exists():
            if (self.request.user != queryset_order[0].order_user):
                raise ValidationError("denied")

        if queryset_order.exists():
            return OrderLine.objects.filter(order__order_user=self.request.user, order=queryset_order[0])
        else:
            raise ValidationError("denied")
            

# 
# 1 cart line details + update quantity (only available if cart line is not paid)  
# 
class OrderLineDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOrderLineUser]
    serializer_class = OrderLineSerializer 
    
    queryset = OrderLine.objects.all()
    
    def delete(self, request, *args, **kwargs):
        temp_orderline = OrderLine.objects.get(pk=self.request.user)

        if (self.request.user != temp_orderline.order.order_user):
            raise ValidationError("denied")
        
        temp_order = Order.objects.filter(order_user=temp_orderline.order.order_user, order_paid=False)
        if temp_order.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError("denied")
    
    
    def perform_update(self, serializer):
        pk = self.kwargs['pk']
                
        temp_orderline = OrderLine.objects.get(pk=pk)

        if (self.request.user != temp_orderline.order.order_user):
            raise ValidationError("denied")
               
        temp_order = Order.objects.get(pk=temp_orderline.order.id)
        
        if ((temp_orderline.order == temp_order) and (temp_orderline.order.order_paid == False)):
            temp_quantity = serializer.validated_data['quantity']
            if temp_quantity == 0:
                temp_orderline.delete()
            elif temp_quantity < 0:
                raise APIException("Bad quantity")
                
            else:                
                if temp_orderline.product.quantity <= serializer.validated_data['quantity']:
                    
                    serializer.validated_data['quantity'] = temp_orderline.product.quantity
                    serializer.validated_data['note']= str(serializer.validated_data['quantity']) + " products left. Quantity set to your order"
                    
                else:
                    serializer.validated_data['note']= ""
                
                serializer.save()
        else:
            raise APIException("Denied")





#
# 
#  

class FindOrdersbyTitle(generics.ListAPIView):
    permission_classes = [IsOrderUser]
    serializer_class = OrderSerializer

    def get_queryset(self):
        temp_title = self.kwargs['title']
        temp_product = Product.objects.get(title=temp_title)
        queryset_orderLines = OrderLine.objects.filter(product=temp_product, order__order_user=self.request.user)
        queryset_orders = []
        for item in queryset_orderLines:
            queryset_orders.append(item.order)
        return queryset_orders


class FindOrdersbyYear(generics.ListAPIView):
    permission_classes = [IsOrderUser]
    serializer_class = OrderSerializer

    def get_queryset(self):
        temp_year = self.kwargs['year']
        first_date = datetime.date(int(temp_year), 1, 1)
        last_date = datetime.date(int(temp_year), 12, 31)
        return Order.objects.filter(date_ordered__range = (first_date, last_date), order_user=self.request.user, order_paid=True)
    
    

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# products management (many=True :> ProductSerializer needs to consult multiple objects in the query set and map them)
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# 
# product list + add one specific product to cart (quantity limited to the available stock)
# a check is done if the product is already in cart
#
class ProductListAdd(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True) 
        # refresh_ratings()
        return Response(serializer.data)
    
    def post(self, request):
        temp_product = Product.objects.get(pk=int(request.data['product_id']))
        queryset_temp_order = Order.objects.filter(order_user=request.user, order_paid=False)

        if request.data['quantity'] < 1:
            raise ValidationError("Quantity < 1")     
        
        if queryset_temp_order.exists():                    
            temp_order = queryset_temp_order[0]
            queryset_temp_orderline = OrderLine.objects.filter(product=temp_product, order=temp_order)
            
            if queryset_temp_orderline.exists():               
                temp_orderline = queryset_temp_orderline[0]  
                serializer = OrderLineSerializer(temp_orderline, data=request.data)
                
                if(serializer.is_valid()):
                    temp_quantity = serializer.validated_data['quantity'] + temp_orderline.quantity
                    
                    if temp_product.quantity <= temp_quantity:
                        serializer.validated_data['quantity'] = temp_product.quantity
                        serializer.validated_data['note']= str(serializer.validated_data['quantity']) + " products left. Quantity set to your order"
 
                    else:
                        serializer.validated_data['quantity'] = temp_quantity
                        serializer.validated_data['note']= ""

                    serializer.validated_data['order__order_user'] = request.user
                    serializer.validated_data['product'] = temp_product
                    serializer.validated_data['order'] = temp_order            
                    serializer.save()
                    return Response(serializer.data)
                
                else:
                    return Response(serializer.errors) 
            
            else:
                temp_orderline = OrderLine()             
                serializer = OrderLineSerializer(temp_orderline, data=request.data)
                
                if(serializer.is_valid()):
                    
                    if temp_product.quantity <= serializer.validated_data['quantity']:
                        
                        serializer.validated_data['quantity'] = temp_product.quantity
                        serializer.validated_data['note']= str(serializer.validated_data['quantity']) + " products left. Quantity set to your order"
                    
                    else:
                        serializer.validated_data['note']= ""
                        
                    serializer.validated_data['order__order_user'] = request.user
                    serializer.validated_data['product'] = temp_product
                    serializer.validated_data['order'] = temp_order            
                    serializer.save()
                    return Response(serializer.data)
                
                else:
                    return Response(serializer.errors) 
        else:
            raise APIException("Order paid")


# 
# product detail + add to cart (quantity limited to the available stock)
# a check is done if the product is already in the cart
#
class ProductDetails(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response('Error : Film doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product)
        return Response(serializer.data) 
     
    
    def put(self, request, pk):
        temp_product = Product.objects.get(pk=pk)
        queryset_temp_order = Order.objects.filter(order_user=request.user, order_paid=False)
        
        if (int(request.data['quantity'])) < 1:
            raise ValidationError("Quantity < 1")
        
        if queryset_temp_order.exists():
                    
            temp_order = queryset_temp_order[0]
            queryset_temp_orderline = OrderLine.objects.filter(product=temp_product, order=temp_order)

            if queryset_temp_orderline.exists():   
                 
                temp_orderline = queryset_temp_orderline[0]   
                serializer = OrderLineSerializer(temp_orderline, data=request.data)
                
                if serializer.is_valid():             
                    temp_quantity = serializer.validated_data['quantity'] + temp_orderline.quantity
                    
                    if temp_product.quantity <= temp_quantity:                         
                        serializer.validated_data['quantity'] = temp_product.quantity
                        serializer.validated_data['note']= str(serializer.validated_data['quantity']) + " products left. Quantity set to your order"
                         
                    else:
                        serializer.validated_data['note']= ""

                    serializer.validated_data['order__order_user'] = request.user
                    serializer.validated_data['product'] = temp_product
                    serializer.validated_data['order'] = temp_order            
                    serializer.save()
                    return Response(serializer.data)
                
                else:
                    return Response(serializer.errors) 
            
            else:
                print(temp_product)
                print(request.data)
                temp_orderline = OrderLine()
                               
                serializer = OrderLineSerializer(temp_orderline, data=request.data)
                if(serializer.is_valid()):
                    
                    if temp_product.quantity <= serializer.validated_data['quantity']:
                        
                        serializer.validated_data['quantity'] = temp_product.quantity
                        serializer.validated_data['note']= str(serializer.validated_data['quantity']) + " products left. Quantity set to your order"
                    
                    else:
                        serializer.validated_data['note']= ""
                        
                    serializer.validated_data['order__order_user'] = request.user
                    serializer.validated_data['product'] = temp_product
                    serializer.validated_data['order'] = temp_order            
                    serializer.save()
                    
                    return Response(serializer.data)
                
                else:
                    return Response(serializer.errors) 
        
    
        else:
            raise APIException("Order paid")
               
 

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Theme list
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class ThemeList(generics.ListAPIView):
    serializer_class = ThemeSerializer

    def get_queryset(self):
        return Theme.objects.all()
    
    # def post(self, request):
    #     serializer = ThemeSerializer(data=request.data)
    #     if(serializer.is_valid()):
    #         serializer.save()
    #         return Response(serializer.data)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)       
    










# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# useless functions
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
         
def index(request):
    message = "Hello World"
    return HttpResponse(message)    


def refresh_ratings():
    products = Product.objects.all()
    if (products.exists()):
        for p in products:
            reviews = Review.objects.filter(product=p)
            if (reviews.exists()):
                p.number_ratings=reviews.count()
                average_rating = 0
                for r in reviews:
                    average_rating = average_rating + r.rating
                average_rating = average_rating/reviews.count()
                p.average_rating = average_rating 
                p.save()
                
                        
# def set_order_init():  
#     customers = Customer.objects.all()
    
#     if customers.exists():
#         for c in customers:
#             orders = Order.objects.filter(customer=c, order_paid=False)
#             if orders.exists():
#                 pass
#             else:
#                 print(type(c.id))
#                 order = Order()
#                 order.customer = c
#                 order.save()
        
    

# class CategoryList(generics.ListAPIView):
#     serializer_class = CategorySerializer
#     permission_classes = [IsAdminOrReadyOnly]
    
#     def get_queryset(self):
#         return Category.objects.all()    
        
            
# class CustomerList(APIView):
#     # permission_classes = [IsAuthenticated]
#     permission_classes = [IsAdminOrReadyOnly]

#     def get(self, request):
#         customers = Customer.objects.all()
#         serializer = CustomerSerializer(customers, many=True)
        

#         return Response(serializer.data)
 
 
 
# /////////////////////////////////////////////////////////////////////////////////////////////////////        




# # many=True :> MovieSerializer needs to consult multiple (not only a single)
# # objects in the query set and map them
# @api_view(['GET', 'POST'])
# def movie_list(request):
    
#     if (request.method == 'GET'): 
#         movies = Movie.objects.all()
#         serializer = MovieSerializer(movies, many=True)
#         return Response(serializer.data) 
      
#     if (request.method == 'POST'): 
#         serializer = MovieSerializer(data=request.data)
#         if(serializer.is_valid()):
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'PUT', 'DELETE'])
# def movie_details(request, pk):
    
#     if(request.method == 'GET'): 
#         try:
#             movie = Movie.objects.get(pk=pk)
#         except Movie.DoesNotExist:
#             return Response('Error : Film inexistant', status=status.HTTP_404_NOT_FOUND)
        
#         serializer = MovieSerializer(movie)
#         return Response(serializer.data)   
     
#     if(request.method == 'PUT'):
#         movie = Movie.objects.get(pk=pk)
#         serializer = MovieSerializer(movie, data=request.data)
#         if(serializer.is_valid()):
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors) 
           
#     if(request.method == 'DELETE'):   
#         movie = Movie.objects.get(pk=pk)
#         movie.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)





def add_numbers():
    l = [1,2,3]
    return l

def add_test():
    d = {'voiture' : 'golff', 'fille' : 'claudette'}
    return d
    
# def index(request):
#     message = add_numbers()
#     message.append("coucFou")
    
#     message2 = add_test()
#     print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
#     print(message2)
#     print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
#     print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
#     # print(**message2)
#     print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
#     print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

#     for i in message:
#         print(i)
#     print (message)
#     print (*message)
#     print(type(message))
#     print(type(message2))
    
#     for key, value in message2.items():
#         print("'''''''''''''''''''''''''''''''''''''''''''''")
#         print(key)
#         print("'''''''''''''''''''''''''''''''''''''''''''''")
#         print(value)

#     # print(type(*message))
    
#     orderL_temp = OrderLine.objects.get(pk=7)
#     print(orderL_temp)
#     test = orderL_temp.get_total_orderLine()
   
    
#     print(test)
    
#     order_temp = Order.objects.get(pk=5)
#     print(order_temp.get_total_order())
#     test = order_temp.get_total_order()
      
#     print(test)
   
   
   
#     print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
#     # print(orderL_temp.get_total_OL())
#     return HttpResponse(test)



# def Products (request):
#     # if (request.method == 'GET'): 
#         queryset_products = Product.objects.all()
#         serializer = ProductSerializer(queryset_products, many=True)
#         print("11111111111111111111111111111111111111111111111111111111111")
#         print(type(queryset_products))
#         print("222222222222222222222222222222222222222222222222")

#         print(queryset_products)
#         print("33333333333333333333333333333333333333")
#         print(type(serializer))
#         print("44444444444444444444444444")

#         print(dir(serializer))
#         print("5555555555555555555555555555555555555555")
#         print(type(serializer.data))
#         print("666666666666666666666666666666666666666666666666")
#         print(vars(serializer))
#         print("7777777777777777777777777777777777777777777777777777777777")
#         print("")
        
#         return Response(serializer.data)
    
#     if (request.method == 'GET'): 
#         movies = Movie.objects.all()
#         serializer = MovieSerializer(movies, many=True)
#         return Response(serializer.data) 

# @api_view(['GET', 'POST'])
# def Categories (request):
#     if (request.method == 'GET'): 

#         queryset_products = Category.objects.all()
#         serializer = CategorySerializer(queryset_products, many=True)    
#         return Response(serializer.data) 

#     if (request.method == 'POST'): 
#         serializer = CategorySerializer(data=request.data)
#         if(serializer.is_valid()):
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'DELETE'])
# def CategoryDetailsTEST(request, pk):
    
#     if(request.method == 'GET'): 
#         try:
#             category = Category.objects.get(pk=pk)
#         except Category.DoesNotExist:
#             return Response('Error : Category inexistant', status=status.HTTP_404_NOT_FOUND)
        
#         serializer = CategorySerializer(category)
#         # print(type(name))
#         return Response({serializer.data})   
