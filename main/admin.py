from django.contrib import admin

# Register your models here.

from import_export.admin import ImportExportModelAdmin
from main.resources import *

class BeneficiaryResourceAdmin(ImportExportModelAdmin):
    resource_class = BeneficiaryResource
    search_fields = ["beneficiary__user_tag", "user__email"]
    list_filter = ["is_deleted"]   
    date_hierarchy = 'created_at'
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]
    
class CurrencyExchangeTableResourceAdmin(ImportExportModelAdmin):
    resource_class = CurrencyExchangeTableResource
    search_fields = ["currency_name", "short_code"]  
    date_hierarchy = 'created_at'
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]
    
class TransactionResourceAdmin(ImportExportModelAdmin):
    resource_class = TransactionResource
    search_fields = ["user__email", 
                     "beneficiary_tag", 
                     "source_tag", 
                     "transaction_ref", 
                     "fund_internal_buddy_ref",
                     "external_to_internal_ref",
                     "internal_to_internal_ref",
                     ""
                     ]  
    date_hierarchy = 'date_created'
    list_filter = ["transaction_type", "status"]
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]
    
class DebitCreditRecordOnAccountResourceAdmin(ImportExportModelAdmin):
    resource_class = DebitCreditRecordOnAccountResource
    search_fields = ["user__email"]  
    date_hierarchy = 'date_created'
    list_filter = ["entry"]
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]
    
class MarketPlaceResourceAdmin(ImportExportModelAdmin):
    resource_class = MarketPlaceResource  
    date_hierarchy = 'created_at'
    list_filter = ["is_deleted"]
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]
    

admin.site.register(Beneficiary, BeneficiaryResourceAdmin)
admin.site.register(CurrencyExchangeTable, CurrencyExchangeTableResourceAdmin)
admin.site.register(Transaction, TransactionResourceAdmin)
admin.site.register(DebitCreditRecordOnAccount, DebitCreditRecordOnAccountResourceAdmin)
admin.site.register(MarketPlace, MarketPlaceResourceAdmin)