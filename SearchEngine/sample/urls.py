from django.urls import path

from . import views

urlpatterns = [
    path("one",views.index,name="one"),
]