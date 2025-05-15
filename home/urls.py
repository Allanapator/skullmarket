# home/urls.py
from django.urls import path, include
from .views import homepage, contact_view

urlpatterns = [
    path('', homepage, name='homepage'),
    path('contact/', contact_view, name='contact'),
    path('captcha/', include('captcha.urls')),
]
