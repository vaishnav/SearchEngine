from django.urls import path

from . import views

app_name = "engine"
urlpatterns = [
    path("index",views.index,name="index"),
    path("crawl",views.crawl, name="crawl"),
    path("rank",views.rank,name="rank"),
    path('indexer',views.index_call,name="indexer"),
    path("index/query",views.query,name="query"),
    path("q",views.q, name="q"),
    path("qc/<str:correction>",views.qc, name="qc"),
    path("aboutus", views.about_us,name="about_us")
]
