# from re import search
from django.conf import settings
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework import generics, serializers, status
from rest_framework.decorators import api_view
from rest_framework.views import APIView, View
from rest_framework import mixins
from rest_framework import generics
from rest_framework.exceptions import APIException, ValidationError
from rest_framework import status
from rest_framework.permissions import OR, IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from stripe.api_resources import checkout
from primeflix_app.models import User, Category, Theme, Product, Review, Customer, Order, OrderLine, ShippingAddress
from primeflix_app.api.serializers import CategorySerializer, ThemeSerializer, ProductSerializer, ReviewSerializer, CustomerSerializer, OrderSerializer, OrderLineSerializer, ShippingAddressSerializer
from primeflix_app.api.permissions import IsAdminOrReadyOnly, IsReviewUserOrReadOnly, IsOrderLineUser
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
import os
import stripe
import json
import datetime


from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


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

         
                

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


@api_view(['GET', 'POST'])
def CreateCheckoutSessionView(request):
    permission_classes = [IsAuthenticated]

    print(request.data)
    print(request)
    # if (request.user != queryset_order[0].order_user):
    #             raise ValidationError("denied")

    temp_order = Order.objects.get(order_user=request.user, order_paid=False)
    queryset_Orderlines = OrderLine.objects.filter(orderLine_user=request.user, order=temp_order)
   
    if (request.user != temp_order.order_user):
                raise ValidationError("denied")
    
    if queryset_Orderlines.exists():
        
        if (request.method == 'POST'): 
            temp_line_items = []
            
            for orderline in queryset_Orderlines:
                temp_line_items.append({'price_data': {'currency': 'eur', 'product_data': {'name': orderline.product.title,},'unit_amount': int((orderline.product.price)*100),},'quantity': orderline.quantity,},)

            session = stripe.checkout.Session.create(
                # for queryset in queryset_Orderlines:
                # print(type(queryset))
                line_items=temp_line_items,
                metadata={
                "customer": temp_order.id
                },
                mode='payment',
                success_url= request.data['success_url'],
                # success_url='http://127.0.0.1:8000/store/product/list/',
                # success_url='https://www.aginteriors.be',
                # cancel_url='https://www.luga.be',
                # cancel_url='http://127.0.0.1:8000/store/order/',
                cancel_url=request.data['cancel_url'],
            )
            print(session)
            print(session.payment_intent)
            
            
            temp_order.payment_intent = session.payment_intent
            temp_order.save()
            # print(temp_order.payment_intent + ' HOLA ')
          
        return HttpResponse(session.url, session.payment_status)

    return HttpResponse("no product in cart")



# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


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

    # Handle the checkout.session.completed event
    
    if event['type'] == 'payment_intent.payment_failed':
        
        print("Alléluia 4")
        # print(payload)
        # intent = event['data']['object']
        # print(intent['customer'])
        # stripe_customer_id = intent["customer"]
        # stripe_customer = stripe.Customer.retrieve(stripe_customer_id)

        # customer_email = stripe_customer['email']
        # product_id = intent["metadata"]["product_id"]

        # product = Product.objects.get(id=product_id)


    # if event['type'] == 'checkout.session.completed':
    #     # session = event['data']['object']

    #     # customer_email = session["customer_details"]["email"]
    #     # product_id = session["metadata"]["product_id"]

    #     # product = Product.objects.get(id=product_id)
    #     print("Alléluia 1")
        
    elif event['type'] == 'checkout.session.completed':
        
        session = event['data']['object']
        customer_email = session["customer_details"]["email"]
        payment_intent = session["payment_intent"]
        print("Alléluia A")
        print(customer_email)
        print("Alléluia B")
        print(payment_intent)
        print("Alléluia C")
        print("Alléluia 2")
        intent = event['data']['object']
        print(intent['customer'])
        print("Alléluia 2 bis")
        
        temp_order = Order.objects.get(payment_intent=payment_intent)
        queryset = Order.objects.filter(order_user=temp_order.order_user)
        queryset.count()
        
        if temp_order.payment_intent == payment_intent:
            temp_order.order_paid = True
            temp_order.transaction_id=queryset.count()
            temp_order.date_ordered=datetime.datetime.now()
            temp_order.save() 
            new_order = Order(order_user=temp_order.order_user)
            new_order.save() 
            
            queryset_orderlines = OrderLine.objects.filter(order = temp_order)
            for orderline in queryset_orderlines:
                temp_product = Product.objects.get(pk=orderline.product.id)
                temp_product.quantity = temp_product.quantity - orderline.quantity
                temp_product.save()
            
            print('mega cool')
    else:
    # elif event["type"] == "payment_intent.succeeded":
        
        print("Alléluia 3")

    return HttpResponse(status=200)


# @csrf_exempt
# def my_webhook_view(request):
#   payload = request.body
#   event = None

#   try:
#     event = stripe.Event.construct_from(
#       json.loads(payload), stripe.api_key
#     )
#   except ValueError as e:
#     # Invalid payload
#     return HttpResponse(status=400)

#   # Handle the event
#   if event.type == 'payment_intent.succeeded':
#     payment_intent = event.data.object # contains a stripe.PaymentIntent
#     # Then define and call a method to handle the successful payment intent.
#     # handle_payment_intent_succeeded(payment_intent)
#   elif event.type == 'payment_method.attached':
#     payment_method = event.data.object # contains a stripe.PaymentMethod
#     # Then define and call a method to handle the successful attachment of a PaymentMethod.
#     # handle_payment_method_attached(payment_method)
#   # ... handle other event types
#   else:
#     print('Unhandled event type {}'.format(event.type))

#   return HttpResponse(status=200)


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class ReviewList(generics.ListAPIView):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(product=pk)
        

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
    
class ReviewDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly] /////////////////////////////////////////////:
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
        # temp_review = Review.objects.get(pk=pk)
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
        # pk = self.kwargs['pk']
        queryset_order = Order.objects.filter(order_user=self.request.user, order_paid=True)
        if queryset_order.exists():
            if (self.request.user != queryset_order[0].order_user):
                raise ValidationError("denied")
        if queryset_order.exists():
            return queryset_order
        else:
            raise ValidationError("no order paid")
    

   
class OrderLines(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderLineSerializer
    
    def get_queryset(self):
        
        queryset_order = Order.objects.filter(order_user=self.request.user, order_paid=False)
        if queryset_order.exists():
            if (self.request.user != queryset_order[0].order_user):
                raise ValidationError("denied")

        if queryset_order.exists():
            return OrderLine.objects.filter(orderLine_user=self.request.user, order=queryset_order[0])
        else:
            raise ValidationError("denied")
            
    # def perform_create(self, serializer):
    #         # pk = self.kwargs['pk']
    #         queryset_order = Order.objects.filter(order_user=self.request.user, order_paid=False)
           
    #         if queryset_order.exists():
            
    #             if (self.request.user != queryset_order[0].order_user):
    #                 raise ValidationError("denied")
                
    #             orderLine_queryset = OrderLine.objects.filter(product=serializer.validated_data['product'], orderLine_user=self.request.user, order=queryset_order[0])
                
    #             if orderLine_queryset.exists():    
    #                 temp_orderline = orderLine_queryset[0]                                
    #                 temp_orderline.quantity = temp_orderline.quantity + serializer.validated_data['quantity']
    #                 temp_orderline.save()
    #             else:
    #                 serializer.save(order=queryset_order[0], orderLine_user=queryset_order[0].order_user)


    
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
                    print(serializer.validated_data['note'])

                else:
                    serializer.validated_data['note']= ""
                 
                
                serializer.save()
        else:
            raise APIException("Order paid")





    
class OrderDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # pk = self.kwargs['pk']
        
        order_query = Order.objects.filter(order_user=self.request.user, order_paid=False)
        if order_query.exists():      
            if (self.request.user != order_query[0].order_user):
                raise ValidationError("you can't access this page")
            
            try:
                temp_order = Order.objects.get(order_user=self.request.user, order_paid=False)
            except Order.DoesNotExist:
                return Response('Error : Order doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
            
            serializer = OrderSerializer(temp_order)
            
            print(*serializer.data)
            print(serializer.data)
            
            print(type(self.kwargs))
            print(self.kwargs)
            print(temp_order.date_ordered)
            for key, value in serializer.data.items():
                print("'''''''''''''''''''''''''''''''''''''''''''''")
                print(key)
                print("'''''''''''''''''''''''''''''''''''''''''''''")
                print(value)
            

            return Response(serializer.data) 

    # def put(self, request):
    #     pass
        # pk = self.kwargs['pk']
        # order_query = Order.objects.filter(order_user=self.request.user, order_paid=False)
        # # order.order_paid = True
        # # order.save()
     
        
        # print (request)
        # print (request.data)
        # print (type(request.data))
        # print (request.data.items())
        
    
    # def perform_create(self, serializer):
    #     # pk = self.kwargs['pk']
    #     temp_product = Product.objects.get(pk=self.request.user)
    
    #     temp_review_user = self.request.user
    #     review_queryset = Review.objects.filter(product=temp_product, review_user=temp_review_user)
        
    #     if (review_queryset.exists()):
    #         raise ValidationError("you have already reviewed this product")
        
    #     if (temp_product.number_ratings == 0):
    #         temp_product.average_rating = serializer.validated_data['rating']
    #     else:
    #         temp_product.average_rating = ((temp_product.average_rating * temp_product.number_ratings ) + float(serializer.validated_data['rating'])) / float(temp_product.number_ratings + 1) 

    #     temp_product.number_ratings = temp_product.number_ratings + 1
    #     temp_product.save()  
    #     serializer.save(product=temp_product, review_user=temp_review_user)
            
    #     if serializer.is_valid():
    #         # print (serializer)
    #         serializer.save()
    #         # print(order_query[0].order_user)
    #         new_order = Order(order_user=self.request.user)
    #         # new_order = Order(order_user=order_query[0].order_user)
    #         new_order.save()
            
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# def perform_update(self, serializer):
#         # temp_review = Review.objects.get(pk=pk)
#         pk = self.kwargs['pk']
#         temp_review = Review.objects.get(pk=pk)
#         temp_product = Product.objects.get(pk=temp_review.product.id)
        
             
#         temp_product.save()  
#         serializer.save(product=temp_product)
        
        
        
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# def perform_update(self, serializer):
#         pk = self.kwargs['pk']
#         # serializer.save()
        
#         temp_orderline = OrderLine.objects.get(pk=pk)

#         if (self.request.user != temp_orderline.order.order_user):
#             raise ValidationError("denied")
                
#         # temp_order = Order.objects.filter(pk=temp_orderline.order.id, order_paid=False)
#         temp_order = Order.objects.get(pk=temp_orderline.order.id)
        
#         if ((temp_orderline.order == temp_order) and (temp_orderline.order.order_paid == False)):
#             serializer.save()

#         else:
#             raise APIException("Order paid")
        

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
     
    
class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadyOnly]
    
    def get_queryset(self):
        # pk = self.kwargs['pk']
        # return Review.objects.filter(product=pk)
        return Category.objects.all()
    
    # def post(self, request):
    #     serializer = CategorySerializer(data=request.data)
    #     if(serializer.is_valid()):
    #         serializer.save()
    #         return Response(serializer.data)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# class CategoryDetails(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAdminOrReadyOnly]
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    
class ThemeList(generics.ListAPIView):
    serializer_class = ThemeSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Theme.objects.all()
    
    def post(self, request):
        serializer = ThemeSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ThemeDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
            
class CustomerList(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAdminOrReadyOnly]

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        
        orderline = OrderLineDetails.objects.get(id=1)
        print("HOLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print(orderline.quantity)
        print("")
        print("HOLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        return Response(serializer.data)
 
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                
class ProductList(APIView):
    # permission_classes = [IsOrderLineUser]
    permission_classes = [IsAuthenticatedOrReadOnly]


    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        
        refresh_ratings()
        
        return Response(serializer.data)
    
    def post(self, request):
        temp_product = Product.objects.get(pk=int(request.data['product_id']))
        queryset_temp_order = Order.objects.filter(order_user=request.user, order_paid=False)
        # print(request.data)
        if request.data['quantity'] < 1:
            raise ValidationError("Quantity < 1")
        

        
        if queryset_temp_order.exists():
                    
            temp_order = queryset_temp_order[0]
            
            # print(temp_order)
            # print(temp_product)
            queryset_temp_orderline = OrderLine.objects.filter(product=temp_product, order=temp_order)
            
            print(queryset_temp_orderline.exists())
            # temp_orderline = queryset_temp_orderline[0]
            # print(temp_orderline)
            
            if queryset_temp_orderline.exists():
                
                temp_orderline = queryset_temp_orderline[0]
                
                serializer = OrderLineSerializer(temp_orderline, data=request.data)
                if(serializer.is_valid()):
                    
                    
                    # delta_quantity = serializer.validated_data['quantity'] - temp_orderline.quantity
                
                    temp_quantity = serializer.validated_data['quantity'] + temp_orderline.quantity
                    # if temp_product.quantity <= serializer.validated_data['quantity']:
                    if temp_product.quantity <= temp_quantity:
                        
                        serializer.validated_data['quantity'] = temp_product.quantity
                        serializer.validated_data['note']= str(serializer.validated_data['quantity']) + " products left. Quantity set to your order"
                        # print(serializer.validated_data['note'])
                         
                    else:
                        serializer.validated_data['quantity'] = temp_quantity
                        serializer.validated_data['note']= ""


                    # print(serializer.data)
                    serializer.validated_data['orderLine_user'] = request.user
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
                        # print(serializer.validated_data['note'])
                    else:
                        serializer.validated_data['note']= ""
                        
                    serializer.validated_data['orderLine_user'] = request.user
                    serializer.validated_data['product'] = temp_product
                    serializer.validated_data['order'] = temp_order            
                    serializer.save()
                    return Response(serializer.data)
                else:
                    return Response(serializer.errors) 
        
    
        else:
            raise APIException("Order paid")

    # def post(self, request):
    #     serializer = ProductSerializer(data=request.data)
    #     if(serializer.is_valid()):
    #         serializer.save()
    #         return Response(serializer.data)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def perform_create(self, serializer):
    #         pk = self.kwargs['pk']
    #         queryset_order = Order.objects.filter(order_user=pk, order_paid=False)
           
    #         if queryset_order.exists():
            
    #             if (self.request.user != queryset_order[0].order_user):
    #                 raise ValidationError("denied")
            
    #         # temp_customer = Customer.objects.get(pk=pk)
    #             temp_order = Order.objects.filter(order_user=pk, order_paid=False)
    #             serializer.save(order=temp_order[0], orderLine_user=temp_order[0].order_user)
                
                
                
    # def post(self, request):
    #     data = request.data
    #     user = request.data
        
    #     queryset_order = Order.objects.filter(order_user=request.user, order_paid=False)
        
    #     if queryset_order.exists():
            
    #         orderline = OrderLine.objects.get_or_create(orderLine_user=request.user, product=self)
            
            
    #         serializer = ProductSerializer(data=request.data)
    #         if(serializer.is_valid()):
    #             serializer.save()
    #             return Response(serializer.data)
    #         else:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   


class ProductDetails(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response('Error : Film doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product)
        return Response(serializer.data) 
    
    # def put(self, request, pk):
    #     product = Product.objects.get(pk=pk)
    #     serializer = ProductSerializer(product, data=request.data)
    #     if(serializer.is_valid()):
    #         serializer.save()
    #         return Response(serializer.data)
    #     else:
    #         return Response(serializer.errors) 
    
    # def delete(self, request, pk):       
    #         product = Product.objects.get(pk=pk)
    #         product.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)        
    
    def put(self, request, pk):
        temp_product = Product.objects.get(pk=pk)
        queryset_temp_order = Order.objects.filter(order_user=request.user, order_paid=False)
        # print(request.data)
        
        if (int(request.data['quantity'])) < 1:
            raise ValidationError("Quantity < 1")
        
        if queryset_temp_order.exists():
                    
            temp_order = queryset_temp_order[0]
            
            print(temp_order)
            print(temp_product)
            queryset_temp_orderline = OrderLine.objects.filter(product=temp_product, order=temp_order)
            
            print(queryset_temp_orderline.exists())
            # temp_orderline = queryset_temp_orderline[0]
            # print(temp_orderline)
            
            if queryset_temp_orderline.exists():
                
                temp_orderline = queryset_temp_orderline[0]
                
                serializer = OrderLineSerializer(temp_orderline, data=request.data)
                if(serializer.is_valid()):
                    
                    
                    # delta_quantity = serializer.validated_data['quantity'] - temp_orderline.quantity
                
                    temp_quantity = serializer.validated_data['quantity'] + temp_orderline.quantity
                    # if temp_product.quantity <= serializer.validated_data['quantity']:
                    if temp_product.quantity <= temp_quantity:
                                                
                        serializer.validated_data['quantity'] = temp_product.quantity
                        serializer.validated_data['note']= str(serializer.validated_data['quantity']) + " products left. Quantity set to your order"
                        # print(serializer.validated_data['note'])
                         
                    else:
                        serializer.validated_data['note']= ""


                    # print(serializer.data)
                    serializer.validated_data['orderLine_user'] = request.user
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
                        # print(serializer.validated_data['note'])
                    else:
                        serializer.validated_data['note']= ""
                        
                    serializer.validated_data['orderLine_user'] = request.user
                    serializer.validated_data['product'] = temp_product
                    serializer.validated_data['order'] = temp_order            
                    serializer.save()
                    return Response(serializer.data)
                else:
                    return Response(serializer.errors) 
        
    
        else:
            raise APIException("Order paid")
        
        
    # def perform_update(self, serializer):
    #     pk = self.kwargs['pk']
    #     # serializer.save()
        
    #     temp_orderline = OrderLine.objects.get(pk=pk)

    #     if (self.request.user != temp_orderline.order.order_user):
    #         raise ValidationError("denied")
               
    #     # temp_order = Order.objects.filter(pk=temp_orderline.order.id, order_paid=False)
    #     temp_order = Order.objects.get(pk=temp_orderline.order.id)
        
    #     if ((temp_orderline.order == temp_order) and (temp_orderline.order.order_paid == False)):
    #         temp_quantity = serializer.validated_data['quantity']
    #         if (temp_quantity==0):
    #             temp_orderline.delete()
    #         else:
    #             # print(temp_quantity)
    #             # print(type(temp_quantity))
                                
    #             temp_product = serializer.validated_data['product']
    #             # print(type(temp_product))
    #             # print(temp_product.quantity)
    #             # print(serializer.validated_data['quantity'])
    #             # temp_quantity = serializer.validated_data['quantity']
    #             # print(type(temp_quantity))
                
                
    #             delta_quantity = serializer.validated_data['quantity'] - temp_orderline.quantity
                
                
    #             if temp_product.quantity <= delta_quantity:
                    
                    
    #                 # print("Stock limited")
    #                 # serializer.validated_data['quantity'] = temp_p.quantity
    #                 # print(str(serializer.validated_data['quantity']) + " products left. Quantity set to your order")
    #                 # print(serializer.validated_data['note'])
    #                 serializer.validated_data['note']= str(serializer.validated_data['quantity']) + " products left. Quantity set to your order"
    #                 print(serializer.validated_data['note'])
    #                 # temp_product = Product.objects.get(pk=temp_p)
                    
    #                 # temp_p.quantity = 0
    #                 # temp_p.save()
    #                 print(self.amount_orderLine(self))
    #             else:
                    
    #                 # print(str(temp_orderline.get_total_orderLine()))
    #                 # print(type(temp_orderline.get_total_orderLine()))
    #                 print(temp_orderline.amount_orderLine)
                    
                    
                
    #             serializer.save()
        
 
 # /////////////////////////////////////////////////////////////////////////////////////////////////////        

 
 
 
# class StreamPlatformDetailsAV(APIView):
#     permission_classes = [IsAdminOrReadyOnly]

#     def get(self, request, pk):
#         try:
#             platform = StreamPlatformList.objects.get(pk=pk)
#         except StreamPlatformList.DoesNotExist:
#             return Response('Error : Platform doesn\'t exist in database', status=status.HTTP_404_NOT_FOUND)
        
#         serializer = StreamPlatformListSerializer(platform)
#         return Response(serializer.data) 
      
#     def put(self, request, pk):
#         platform = StreamPlatformList.objects.get(pk=pk)
#         serializer = StreamPlatformListSerializer(platform, data=request.data)
#         if(serializer.is_valid()):
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors) 
    
#     def delete(self, request, pk):       
#             platform = StreamPlatformList.objects.get(pk=pk)
#             platform.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)     
 
 
 
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



def index(request):
    message = "Hello World"
    return HttpResponse(message)

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
