from django.contrib import admin
from .models import Film , Acteur

admin.site.register(Film)

@admin.register(Acteur)
class ActeurAdmin(admin.ModelAdmin):
    list_display = ['nom','role','photo']
    list_filter = ['nom','role']
    search_fields = ['nom', 'role']



