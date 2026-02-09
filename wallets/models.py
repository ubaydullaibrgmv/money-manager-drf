from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"

class Category(BaseModel):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Wallet(BaseModel):
    CURRENCY_CHOICES = [
        ('UZS', 'O‘zbek so‘mi'),
        ('USD', 'AQSH dollari'),
        ('EUR', 'Yevro'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='UZS')

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Transaction(BaseModel):
    TRANSACTION_TYPE = (
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPE)
    note = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            t_type = str(self.type).upper()
            if t_type == 'INCOME':
                self.wallet.balance += self.amount
            elif t_type == 'EXPENSE':
                if self.wallet.balance < self.amount:
                    raise ValidationError("Hamyonda mablag' yetarli emas!")
                self.wallet.balance -= self.amount
            self.wallet.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.type == 'INCOME':
            self.wallet.balance -= self.amount
        elif self.type == 'EXPENSE':
            self.wallet.balance += self.amount
        self.wallet.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.type}: {self.amount} | {self.wallet.name}"