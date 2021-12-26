from django.urls import path, include
###### from primeflix.primelist_app.models import Review
# from primelist_app.api.views import movie_list, movie_details
# from primeflix_app.api.views import Categories, CategoryDetailsTEST ,Products, ProductAV, CreateCheckoutSessionView, CategoryList, CategoryDetails, ThemeList, ThemeDetails, ProductAV, ProductDetailsAV, ReviewList, ReviewCreate, ReviewDetails, OrderListPaid, OrderDetails, OrderLines, OrderLineDetails, ShippingAddress
from primeflix_app.api.views import CustomerList, CreateCheckoutSessionView, CategoryList, ThemeList, ProductList, ProductDetails, ReviewList, ReviewCreate, ReviewDetails, OrderListPaid, OrderDetails, OrderLines, OrderLineDetails, ShippingAddress

urlpatterns = [
    # path('customer/list/', CustomerList.as_view(), name='customer-list'),
    path('product/list/', ProductList.as_view(), name='product-list'),
    # path('products/', Products, name='products'),
    # path('categories/', Categories, name='categories'),
    # path('categorydetail/<int:pk>/', CategoryDetailsTEST, name='categories'),
    path('product/<int:pk>/', ProductDetails.as_view(), name='product-details'),
    # path('category/list/', CategoryList.as_view(), name='category-list'),
    # path('category/<int:pk>/', CategoryDetails.as_view(), name='category-details'),
    path('theme/list/', ThemeList.as_view(), name='theme-list'),
    # path('theme/<int:pk>/', ThemeDetails.as_view(), name='theme-details'),
    # path('review/', ReviewList.as_view(), name="review-list"),
    # path('review/<int:pk>/', ReviewDetails.as_view(), name="review-details"),
    path('product/<int:pk>/reviews/', ReviewList.as_view(), name="review-list"),
    path('<int:pk>/review-create/', ReviewCreate.as_view(), name="review-create"),
    path('review/<int:pk>/', ReviewDetails.as_view(), name="review-details"),
    # path('order/<int:pk>/', OrderDetailsAV.as_view(), name="cart-details"),
    path('orders-paid/', OrderListPaid.as_view(), name="orders-paid"),
    # path('<int:pk>/order-payment/', OrderListPaid.as_view(), name="orders-payment"),
    path('order/', OrderDetails.as_view(), name="order"),
    # path('<int:pk>/orderlines/', OrderLines.as_view(), name="orderlines"),
    path('orderlines/', OrderLines.as_view(), name="orderlines"),
    path('orderline/<int:pk>/', OrderLineDetails.as_view(), name="orderline-details"),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name="checkout-session"),
]

