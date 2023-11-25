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
    

admin.site.register(Beneficiary, BeneficiaryResourceAdmin)