from django.db import models
# from django.db.models.fields import related
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
# from django.db.models.deletion import CASCADE
from datetime import datetime    

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
            
    def __str__(self):
        return self.name


class Theme (models.Model):
    name = models.CharField(max_length=255)
        
    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    theme =  models.ForeignKey(Theme, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, unique=True)
    director = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    year = models.PositiveIntegerField(default=2000)
    duration = models.CharField(max_length=255, blank=True)
    trailer = models.CharField(max_length=255, blank=True)
    season = models.CharField(max_length=255, blank=True)
    # image = models.ImageField(upload_to='images/')
    image_a = models.CharField(max_length=255, blank=True)
    image_b = models.CharField(max_length=255, blank=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    # discount = models.PositiveSmallIntegerField()
    in_stock = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    average_rating = models.FloatField(default=0)
    number_ratings = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return self.title
    
    
class Review(models.Model):
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.CharField(max_length=200, null=True)
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    review_user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.rating) + "/5 for product : " + self.product.title + " | written by : " + str(self.review_user)
    

class Order(models.Model):
	order_paid = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, blank=True, null=True)
	order_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	payment_intent = models.CharField(max_length=100, blank=True, null=True)
	date_created = models.DateTimeField(default=datetime.now())
	date_ordered = models.DateTimeField(null=True)
	order_amount = models.PositiveIntegerField(default=0, null=True, blank=True)
	
 
	@property
	def get_test(self):
		total ='coucou'
		return total

	@property
	def get_total_order(self):
		queryset_orderLines = OrderLine.objects.filter(order=self)
		if queryset_orderLines.exists():
			total = 0

			for orderLine in queryset_orderLines:
				if (orderLine.order.id == self.id):
					total = total + orderLine.get_total_orderLine
			return total

	def __str__(self):
		return str(self.id) + " " + str(self.order_user)


class OrderLine(models.Model):
	quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
	date_update = models.DateTimeField(auto_now_add=True)
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name="order_lines")
	note = models.CharField(max_length=300, null=True, blank=True)
    
	@property
	def get_total_orderLine(self):
		if (self.quantity != 0):
			total = self.product.price * self.quantity
			return total
		else: 
			return 0 

	def __str__(self):
		return  str(self.id) + " -  for user : " + str(self.product) + " -   from order : " + str(self.order)
		return str(self.order) + str(self.orderLine_user) + str(self.order.order_user) + str(self.product) + " : " + str(self.product.price) + "€  * " + str(self.quantity) + " = " + self.get_total_orderLine + " €"


class ShippingAddress(models.Model):
	street = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_created = models.DateTimeField(auto_now_add=True)
	shippingAddress_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
	# order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return self.street


class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200, default=True, unique=True)
	stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
 
	def __str__(self):
		return self.email