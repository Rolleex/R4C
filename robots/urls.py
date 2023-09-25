from django.urls import path

from robots.views import add_robot, report_of_week

urlpatterns = [

    path('create/', add_robot, name='add_robot'),
    path('download/', report_of_week),
]
