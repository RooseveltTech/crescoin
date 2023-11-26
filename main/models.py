import time
import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.

class Beneficiary(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, null=True, blank=True,
                                 related_name="beneficiary_owner")
    beneficiary = models.ForeignKey("core.User", on_delete=models.CASCADE, null=True, blank=True,
                                 related_name="beneficiary_receiver")
    amount = models.FloatField(null=True, blank=True, default=0.0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "BENEFICIARY"
        verbose_name_plural = "BENEFICIARIES"

    @classmethod
    def create_single_multiple_beneficiary(cls, user, all_beneficiary):
        for beneficiary in all_beneficiary:
            beneficiary_tag = beneficiary["beneficiary_tag"]
            beneficiary_user = User.objects.filter(user_tag=beneficiary_tag).last()
            create_beneficiary_instance = Beneficiary.objects.create(
                    user=user,
                    beneficiary=beneficiary_user
                )    
            
class CurrencyExchangeTable(models.Model):
    short_code = models.CharField(max_length=255, blank=False, null=True)
    currency_name = models.CharField(max_length=255, blank=False, null=True)
    currency_rate = models.FloatField(null=True, blank=True, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "CURRENCY VALUE"
        verbose_name_plural = "CURRENCY VALUES"

class Transaction(models.Model):
    SUCCESSFUL = "SUCCESSFUL"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    REVERSED = "REVERSED"

    TRANSACTION_STATUS_CHOICES = [
        (SUCCESSFUL, "SUCCESSFUL"),
        (PENDING, "PENDING"),
        (IN_PROGRESS, "IN_PROGRESS"),
        (FAILED, "FAILED"),
        (REVERSED, "REVERSED"),
    ]
    TRANSACTION_TYPES = (
        ("WITHDRAWAL", "WITHDRAWAL"),
        ("REVERSAL", "REVERSAL"),
        ("BUDDY", "BUDDY"),
        ("FUND_WALLET", "FUND_WALLET"),

    )


    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    # User
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="transactions")
    user_email = models.EmailField(null=True, blank=True)

    amount = models.FloatField(null=True, blank=True, validators=[
        MinValueValidator(0.0)])
    commission = models.FloatField(null=True, blank=True, validators=[
        MinValueValidator(0.0)])
    # --------------------balances-------------------------
    balance_before = models.FloatField(null=True, blank=True)
    balance_after = models.FloatField(null=True, blank=True)
    # ------------------------------------------------------
    status = models.CharField(max_length=150, choices=TRANSACTION_STATUS_CHOICES, default="SUCCESSFUL", null=True,
                            blank=True)

    transaction_type = models.CharField(
        max_length=50, choices=TRANSACTION_TYPES, default="FUND_WALLET")
    # reference
    transaction_ref = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    external_to_internal_ref = models.CharField(
        max_length=500, null=True, blank=True)
    internal_to_internal_ref = models.CharField(
        max_length=500, null=True, blank=True)
    internal_to_external_ref = models.CharField(
        max_length=500, null=True, blank=True)
    fund_internal_buddy_ref = models.CharField(
        max_length=250, null=True, blank=True)
    provider_fee = models.FloatField(null=True, blank=True)
    total_amount_sent_out = models.FloatField(null=True, blank=True)
    total_amount_received = models.FloatField(null=True, blank=True)
    is_reversed = models.BooleanField(default=False)

    # For BANK_TRANSFER transactions
    beneficiary_tag = models.CharField(
        max_length=250, null=True, blank=True)
    beneficiary_name = models.CharField(
        max_length=250, null=True, blank=True)
    source_tag = models.CharField(
        max_length=250, null=True, blank=True)
    source_name = models.CharField(
        max_length=250, null=True, blank=True)
    total_amount_resolved = models.FloatField(null=True, blank=True)

    narration = models.CharField(max_length=1000, null=True, blank=True)
    date_credited = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["-date_created"]
        verbose_name = "TRANSACTION"
        verbose_name_plural = "TRANSACTIONS"

    def __str__(self):
        return f"trnx - {self.id}"

    @classmethod
    def create_unique_transaction_ref(cls, suffix):
        epoch = int(time.time())
        ref = f"{suffix}-{str(epoch)[-10:]}-{uuid.uuid4()}"
        return ref
    
class DebitCreditRecordOnAccount(models.Model):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    REVERSAL = "REVERSAL"

    TRANS_TYPE_DEBIT_OR_CREDIT_CHOICES = [
        (CREDIT, "CREDIT"),
        (DEBIT, "DEBIT"),
        (REVERSAL, "REVERSAL"),
    ]

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="debit_credit_user")
    entry = models.CharField(
        max_length=200, choices=TRANS_TYPE_DEBIT_OR_CREDIT_CHOICES)
    balance_before = models.FloatField(default=0.00)
    balance_after = models.FloatField(default=0.00)
    amount = models.FloatField(validators=[MinValueValidator(0.0)])
    type_of_trans = models.CharField(max_length=200, null=True, blank=True)
    transaction_instance_id = models.CharField(
        max_length=400, null=True, blank=True)
    date_credited = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entry.lower()}"

    class Meta:
        verbose_name = "DEBIT CREDIT RECORD"
        verbose_name_plural = "DEBIT CREDIT RECORDS"