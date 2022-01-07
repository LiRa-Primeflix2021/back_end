from django.urls import path
from primeflix_app.api.views import FindOrdersbyYear, FindOrdersbyTitle, stripe_webhook, CreateCheckoutSessionView, ThemeList, ProductListAdd, ProductDetails, ReviewList, ReviewCreate, ReviewDetails, OrdersPaid, OrderDetails, OrderLines, OrderLineDetails, ShippingAddressDetails

urlpatterns = [ 
    path('theme/list/', ThemeList.as_view(), name='theme-list'),  
    
    path('product/list/', ProductListAdd.as_view(), name='product-list'),
    path('product/<int:pk>/', ProductDetails.as_view(), name='product-details'),
      
    path('product/<int:pk>/reviews/', ReviewList.as_view(), name="review-list"),
    path('<int:pk>/review-create/', ReviewCreate.as_view(), name="review-create"),
    path('review/<int:pk>/', ReviewDetails.as_view(), name="review-details"),  
    
    path('orders-paid/', OrdersPaid.as_view(), name="orders-paid"),  
    path('order/', OrderDetails.as_view(), name="order"),
    path('orderlines/', OrderLines.as_view(), name="orderlines"),
    path('orderline/<int:pk>/', OrderLineDetails.as_view(), name="orderline-details"),
    path('orders-title/<str:title>/', FindOrdersbyTitle.as_view(), name="movies-paid"),
    path('orders-year/<str:year>/', FindOrdersbyYear.as_view(), name="orders-year"),
    
    path('shipping-address/', ShippingAddressDetails.as_view(), name='shipping_address'),

    path('create-checkout-session/', CreateCheckoutSessionView, name="checkout-session"),    
        
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),

    # path('products/', Products, name='products'),
    # path('categories/', Categories, name='categories'),
    # path('categorydetail/<int:pk>/', CategoryDetailsTEST, name='categories'),
    # path('category/list/', CategoryList.as_view(), name='category-list'),
    # path('category/<int:pk>/', CategoryDetails.as_view(), name='category-details'),
    # path('customer/list/', CustomerList.as_view(), name='customer-list'),
    # path('<int:pk>/order-payment/', OrderListPaid.as_view(), name="orders-payment"),
    # path('<int:pk>/orderlines/', OrderLines.as_view(), name="orderlines"),
    # path('order/<int:pk>/', OrderDetailsAV.as_view(), name="cart-details"),
    # path('theme/<int:pk>/', ThemeDetails.as_view(), name='theme-details'),
    # path('review/', ReviewList.as_view(), name="review-list"),
    # path('review/<int:pk>/', ReviewDetails.as_view(), name="review-details"),
]

