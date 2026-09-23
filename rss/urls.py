from django.urls import path

from . import views

app_name = "rss"

urlpatterns = [
    path("", views.today, name="today"),
    path("unread/", views.unread, name="unread"),
    path("stream/", views.stream, name="stream"),
    path("brief/", views.brief, name="brief"),
    path("article/<str:item_id>/", views.article, name="article"),
]
