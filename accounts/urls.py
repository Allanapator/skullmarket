from django.urls import path
from .views import signup, edit_account

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('edit/', edit_account, name='account_edit'),
]
