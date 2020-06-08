from django.urls import path
from .views import signin, signup, signout, signup_confirm_email

urlpatterns = [
    path('signin/', signin, name='signin'),
    path('signup_confirm_email/', signup_confirm_email, name='signup_confirm_email'),
    path('signup/', signup, name='signup'),
    path('logout/', signout, name='signout')
]