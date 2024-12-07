from django.urls import path
from . import views

urlpatterns = [
    # ... existing paths ...
    path('login/', views.login, name='login'),
]