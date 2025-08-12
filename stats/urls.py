from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    # GET /v1/ranking
    path('', views.RankingListView.as_view(), name='ranking-list'),
    
    # GET /v1/ranking/<int:user_id>
    path('<int:user_id>/', views.UserRankingDetailView.as_view(), name='user-ranking-detail'),
]