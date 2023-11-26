from django.db import transaction
from rest_framework import serializers

from main.models import Beneficiary, CurrencyExchangeTable, DebitCreditRecordOnAccount, MarketPlace, Transaction
from django.contrib.auth import get_user_model
User = get_user_model()

class AllBeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = [
            "id",
            "beneficiary__user_tag"
        ]

class BeneficiarySerializer(serializers.Serializer):
    beneficiary_tag = serializers.CharField(required=True)
    def self(self, attrs):
        user=self.context["request_user"]
        beneficiary_tag = attrs.get("beneficiary_tag")
        beneficiary_user = User.objects.filter(user_tag=beneficiary_tag).last()
        if not beneficiary_user:
            raise serializers.ValidationError(

                {"error": True, "message": f"{beneficiary_tag} does not exist"}
            )
        beneficiary = Beneficiary.objects.filter(beneficiary__user_tag=beneficiary_tag, user=user, is_deleted=False).last()
        if beneficiary:
            raise serializers.ValidationError(
                {"error": True, "message": f"{beneficiary_tag} already exist"}
            )
        return attrs

class CreateBeneficiarySerializer(serializers.Serializer):
    beneficiary_data = serializers.ListSerializer(child=BeneficiarySerializer())

    def validate(self, attrs):
        user=self.context["request_user"]
        if len(attrs["beneficiary_data"]) < 1:
            raise serializers.ValidationError(
                {"error": True, "message": "beneficiary_data cannot be empty"}
            )
        return attrs
    
class BeneficiaryIdSerializer(serializers.Serializer):
    beneficiary_tag = serializers.CharField(required=True)
    def validate(self, attrs):
        user=self.context["request_user"]
        beneficiary_tag = attrs.get("beneficiary_tag")
        beneficiary = Beneficiary.objects.filter(beneficiary__user_tag=beneficiary_tag, user=user, is_deleted=False).last()
        if not beneficiary:
            raise serializers.ValidationError(
                {"error": True, "message": "beneficiary does not exist"}
            )
        beneficiary.is_deleted = True
        beneficiary.save()
        return attrs
    
class DeleteBeneficiarySerializer(serializers.Serializer):
    beneficiary_data = serializers.ListSerializer(child=BeneficiaryIdSerializer())

    def validate(self, attrs):
        user=self.context["request_user"]
        if len(attrs["beneficiary_data"]) < 1:
            raise serializers.ValidationError(
                {"error": True, "message": "beneficiary_data cannot be empty"}
            )
        return attrs
    
class CreateTransactionPinSerializer(serializers.Serializer):
    transaction_pin = serializers.CharField(required=True)
    transaction_pin_retry = serializers.CharField(required=True)

    def validate(self, attrs):
        request_user = self.context.get('request_user')
        if attrs["transaction_pin"].isnumeric():
            transaction_pin = attrs.get("transaction_pin")
            transaction_pin_retry = attrs.get("transaction_pin_retry")
            if len(transaction_pin) != 4:
                raise serializers.ValidationError(
                    {"error": True, "message": "transaction_pin must be 4 digits"}
                )
            if transaction_pin != transaction_pin_retry:
                raise serializers.ValidationError(
                    {"error": True, "message": "transaction_pin and transaction_pin_retry does not match"}
                )
            else:
                pin_created = User.create_transaction_pin(
                        user=request_user, transaction_pin=transaction_pin
                    )
        else:
            raise serializers.ValidationError(
                {"error": True, "transaction_pin": "transaction_pin must be numeric"}
            )
        
        return attrs
class ChangeTransactionPinSerializer(serializers.Serializer):
    old_transaction_pin = serializers.CharField(required=True)
    transaction_pin = serializers.CharField(required=True)
    repeat_transaction_pin = serializers.CharField(required=True)

    def validate(self, attrs):
        old_transaction_pin = attrs.get("old_transaction_pin")
        transaction_pin = attrs.get("transaction_pin")
        repeat_transaction_pin = attrs.get("repeat_transaction_pin")
        request_user = self.context.get('request_user')
        
        if transaction_pin.isnumeric():
            check_transaction_pin = User.check_transaction_pin(user=request_user, transaction_pin=old_transaction_pin)
            if not check_transaction_pin:
                raise serializers.ValidationError(
                    {
                        "error": True,
                        "message": "user old transaction_pin is incorrect!"
                    }
                )
            if transaction_pin != repeat_transaction_pin:
                raise serializers.ValidationError(
                    {
                        "error": True,
                        'message': "transaction_pin and repeat_transaction_pin must be equal!"
                    }
            )
            else:
                try:
                    with transaction.atomic():
                        # remove transaction_pin
                        request_user.transaction_pin = None
                        request_user.save()
                        update_user_transaction_pin = User.create_transaction_pin(request_user, transaction_pin)
                except:
                    return serializers.ValidationError(
                        {
                            "error": True,
                            "message": "Something went wrong, please try again!"
                        }
                    )
        else:
            raise serializers.ValidationError(
                {"error": True, "message": "You must supply an integer"}
            )
        return attrs
    
class GetExchangeRateSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True, min_value=1)
    currency_from = serializers.CharField(required=True)
    currency_to = serializers.CharField(required=True)
    def validate(self, attrs):
        currency_from = attrs.get("currency_from")
        currency_to = attrs.get("currency_to")
        amount = attrs.get("amount")
        if len(currency_from) != 3:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "currency_from must be three letter code"
                }
            )
        get_currency_from = CurrencyExchangeTable.objects.filter(short_code=currency_from, currency_rate__gt=0).last()
        if not get_currency_from:
            raise serializers.ValidationError(
                {
                    "error": True, "message": f"{currency_from} does not exist"
                }
            )
        if len(currency_to) != 3:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "currency_to must be three letter code"
                }
            )
        get_currency_to = CurrencyExchangeTable.objects.filter(short_code=currency_to, currency_rate__gt=0).last()
        if not get_currency_to:
            raise serializers.ValidationError(
                {
                    "error": True, "message": f"{currency_to} does not exist"
                }
            )
        if currency_from == currency_to:
            raise serializers.ValidationError(
                {
                    "error": True, "message": f"{currency_from} and {currency_to} cannot be be the same"
                }
            )
        
        base_amount = 1 / get_currency_from.currency_rate
        exchange_rate = round(base_amount * get_currency_to.currency_rate, 2) + (0.1 * round(base_amount * get_currency_to.currency_rate, 2))
        attrs["exchange_rate_from"] = 1
        attrs["exchange_rate_to"] = exchange_rate * amount
        return attrs
    
class GetExchangeForFundingAccountSerializer(serializers.Serializer):
    def validate(self, attrs):
        currency_from = self.context.get("currency_from")
        if not currency_from:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "currency_from is required and is a parameter"
                }
            )
        if len(currency_from) != 3:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "currency_from must be three letter code"
                }
            )
        get_currency_from = CurrencyExchangeTable.objects.filter(short_code=currency_from, currency_rate__gt=0).last()
        if not get_currency_from:
            raise serializers.ValidationError(
                {
                    "error": True, "message": f"{currency_from} does not exist"
                }
            )
        
        get_currency_to = CurrencyExchangeTable.objects.filter(short_code="USD").last()
        base_amount = 1 / get_currency_from.currency_rate
        exchange_rate = round(base_amount * get_currency_to.currency_rate, 2) - (0.1 * round(base_amount * get_currency_to.currency_rate, 2))
        attrs["message"] = f"you account will be funded with {exchange_rate} CRC"
        attrs["exchange_rate"] = exchange_rate
        return attrs


class FundAccountSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True, min_value=1)
    currency_from = serializers.CharField(required=True)
    transaction_pin = serializers.CharField(required=True)
    def validate(self, attrs):
        transaction_pin = attrs.get("transaction_pin")
        request_user = self.context.get('request_user')
        amount = attrs.get("amount")
        currency_from = attrs.get("currency_from")

        check_transaction_pin = User.check_transaction_pin(user=request_user, transaction_pin=transaction_pin)
        if not check_transaction_pin:
            raise serializers.ValidationError(
                {
                    "error": True,
                    "message": "transaction_pin is incorrect!"
                }
            )
        if len(currency_from) != 3:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "currency_from must be three letter code"
                }
            )
        get_currency_from = CurrencyExchangeTable.objects.filter(short_code=currency_from, currency_rate__gt=0).last()
        if not get_currency_from:
            raise serializers.ValidationError(
                {
                    "error": True, "message": f"{currency_from} does not exist"
                }
            )
        get_currency_to = CurrencyExchangeTable.objects.filter(short_code="USD").last()
        base_amount = 1 / get_currency_from.currency_rate
        exchange_rate = round(base_amount * get_currency_to.currency_rate, 2) - (0.2 * round(base_amount * get_currency_to.currency_rate, 2))
        amount_to = exchange_rate * amount
        if amount_to < 1:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "you must fund your account with at least 1 CRC"
                }
            )
        
        User.fund_account(user=request_user, amount=amount_to)
        attrs["amount_from"] = amount
        attrs["currency_from"] = get_currency_from.short_code
        attrs["exchange_rate"] = exchange_rate
        attrs["amount_to"] = amount_to
        attrs["currency_to"] = "CRC"
        attrs["message"] = f"you account has been funded with {amount_to} CRC"
        return attrs
    
class SendMoneySerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True, min_value=1)
    receiver_tag = serializers.CharField(required=True)
    transaction_pin = serializers.CharField(required=True)
    narration = serializers.CharField(required=True)
    def validate(self, attrs):
        transaction_pin = attrs.get("transaction_pin")
        request_user = self.context.get('request_user')
        amount = attrs.get("amount")
        receiver_tag = attrs.get("receiver_tag")
        narration = attrs.get("narration")

        check_transaction_pin = User.check_transaction_pin(user=request_user, transaction_pin=transaction_pin)
        if not check_transaction_pin:
            raise serializers.ValidationError(
                {
                    "error": True,
                    "message": "transaction_pin is incorrect!"
                }
            )
    
        get_receiver = User.objects.filter(user_tag=receiver_tag).last()
        if not get_receiver:
            raise serializers.ValidationError(
                {
                    "error": True, "message": f"{get_receiver} does not exist"
                }
            )
        transaction = Transaction.objects.create(user=request_user,
                                                user_email=request_user.email,
                                                amount=amount,
                                                total_amount_sent_out=amount,
                                                beneficiary_tag=receiver_tag,
                                                beneficiary_name=receiver_tag.full_name,
                                                narration=narration,
                                                source_name=request_user.full_name,
                                                source_tag=request_user.user_tag,
                                                transaction_type="BUDDY",
                                                status="FAILED",
                                                )
        # Charge wallet
        debit_wallet = User.deduct_balance(
            user=request_user, amount=amount)

        if debit_wallet.get("succeeded") is True:
            reference = Transaction.create_unique_transaction_ref(
                        suffix="BUDDY")
            fund_buddy_reference = Transaction.create_unique_transaction_ref(
                        suffix="BUDDY")
            wallet_instance = debit_wallet.get("wallet")
            balance_after = debit_wallet.get("amount_after")
            balance_before = debit_wallet.get("amount_before")
            transaction.balance_before = balance_before
            transaction.internal_to_internal_ref = reference
            transaction.balance_after = balance_after
            transaction.fund_internal_buddy_ref = fund_buddy_reference
            transaction.status = "SUCCESSFUL"
            transaction.save()

            debit_record = DebitCreditRecordOnAccount.objects.create(
                        user=request_user,
                        entry="DEBIT",
                        wallet=wallet_instance,
                        balance_before=balance_before,
                        amount=amount,
                        balance_after=balance_after,
                        transaction_instance_id=transaction.id
                    )
            User.fund_account(user=get_receiver, amount=amount)
        else:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "insufficient funds!"
                }
            )
        return attrs
  
class UserDashBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =[
            "email",
            "phone_number", 
            "first_name", 
            "last_name", 
            "country", 
            "passport_number", 
            "passport_expiry_date", 
            "passport_issue_date", 
            "driving_license_number", 
            "driving_license_expiry_date", 
            "driving_license_issue_date", 
            "user_tag", 
            "balance"
        ]

class UserTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"

class DebitCreditHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DebitCreditRecordOnAccount
        fields = "__all__"

class WithdrawalSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True, min_value=1)
    withdrawal_type = serializers.CharField(required=True)
    withdrawal_operator = serializers.CharField(required=True)
    transaction_pin = serializers.CharField(required=True)
    currency_code = serializers.CharField(required=True)
    narration = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

    def validate(self, attrs):
        transaction_pin = attrs.get("transaction_pin")
        request_user = self.context.get('request_user')
        amount = attrs.get("amount")
        withdrawal_type = attrs.get("withdrawal_type")
        withdrawal_operator = attrs.get("withdrawal_operator")
        narration = attrs.get("narration")
        currency_code = attrs.get("currency_code")

        if len(currency_code) != 3:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "currency_code must be three letter code"
                }
            )
        get_currency_code = CurrencyExchangeTable.objects.filter(short_code=currency_code, currency_rate__gt=0).last()
        if not get_currency_code:
            raise serializers.ValidationError(
                {
                    "error": True, "message": f"{currency_code} does not exist"
                }
            )
        get_currency_to = CurrencyExchangeTable.objects.filter(short_code="USD").last()
        base_amount = 1 / get_currency_code.currency_rate
        exchange_rate = round(base_amount * get_currency_to.currency_rate, 2) - (0.3 * round(base_amount * get_currency_to.currency_rate, 2))
        amount_to = exchange_rate * amount

        check_transaction_pin = User.check_transaction_pin(user=request_user, transaction_pin=transaction_pin)
        if not check_transaction_pin:
            raise serializers.ValidationError(
                {
                    "error": True,
                    "message": "transaction_pin is incorrect!"
                }
            )
        transaction = Transaction.objects.create(user=request_user,
                                                user_email=request_user.email,
                                                amount=amount,
                                                total_amount_sent_out=amount,
                                                narration=narration,
                                                source_name=request_user.full_name,
                                                source_tag=request_user.user_tag,
                                                transaction_type="WITHDRAWAL",
                                                status="FAILED",
                                                withdrawal_type=withdrawal_type,
                                                withdrawal_operator=withdrawal_operator
                                                )
        # Charge wallet
        debit_wallet = User.deduct_balance(
            user=request_user, amount=amount)

        if debit_wallet.get("succeeded") is True:
            reference = Transaction.create_unique_transaction_ref(
                        suffix="WTD")
            wallet_instance = debit_wallet.get("wallet")
            balance_after = debit_wallet.get("amount_after")
            balance_before = debit_wallet.get("amount_before")
            transaction.balance_before = balance_before
            transaction.internal_to_external_ref = reference
            transaction.balance_after = balance_after
            transaction.status = "SUCCESSFUL"
            transaction.save()

            debit_record = DebitCreditRecordOnAccount.objects.create(
                        user=request_user,
                        entry="DEBIT",
                        wallet=wallet_instance,
                        balance_before=balance_before,
                        amount=amount,
                        balance_after=balance_after,
                        transaction_instance_id=transaction.id
                    )
        else:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "insufficient funds!"
                }
            )
        attrs["amount_from"] = amount
        attrs["currency_from"] = "CRC"
        attrs["currency_to"] = currency_code
        attrs["exchange_rate"] = exchange_rate
        attrs["amount_to"] = amount_to
        attrs["message"] = f"you account have withdrawn {currency_code} {amount_to} successfully"
        return attrs
    
class CreateP2PSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True)
    currency_from = serializers.CharField(required=True)
    currency_to = serializers.CharField(required=True)
    def validate(self, attrs):
        currency_from = attrs.get("currency_from")
        currency_to = attrs.get("currency_to")
        amount = attrs.get("amount")
        phone_number = attrs.get("phone_number")
        request_user = self.context.get('request_user')
        if len(currency_from) != 3:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "currency_from must be three letter code"
                }
            )
        get_currency_from = CurrencyExchangeTable.objects.filter(short_code=currency_from).last()
        if not get_currency_from:
            raise serializers.ValidationError(
                {
                    "error": True, "message": f"{currency_from} does not exist"
                }
            )
        if len(currency_to) != 3:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "currency_to must be three letter code"
                }
            )
        get_currency_to = CurrencyExchangeTable.objects.filter(short_code=currency_to).last()
        if not get_currency_to:
            raise serializers.ValidationError(
                {
                    "error": True, "message": f"{currency_to} does not exist"
                }
            )
        if currency_from == currency_to:
            raise serializers.ValidationError(
                {
                    "error": True, "message": f"{currency_from} and {currency_to} cannot be be the same"
                }
            )
        MarketPlace.objects.create(
            user = request_user,
            amount = amount,
            currency_from = currency_from,
            currency_to = currency_to,
            phone_number = phone_number
        )
        return attrs
    
class DeleteP2PSerializer(serializers.Serializer):
    def validate(self, attrs):
        request_user = self.context.get('request_user')
        market_place_id = self.context.get('market_place_id')
        get_market_place = MarketPlace.objects.filter(id=market_place_id, user=request_user).last()
        if not get_market_place:
            raise serializers.ValidationError(
                {
                    "error": True, "message": "market place does not exist"
                }
            )
        get_market_place.is_deleted = True
        get_market_place.save()
        return attrs

class GetP2PSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketPlace
        fields = "__all__"