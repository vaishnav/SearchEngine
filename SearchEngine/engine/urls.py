from django.urls import path

from . import views

urlpatterns = [
    path("index",views.index,name="index"),
    path("crawl",views.crawl, name="crawl"),
    path("rank",views.rank,name="rank"),
]
