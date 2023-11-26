import time
from django.db import models, transaction
from django.db.models import F
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.hashers import check_password, make_password
import uuid
import json, os

# Create your model(s) here.

VERIFICATION_TYPE = [
        ("PASSPORT", "PASSPORT"),
        ("DRIVING_LICENSE", "DRIVING_LICENSE"),
        ("NULL", "NULL")
    ]

class BaseModel(models.Model):
    """Base model for reuse.
    Args:
        models (Model): Django's model class.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_('date created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date updated'), auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModel):
    """User model."""

    username = None
    email = models.EmailField(unique=True, )
    phone_number = models.CharField(max_length=255, blank=False, null=True, unique=True)
    first_name = models.CharField(max_length=255, blank=False, null=True)
    last_name = models.CharField(max_length=255, blank=False, null=True)
    country = models.CharField(max_length=255, blank=False, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    user_is_active = models.BooleanField(default=False)
    user_is_suspended = models.BooleanField(default=False)
    user_is_deleted = models.BooleanField(default=False)
    transaction_pin = models.CharField(max_length=255, null=True, blank=True, editable=False)
    passport_number = models.CharField(max_length=255, blank=False, null=True)
    passport_expiry_date = models.DateField(blank=False, null=True)
    passport_issue_date = models.DateField(blank=False, null=True)
    driving_license_number = models.CharField(max_length=255, blank=False, null=True)
    driving_license_expiry_date = models.DateField(blank=False, null=True)
    driving_license_issue_date = models.DateField(blank=False, null=True)
    user_tag = models.CharField(max_length=255, blank=False, null=True, unique=True)
    verification_type = models.CharField(max_length=200, choices=VERIFICATION_TYPE, default="NULL")
    balance = models.FloatField(default=0.0, validators=[
        MinValueValidator(0.0)])
    previous_balance = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self) -> str:
        return str(self.email)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'USER PROFILE'
        verbose_name_plural = 'USER PROFILES'

    def save(self, *args, **kwargs):

        try:
            if self.pk:
                self.previous_balance = self.__original_amount

            return super(User, self).save(*args, **kwargs)
        except Exception as err:
            raise Exception(f"{err}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_amount = self.balance

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def user_exist(cls, email):
        try:
            user = cls.objects.get(email=email)
        except cls.DoesNotExist:
            return None
        return user
    
    @staticmethod
    def create_transaction_pin(user, transaction_pin) -> bool:
        """
        Collect pin and hash it
        """
        if not user.transaction_pin:
            hashed_pin = make_password(transaction_pin)
            user.transaction_pin = hashed_pin
            user.save()
            return True
        else:
            return False
        
    @staticmethod
    def check_transaction_pin(user, transaction_pin) -> bool:
        """
        Check if entered pin is correct
        """
        return check_password(transaction_pin, user.transaction_pin)
    
    @classmethod
    def deduct_balance(cls, user, amount):
        with transaction.atomic():
            initial_balance = user.balance

            if 0 < amount <= initial_balance:
                user.balance = F('balance') - amount
                user.save()
                user.refresh_from_db()

                wallet_data = {
                    "succeeded": True,
                    "amount_before": initial_balance,
                    "amount_after": user.balance,
                    "wallet": user,
                }
                return wallet_data

            else:
                failed = {
                    "succeeded": False,
                    "amount_before": None,
                    "amount_after": None,
                    "wallet": user,
                }
                return failed
    
    @classmethod
    def fund_wallet(cls, request_user, amount):
        from main.models import DebitCreditRecordOnAccount, Transaction
        transaction_ref = Transaction.create_unique_transaction_ref
        with transaction.atomic():
            initial_transaction_record = Transaction.objects.create(
                user=request_user,
                external_to_internal_ref=transaction_ref,
                transaction_type="FUND_WALLET",
                narration="FUND WALLET",
                amount=amount
            )

            debit_credit_record = DebitCreditRecordOnAccount.objects.create(user=request_user,
                                                                            entry="CREDIT",
                                                                            amount=amount,
                                                                            transaction_instance_id=initial_transaction_record.id,
                                                                            date_credited=timezone.now()
                                                                            )

            # fund wallet
            wallet_instance = request_user
            previous_balance = wallet_instance.balance
            wallet_instance.balance = F(
                'balance') + initial_transaction_record.amount
            wallet_instance.save()

            wallet_instance.refresh_from_db()
            updated_balance = wallet_instance.balance

            debit_credit_record.wallet = wallet_instance
            debit_credit_record.balance_before = previous_balance
            debit_credit_record.balance_after = updated_balance
            debit_credit_record.save()

            initial_transaction_record.balance_before = previous_balance
            initial_transaction_record.balance_after = updated_balance
            initial_transaction_record.status = "SUCCESSFUL"
            initial_transaction_record.date_credited = timezone.now()
            initial_transaction_record.save()
            return True
        
    def username_exist(cls, username):
        try:
            username = cls.objects.get(username=username)
        except cls.DoesNotExist:
            return None
        return username