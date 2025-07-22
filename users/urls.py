from django.urls import path

from .views import CustomLoginView, CustomCreateUserView , LogoutView , UserProfileView , PasswordResetConfirmView, PasswordResetRequestView


app_name ='users'

urlpatterns = [
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/',
         PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('login/',CustomLoginView.as_view(),name= 'login'),
    path('create/',CustomCreateUserView.as_view(), name= 'create'),
    path('logout/',LogoutView.as_view(), name= 'logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),

]
