from django.urls import path

from .views import place_order

urlpatterns = [
    path('make-order/', place_order)
]
