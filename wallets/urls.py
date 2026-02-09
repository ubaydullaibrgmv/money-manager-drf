from django.urls import path
from .views import WalletListCreateAPIView, CategoryListCreateAPIView, TransactionListCreateAPIView, \
    TransactionDetailAPIView, DashboardChartsAPIView, TransactionStatisticsAPIView

urlpatterns = [
    path('', WalletListCreateAPIView.as_view(), name='wallet-list-create'),
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('transactions/', TransactionListCreateAPIView.as_view(), name='transaction-list-create'),
    path('charts/', DashboardChartsAPIView.as_view(), name='dashboard-charts'),
    path('transactions/<int:pk>/', TransactionDetailAPIView.as_view(), name='transaction-detail'),
    path('stats/', TransactionStatisticsAPIView.as_view(), name='transaction-stats'),
    path('charts/', DashboardChartsAPIView.as_view(), name='dashboard-charts'),
]