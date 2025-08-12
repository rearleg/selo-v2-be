from django.urls import path
from users.views import SignupView, LoginView, LogoutView

app_name = 'auth'

urlpatterns = [
    # POST /v1/signup
    path('', SignupView.as_view(), name='signup'),
    
    # POST /v1/login
    path('', LoginView.as_view(), name='login'),
    
    # POST /v1/logout  
    path('', LogoutView.as_view(), name='logout'),
]