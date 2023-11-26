from import_export import resources

from main.models import Beneficiary, CurrencyExchangeTable, DebitCreditRecordOnAccount, Transaction

class BeneficiaryResource(resources.ModelResource):
    class Meta:
        model = Beneficiary

class CurrencyExchangeTableResource(resources.ModelResource):
    class Meta:
        model = CurrencyExchangeTable

class TransactionResource(resources.ModelResource):
    class Meta:
        model = Transaction

class DebitCreditRecordOnAccountResource(resources.ModelResource):
    class Meta:
        model = DebitCreditRecordOnAccount