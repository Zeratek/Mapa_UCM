from django.shortcuts import render, redirect
from django.http import JsonResponse
from MapAdmin.views import listaOrdenadaEstructuras, haversine, dijkstra
from MapAdmin.models import Punto,Linea,Edificacion,EstructuraEdificacion,EntradasEdificacion
from django.db.models.functions import Cast,Coalesce
from django.db.models import FloatField,Value,Q,F,Count,IntegerField
# Create your views here.

def index(request):
    estructurasMapa = listaOrdenadaEstructuras()
    pisos = list(Edificacion.objects.values_list('piso', flat=True).distinct())
    listaEdificaciones = list(Edificacion.objects.all().annotate(nombre_fk = Coalesce('pertenece__nombre', Value('-'))).values('id','nombre','piso','nombre_fk','informacion'))
    puntosMapa = list(Punto.objects.annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('id', 'lat_float', 'lon_float'))
    lineasMapa = list(Linea.objects.annotate(punto_inicio_lat_float=Cast('punto_inicio__lat', FloatField())).annotate(punto_inicio_lon_float=Cast('punto_inicio__lon', FloatField())).annotate(punto_fin_lat_float=Cast('punto_fin__lat', FloatField())).annotate(punto_fin_lon_float=Cast('punto_fin__lon', FloatField())).values('id', 'punto_inicio_lat_float', 'punto_inicio_lon_float', 'punto_fin_lat_float', 'punto_fin_lon_float'))
    #print(obtener_conexiones())
    return render(request, 'index.html',{'puntosMapa':puntosMapa,'lineasMapa':lineasMapa,'estructurasMapa':estructurasMapa,'pisos':pisos,'listaEdificaciones':listaEdificaciones})

def building_info(request, buildingID):
    buildingInfo = []#list(Buildings.objects.filter(id = buildingID).values('id','name'))
    print(buildingInfo)
    return JsonResponse(buildingInfo, safe=False)

#funcion que calcula el camino entre 2 puntos
def calcularCamino(request,p_lat,p_lon,e_id):
    initLat = float(p_lat)
    initLon = float(p_lon)
    puntoCercano,distInicial=puntoMasCercano(initLat,initLon)
    entradas = list(EntradasEdificacion.objects.filter(edificio__id = e_id).values('punto_camino__id'))
    #print(puntoCercano)
    graph = obtener_conexiones()
    #print(entradas[0]['punto_camino__id'])
    shortest_distance=-1
    shortest_path = {}
    #print(len(entradas) - 1)
    if len(entradas)>0:
        for i in range(len(entradas)):
            id_entrada = entradas[i]['punto_camino__id']
            #print(id_entrada)
            #aux_shortest_distance, aux_shortest_path = dijkstra(graph, str(puntoCercano), str(entradas[i]['punto_camino__id']))
            aux_shortest_distance, aux_shortest_path = dijkstra(graph, str(puntoCercano), str(id_entrada))
            #print(f"Distancia: {aux_shortest_distance}")
            if shortest_distance == -1:
                shortest_distance = aux_shortest_distance
                shortest_path = aux_shortest_path
            else:
                if aux_shortest_distance < shortest_distance:
                    shortest_distance = aux_shortest_distance
                    shortest_path = aux_shortest_path
                else:
                    pass
            #print(f"Distancia más corta: {shortest_distance}")
            #print(f"Camino más corto: {shortest_path}")
    else:
        #print("no tiene entradas")
        return JsonResponse([None,None], safe=False)
    listaPuntos=[]
    listaLineas=[]
    obj3 = Linea.objects.filter(punto_inicio=1).values()
    #print(graph)
    for i in range(len(shortest_path) - 1):
        obj1 = Punto.objects.filter(id=shortest_path[i]).annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('id', 'lat_float', 'lon_float')[0]
        obj2 = Punto.objects.filter(id=shortest_path[i+1]).annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('id', 'lat_float', 'lon_float')[0]
        if obj1 not in listaPuntos:
            listaPuntos.append(obj1)
        if obj2 not in listaPuntos:
            listaPuntos.append(obj2)
        obj3 = Linea.objects.filter(punto_inicio=shortest_path[i],punto_fin=shortest_path[i+1]).annotate(punto_inicio_lat_float=Cast('punto_inicio__lat', FloatField())).annotate(punto_inicio_lon_float=Cast('punto_inicio__lon', FloatField())).annotate(punto_fin_lat_float=Cast('punto_fin__lat', FloatField())).annotate(punto_fin_lon_float=Cast('punto_fin__lon', FloatField())).values('id', 'punto_inicio_lat_float', 'punto_inicio_lon_float', 'punto_fin_lat_float', 'punto_fin_lon_float')
        if obj3:
            listaLineas.append(obj3[0])
        else:
            obj3 = Linea.objects.filter(punto_inicio=shortest_path[i+1],punto_fin=shortest_path[i]).annotate(punto_inicio_lat_float=Cast('punto_inicio__lat', FloatField())).annotate(punto_inicio_lon_float=Cast('punto_inicio__lon', FloatField())).annotate(punto_fin_lat_float=Cast('punto_fin__lat', FloatField())).annotate(punto_fin_lon_float=Cast('punto_fin__lon', FloatField())).values('id', 'punto_inicio_lat_float', 'punto_inicio_lon_float', 'punto_fin_lat_float', 'punto_fin_lon_float')
            listaLineas.append(obj3[0])
        #print(obj3)
        #listaLineas.append(obj3)
        #print(shortest_path[i])
        #print(shortest_path[i+1])
    #print("-------------------")
    #print(listaPuntos)
    #print("-------------------")
    #print(listaLineas)
    
    return JsonResponse([listaPuntos,listaLineas,shortest_distance+distInicial], safe=False)

def puntoMasCercano(lat,lon):
    puntos = Punto.objects.annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('id', 'lat_float', 'lon_float')
    #print(puntos)
    masCercano = 0
    disMasCercano = -1
    #print('buscando punto mas cercano')
    for i in puntos:
        finalLat = i['lat_float']
        finalLon = i['lon_float']
        dist = haversine(lat,lon,finalLat,finalLon)
        #print(dist)
        if dist < disMasCercano or disMasCercano == -1:
            disMasCercano=dist
            masCercano = i['id']
        #print(i['lat_float'])
        #print(i['lon_float'])
    #print('el mas cercano es: ')
    #print(masCercano)
    #print(disMasCercano)
    return masCercano,disMasCercano

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