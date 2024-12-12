from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/internal/', views.internal_dashboard, name='internal_dashboard'),
    path('dashboard/client/', views.client_dashboard, name='client_dashboard'),
    path('generate-assessment/', views.generate_assessment, name='generate_assessment'),
    path('api/pillar-score-trends/', views.pillar_score_trends_api, name='pillar_score_trends_api'),
]

# touched on 2025-05-27T15:29:02.325030Z
# touched on 2025-05-27T15:45:56.087430Z