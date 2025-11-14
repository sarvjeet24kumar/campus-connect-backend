from django.urls import path

from .views import create_admin, csrf_token, current_user, login_view, logout_view, signup

urlpatterns = [
    path('csrf-token/', csrf_token, name='csrf_token'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('current-user/', current_user, name='current_user'),
    path('create-admin/', create_admin, name='create_admin'),
]


