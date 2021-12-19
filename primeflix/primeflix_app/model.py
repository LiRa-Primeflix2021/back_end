from django.test import TestCase
from .models import Category, Post

class TestPrimeflixAppModels(TestCase):
    
    def test_model_str(self):
        name = Category.objects.create()
