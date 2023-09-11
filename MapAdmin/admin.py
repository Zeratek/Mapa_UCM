from django.contrib import admin
from .models import Punto,Linea,Edificacion,EstructuraEdificacion
# Register your models here.
admin.site.register(Punto)
admin.site.register(Linea)
admin.site.register(Edificacion)
admin.site.register(EstructuraEdificacion)