********************************************************************
INSTALLATION stripe
********************************************************************
-> download stripe_X.X.X_windows_x86_64.zip   (source : https://github.com/stripe/stripe-cli/releases/latest) (https://stripe.com/docs/stripe-cli) (https://stripe.com/docs/stripe-cli/webhooks
-> extract file 

-> open prompt :

start stripe.exe

stripe login --interactive

sk_test_51K5qULCHYlGQuK8DVIeyda9GmeCALustT4HfkQOf7ie8ptlINb0yxcAJzoF9zryXCxkFhzSKfiiLsWycxJUF0c5600bc9NWCAT

-> (press enter to confirm the name of your computer)

stripe listen --forward-to 127.0.0.1:8000/store/webhooks/stripe/

-> (do not close prompt)


********************************************************************
INSTALLATION project + RUN SERVER
********************************************************************
-> download + install last version python  (source : https://www.python.org/downloads/)

-> download zip "back_end-examen"
-> open zip and extract folder "back_end-examen"

-> open a second prompt :

cd back_end-examen

-> copy these 10 following commands and paste them :

primeflix_env\scripts\activate
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install stripe
pip install django-cors-headers 
pip install flask
pip install social-auth-app-django
cd primeflix
python manage.py runserver


(skip this part. It must be done if the virtual environment is new with the command "python -m venv primeflix_env")
-> in folder : project\primeflix_env\Lib\site-packages\rest_framework
-> open file : permissions.py 
-> add : SAFE_ACCESS = ()
-> save file


********************************************************************
RUN SERVER  (if you have done the installation and you want to start the app)
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
example jason format :
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
example jason format :
{
	"username" : "diego", 
	"password" : "informatique"
}

********************************************************************

refresh token
POST
endpoint : 127.0.0.1:8000/account/token/refresh/
example jason format :
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
example jason format :
{
	"product_id" : 5,
	"quantity" : 1
}

********************************************************************

product detail + add product to cart 
GET, PUT
endpoint : 127.0.0.1:8000/store/product/1/
example jason format :
{
    "quantity": 3
}

********************************************************************

cart line details (1 cart line) 
GET, PUT
endpoint : 127.0.0.1:8000/store/orderline/3/
example jason format :
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
example jason format :
{
	"rating" : 3,
	"description" : "just ok"   
}

********************************************************************

detail review + update + delete
GET, PUT, DELETE
endpoint : 127.0.0.1:8000/store/review/2/
example jason format :
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
example jason format :
{
	"success_url" : "http://127.0.0.1:8000/store/product/list/",
	"cancel_url" : "http://127.0.0.1:8000/store/order/"
}
example of data to test checkout session :
email : test@gmail.com
correct card information : 4242 4242 4242 4242     wrong card information : 4000 0000 0000 0002
date : 12/22
cvc : 123
nom : test

********************************************************************

shipping address details
GET, POST, PUT, DELETE
endpoint : 127.0.0.1:8000/store/shipping-address/
example jason format :
{
    "address": "Rue du Bonheur 777",
    "city": "Liège",
    "zipcode": "4000"
}


********************************************************************

update password and email
GET, PUT
endpoint : 127.0.0.1:8000/account/update-profile/
example jason format :
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

find orders by year
GET
endpoint : 127.0.0.1:8000/store/orders-year/2019/	


********************************************************************

find order lines by category
GET
endpoint : 127.0.0.1:8000/store/orderlines-category/Movie/

********************************************************************

find product by title
GET
endpoint : 127.0.0.1:8000/store/movie-title/Titanic/

********************************************************************

find products by Theme
GET
endpoint : 127.0.0.1:8000/store/movies-theme/Drama/

********************************************************************

find products by Category and by Theme
GET
endpoint : 127.0.0.1:8000/store/movies-category-theme/Movie/Drama/

********************************************************************







