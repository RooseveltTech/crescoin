from django.db import transaction
from rest_framework import serializers

from main.models import Beneficiary
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
                {"beneficiary_data": f"{beneficiary_tag} does not exist"}
            )
        beneficiary = Beneficiary.objects.filter(beneficiary__user_tag=beneficiary_tag, user=user, is_deleted=False).last()
        if beneficiary:
            raise serializers.ValidationError(
                {"beneficiary_data": f"{beneficiary_tag} already exist"}
            )
        return attrs

class CreateBeneficiarySerializer(serializers.Serializer):
    beneficiary_data = serializers.ListSerializer(child=BeneficiarySerializer())

    def validate(self, attrs):
        user=self.context["request_user"]
        if len(attrs["beneficiary_data"]) < 1:
            raise serializers.ValidationError(
                {"beneficiary_data": "beneficiary_data cannot be empty"}
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
                {"beneficiary_data": "beneficiary does not exist"}
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
                {"beneficiary_data": "beneficiary_data cannot be empty"}
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
                    {"transaction_pin": "transaction_pin must be 4 digits"}
                )
            if transaction_pin != transaction_pin_retry:
                raise serializers.ValidationError(
                    {"transaction_pin": "transaction_pin and transaction_pin_retry does not match"}
                )
            else:
                pin_created = User.create_transaction_pin(
                        user=request_user, transaction_pin=transaction_pin
                    )
        else:
            raise serializers.ValidationError(
                {"error_code": "14", "transaction_pin": "transaction_pin must be numeric"}
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
                        "error_code": "14",
                        "transaction_pin": "user old transaction_pin is incorrect!"
                    }
                )
            if transaction_pin != repeat_transaction_pin:
                raise serializers.ValidationError(
                    {
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
                            "message": "Something went wrong, please try again!"
                        }
                    )
        else:
            raise serializers.ValidationError(
                {"error_code": "14", "message": "You must supply an integer"}
            )
        return attrs
    
     
        
        
  