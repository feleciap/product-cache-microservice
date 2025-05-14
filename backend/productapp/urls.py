from django.urls import path
from .views import get_product

urlpatterns = [
    path('<int:product_id>/', get_product),
]
