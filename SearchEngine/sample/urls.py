from django.urls import path

from . import views

urlpatterns = [
    path("one",views.one,name="one"),
    path("two",views.two,name="two"),
    path("three",views.three,name="three"),
    path("four",views.four,name="four"),
    path("five",views.five,name="five"),
    path("six",views.six,name="six"),
    path("seven",views.seven,name="seven"),
    path("eight",views.eight,name="eight"),
    path("nine",views.nine,name="nine"),
    path("ten",views.ten,name="ten"),
]