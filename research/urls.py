from django.urls import path
from . import views

app_name = 'research'

urlpatterns = [
    path('', views.research_home, name='research_home'),
    path('papers/', views.paper_list, name='paper_list'),
    path('papers/<int:pk>/', views.paper_detail, name='paper_detail'),
    path('papers/create/', views.paper_create, name='paper_create'),
    path('papers/<int:pk>/update/', views.paper_update, name='paper_update'),
    path('papers/<int:pk>/delete/', views.paper_delete, name='paper_delete'),
    path('experiments/', views.experiment_list, name='experiment_list'),
    path('experiments/create/', views.experiment_create, name='experiment_create'),
    path('experiments/<int:pk>/delete/', views.experiment_delete, name='experiment_delete'),
]
