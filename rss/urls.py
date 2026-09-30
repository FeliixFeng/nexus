from django.urls import path

from . import views

app_name = "rss"

urlpatterns = [
    path("", views.today, name="today"),
    path("brief/", views.brief, name="brief"),
    path("brief/<str:day>/", views.brief, name="brief_day"),
    path("article/<str:item_id>/", views.article, name="article"),
    path("lab/", views.lab, name="lab"),
]
