from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'photo')