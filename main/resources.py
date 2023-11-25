from import_export import resources

from main.models import Beneficiary

class BeneficiaryResource(resources.ModelResource):
    class Meta:
        model = Beneficiary