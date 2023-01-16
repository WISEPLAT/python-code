from django.urls import path

from . import views

urlpatterns = [
    path('', views.Welcome.as_view(), name='welcome'),
    path('market/', views.Trading.as_view(), name='trading'),
    path('sandbox/', views.SandBox.as_view(), name='sandbox'),
]