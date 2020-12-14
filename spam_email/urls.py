from django.urls import path
from . import views
from .views import HistoryView, EmailDeleteView

urlpatterns = [
    path('', views.home, name='home'),
    path('history/', HistoryView.as_view(), name='history'),
    path('history/<int:pk>/delete/', EmailDeleteView.as_view(), name='email_delete'),
]