from django.urls import path
from users.views import sign_in, sign_up, sign_out

urlpatterns = [
    path('sign-in/', sign_in, name='sign-in'),
    path('sign-up/', sign_up, name='sign-up'),
    path('logout/', sign_out, name='logout'),
]