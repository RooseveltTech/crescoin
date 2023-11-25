from django.db import models
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