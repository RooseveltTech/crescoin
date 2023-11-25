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

class CreateBeneficiarySerializer(serializers.Serializer):
    beneficiary_data = serializers.ListSerializer(child=BeneficiarySerializer())

    def validate(self, attrs):
        user=self.context["request_user"]
        if len(attrs["beneficiary_data"]) < 1:
            raise serializers.ValidationError(
                {"beneficiary_data": "beneficiary_data cannot be empty"}
            )
        all_beneficiary_tag = attrs.get("beneficiary_data")
        for beneficiary in all_beneficiary_tag:
            beneficiary_tag = beneficiary.get("beneficiary_tag")
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
    
class BeneficiaryIdSerializer(serializers.Serializer):
    beneficiary_tag = serializers.CharField(required=True)
    
class DeleteBeneficiarySerializer(serializers.Serializer):
    beneficiary_data = serializers.ListSerializer(child=BeneficiaryIdSerializer())

    def validate(self, attrs):
        user=self.context["request_user"]
        if len(attrs["beneficiary_data"]) < 1:
            raise serializers.ValidationError(
                {"beneficiary_data": "beneficiary_data cannot be empty"}
            )
        all_beneficiary_tag = attrs.get("beneficiary_data")
        for tag in all_beneficiary_tag:
            beneficiary_tag = tag.get("beneficiary_tag")
            beneficiary = Beneficiary.objects.filter(beneficiary__user_tag=beneficiary_tag, user=user, is_deleted=False).last()
            if not beneficiary:
                raise serializers.ValidationError(
                    {"beneficiary_data": "beneficiary does not exist"}
                )
            beneficiary_tag.is_deleted = True
            beneficiary_tag.save()
        return attrs