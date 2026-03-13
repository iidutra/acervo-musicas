from django.urls import path

from apps.core.views import DashboardView

app_name = 'core'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]
