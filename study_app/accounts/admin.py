from django.contrib import admin
from .models import CustomUser, Connection

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Connection)
