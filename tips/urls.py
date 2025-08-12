from django.urls import path
from . import views

app_name = 'tips'

urlpatterns = [
    # GET /v1/tips
    path('', views.TipsListView.as_view(), name='tips-list'),
]