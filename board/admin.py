from django.contrib import admin

from .models import RequiredKeyword, ExcludedKeyword, Profile


admin.site.register(Profile)
admin.site.register(RequiredKeyword)
admin.site.register(ExcludedKeyword)
