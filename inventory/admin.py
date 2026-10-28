from django.contrib import admin
from .models import Organization, OrganizationSettings, Product


admin.site.register(Organization)
admin.site.register(OrganizationSettings)
admin.site.register(Product)