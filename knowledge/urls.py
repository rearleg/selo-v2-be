from django.urls import path
from tips.views import KnowledgeListView

app_name = 'knowledge'

urlpatterns = [
    # GET /v1/knowledge
    path('', KnowledgeListView.as_view(), name='knowledge-list'),
]