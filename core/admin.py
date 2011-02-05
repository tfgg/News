from django.contrib import admin

import models

class NarrativeAdmin(admin.ModelAdmin):
  prepopulated_fields = {'slug': ('title',),}


admin.site.register(models.Narrative, NarrativeAdmin)
admin.site.register(models.GuardianSearch)

