from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from .models import Wallet, Category, Transaction
from .serializers import (
    WalletSerializer,
    CategorySerializer,
    TransactionSerializer,
    UserCreateSerializer
)
from .utils import get_usd_rate


class TransactionStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        usd_to_uzs = get_usd_rate()

        wallets = Wallet.objects.filter(user=user)
        total_balance_uzs = 0

        for wallet in wallets:
            if wallet.currency == 'USD':
                total_balance_uzs += (wallet.balance * usd_to_uzs)
            else:
                total_balance_uzs += wallet.balance


        return Response({
            "total_balance_uzs": round(total_balance_uzs, 2),
            "current_usd_rate": usd_to_uzs,
            "currency": "UZS"
        })

class WalletListCreateAPIView(ListCreateAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class TransactionListCreateAPIView(ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'category', 'wallet', 'date']

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class TransactionDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        instance.delete()


class UserCreateAPIView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class DashboardChartsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        seven_days_ago = timezone.now() - timedelta(days=7)

        daily_expenses = (
            Transaction.objects.filter(
                wallet__user=user,
                type='EXPENSE',
                date__gte=seven_days_ago
            )
            .annotate(day=TruncDay('date'))
            .values('day')
            .annotate(total=Sum('amount'))
            .order_by('day')
        )

        category_data = (
            Transaction.objects.filter(wallet__user=user, type='EXPENSE')
            .values('category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        return Response({
            "daily_chart": daily_expenses,
            "category_chart": category_data
        })