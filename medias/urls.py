from django.urls import path
from . import views

app_name = 'medias'

urlpatterns = [
    path('images/', views.ImageListCreateView.as_view(), name='image-list-create'),
    path('images/upload/', views.ImageUploadView.as_view(), name='image-upload'),
    path('profile-images/', views.ProfileImageCreateView.as_view(), name='profile-image-create'),
    path('profile-images/upload/', views.ProfileImageUploadView.as_view(), name='profile-image-upload'),
]