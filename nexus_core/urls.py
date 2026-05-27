from django.urls import path
from . import views

app_name = 'nexus_core'

urlpatterns = [
    path('', views.home, name='home'),
]
