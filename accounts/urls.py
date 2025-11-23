from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import  login_view, logout_view, signup,current_user

urlpatterns = [
    
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('current-user/', current_user, name='current_user'),
]


