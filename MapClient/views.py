from django.shortcuts import render, redirect
from django.http import JsonResponse
from MapAdmin.views import listaOrdenadaEstructuras
from MapAdmin.models import Punto,Linea,Edificacion,EstructuraEdificacion,EntradasEdificacion
from django.db.models.functions import Cast,Coalesce
from django.db.models import FloatField,Value,Q,F,Count,IntegerField
# Create your views here.

def index(request):
    estructurasMapa = listaOrdenadaEstructuras()
    pisos = list(Edificacion.objects.values_list('piso', flat=True).distinct())
    listaEdificaciones = list(Edificacion.objects.all().annotate(nombre_fk = Coalesce('pertenece__nombre', Value('-'))).values('id','nombre','piso','nombre_fk'))
    print(obtener_conexiones())
    return render(request, 'index.html',{'estructurasMapa':estructurasMapa,'pisos':pisos,'listaEdificaciones':listaEdificaciones})

def building_info(request, buildingID):
    buildingInfo = []#list(Buildings.objects.filter(id = buildingID).values('id','name'))
    print(buildingInfo)
    return JsonResponse(buildingInfo, safe=False)
def calcularCamino(request,p_lat,p_lon):
    print(type(p_lat))
    print(p_lon)
    return JsonResponse([], safe=False)

"""
def obtener_conexiones():
    conexiones = Linea.objects.values('punto_inicio').annotate(
        conexion=Cast('punto_fin', IntegerField()),
        peso=Cast('peso', IntegerField())
    ).values('punto_inicio', 'conexion', 'peso')

    graph = {}
    for conexion in conexiones:
        idpunto1 = str(conexion['punto_inicio'])
        conexion_id = str(conexion['conexion'])
        peso = conexion['peso']

        if idpunto1 not in graph:
            graph[idpunto1] = {}

        graph[idpunto1][conexion_id] = peso

    return graph
"""
def obtener_conexiones():
    conexiones = Linea.objects.values('punto_inicio', 'punto_fin', 'peso')

    graph = {}
    for conexion in conexiones:
        idpunto1 = str(conexion['punto_inicio'])
        idpunto2 = str(conexion['punto_fin'])
        peso = conexion['peso']

        if idpunto1 not in graph:
            graph[idpunto1] = {}

        if idpunto2 not in graph:
            graph[idpunto2] = {}

        graph[idpunto1][idpunto2] = peso
        graph[idpunto2][idpunto1] = peso

    return graph