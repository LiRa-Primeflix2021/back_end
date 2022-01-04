INSTALLATION stripe.exe   (source : https://github.com/stripe/stripe-cli/releases/latest) (https://stripe.com/docs/stripe-cli) (https://stripe.com/docs/stripe-cli/webhooks

->open prompt :

start stripe.exe

stripe login --interactive

sk_test_51K5qULCHYlGQuK8DVIeyda9GmeCALustT4HfkQOf7ie8ptlINb0yxcAJzoF9zryXCxkFhzSKfiiLsWycxJUF0c5600bc9NWCAT

stripe listen --forward-to 127.0.0.1:8000/store/webhooks/stripe/

(do not close prompt)

********************************************************************
INSTALLATION + RUN SERVER
********************************************************************
download + install python
create folder "project"
paste "back_end_folder" in "project"

->open a second prompt :

cd project

python -m venv primeflix_env

primeflix_env\scripts\activate

pip install djangorestframework

pip install djangorestframework-simplejwt

pip install stripe

pip install django-cors-headers 

pip install flask

pip install social-auth-app-django

cd primeflix
python manage.py runserver

-> in folder : project\primeflix_env\Lib\site-packages\rest_framework
-> open file : permissions.py 
-> add : SAFE_ACCESS = ()
-> save file

********************************************************************
RUN SERVER
********************************************************************

cd project
primeflix_env\scripts\activate
cd primeflix
python manage.py runserver



********************************************************************
ENDPOINTS LIST
********************************************************************

sign up user
POST
endpoint : 127.0.0.1:8000/account/register/
{
	"username":"diego",
	"email":"diego@gmail.com",
	"password":"informatique",
	"password2": "informatique"
}

********************************************************************

access token user (always carry the access token)
POST
endpoint : 127.0.0.1:8000/account/token/
{
	"username" : "diego", 
	"password" : "informatique"
}

********************************************************************

refresh token
POST
endpoint : 127.0.0.1:8000/account/token/refresh/
{
    "refresh" : "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY0MDg4MDI5MSwiaWF0IjoxNjQwNzkzODkxLCJqdGkiOiI2YzZmYTEzMzY3OWM0NDYzYmNjMmNkY2I4ZmIyMDQ2NCIsInVzZXJfaWQiOjV9.thFvUsTe-_Zri2KIVc5CQq0PSI_JO0DD7faZkMIzyFo"
}

********************************************************************

logout user
POST
endpoint : 127.0.0.1:8000/account/logout/

********************************************************************

cart + details (cart lines)
GET
endpoint : 127.0.0.1:8000/store/order/

********************************************************************

current cart lines
GET
endpoint : 127.0.0.1:8000/store/ordelines/

********************************************************************

list products + add product to cart 
GET, POST
endpoint : 127.0.0.1:8000/store/product/list/
{
	"product_id" : 5,
	"quantity" : 1
}

********************************************************************

product detail + add product to cart 
GET, PUT
endpoint : 127.0.0.1:8000/store/product/1/
{
    "quantity": 3
}

********************************************************************

cart line details (1 cart line) 
GET, PUT
endpoint : 127.0.0.1:8000/store/orderline/3/

{
    "quantity": 1
}

********************************************************************

orders paid 
GET
endpoint : 127.0.0.1:8000/store/orders-paid/

********************************************************************

product reviews
endpoint : 127.0.0.1:8000/store/product/1/reviews/
GET

********************************************************************

create movie review
route : 127.0.0.1:8000/store/1/review-create/
POST
{
	"rating" : 3,
	"description" : "just ok"   
}

********************************************************************

detail review + update + delete
GET, PUT, DELETE
endpoint : 127.0.0.1:8000/store/review/2/
{
    "rating": 5,
    "description" : "Nice movie"
}

********************************************************************

list themes
GET
endpoint : 127.0.0.1:8000/store/theme/list/

********************************************************************

payment checkout session
GET, POST
endpoint : 127.0.0.1:8000/store/create-checkout-session/
{
	"success_url" : "http://127.0.0.1:8000/store/product/list/",
	"cancel_url" : "http://127.0.0.1:8000/store/order/"
}
email : test@gmail.com
correct card information : 4242 4242 4242 4242     wrong card information : 4000 0000 0000 0002
date : 12/22
cvc : 123
nom : test

********************************************************************

shipping address details
GET, POST, PUT, DELETE
endpoint : 127.0.0.1:8000/store/shipping-address/
{
    "address": "Rue du Bonheur 777",
    "city": "Liège",
    "zipcode": "4000"
}


********************************************************************

update password and email
GET, PUT
endpoint : 127.0.0.1:8000/account/update-profile/
{
	"first_name" : "diego",
	"last_name" : "santiago", 
	"email":"diego@gmail.com",
	"password":"informatique",
	"password2": "informatique"
	
}

********************************************************************

find orders by title
GET
endpoint : 127.0.0.1:8000/store/orders-title/Titanic/

********************************************************************

find orders by title
GET
endpoint : 127.0.0.1:8000/store/orders-year/2021/	

********************************************************************
