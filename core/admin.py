from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from core.models import User

# Register your models here.
class UserResource(resources.ModelResource):
    class Meta:
        model = User


class UserResourceAdmin(ImportExportModelAdmin):
    resource_class = UserResource

    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]
    
admin.site.register(User, UserResourceAdmin)