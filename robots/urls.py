from django.urls import path

from robots.views import add_robot

urlpatterns = [

    path('create/', add_robot, name='add_robot'),

]