from django.shortcuts import render, redirect
from django.http import JsonResponse
from MapAdmin.views import listaOrdenadaEstructuras
from MapAdmin.models import Punto,Linea,Edificacion,EstructuraEdificacion,EntradasEdificacion
from django.db.models.functions import Cast,Coalesce
from django.db.models import FloatField,Value,Q,F,Count,IntegerField
from dijkstar import Graph, find_path
from haversine import haversine
# Create your views here.
#funcion que muestra el mapa de usuario
def index(request):
    estructurasMapa = listaOrdenadaEstructuras()
    pisos = list(Edificacion.objects.values_list('piso', flat=True).distinct())
    listaEstructurasEdificaciones = EstructuraEdificacion.objects.values('edificacion').distinct()
    listaEdificaciones = list(Edificacion.objects.filter(id__in=listaEstructurasEdificaciones).annotate(nombre_fk = Coalesce('pertenece__nombre', Value('-'))).values('id','nombre','piso','nombre_fk','informacion'))
    puntosMapa = list(Punto.objects.annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('id', 'lat_float', 'lon_float'))
    lineasMapa = list(Linea.objects.annotate(punto_inicio_lat_float=Cast('punto_inicio__lat', FloatField())).annotate(punto_inicio_lon_float=Cast('punto_inicio__lon', FloatField())).annotate(punto_fin_lat_float=Cast('punto_fin__lat', FloatField())).annotate(punto_fin_lon_float=Cast('punto_fin__lon', FloatField())).values('id', 'punto_inicio_lat_float', 'punto_inicio_lon_float', 'punto_fin_lat_float', 'punto_fin_lon_float'))
    #print(obtener_conexiones())
    return render(request, 'index.html',{'puntosMapa':puntosMapa,'lineasMapa':lineasMapa,'estructurasMapa':estructurasMapa,'pisos':pisos,'listaEdificaciones':listaEdificaciones})


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
    shortest_path = []
    #print(len(entradas) - 1)
    if len(entradas)>0:
        for i in range(len(entradas)):
            id_entrada = entradas[i]['punto_camino__id']
            if id_entrada == puntoCercano:
                mismoPunto =  list(Punto.objects.filter(id=id_entrada).annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('id', 'lat_float', 'lon_float'))
                return JsonResponse([mismoPunto,[],round(distInicial,1)], safe=False)
            try:
                paths = find_path(graph, puntoCercano, id_entrada)
            except:
                return JsonResponse([mismoPunto,[],round(distInicial,1)], safe=False)
            aux_shortest_path = paths.nodes
            aux_shortest_distance = find_path(graph, puntoCercano, id_entrada).total_cost
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
        #print(shortest_path)
        if not shortest_path:
            return JsonResponse([None,None], safe=False)
    else:
        #print("no tiene entradas")
        return JsonResponse([None,None], safe=False)
    listaPuntos=[]
    listaLineas=[]
    #obj3 = Linea.objects.filter(punto_inicio=1).values()
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
    total_distance = shortest_distance+distInicial
    #print(total_distance)
    total_distance = round(total_distance,1)
    return JsonResponse([listaPuntos,listaLineas,total_distance], safe=False)

#funcion que obtiene el punto mas cercano
def puntoMasCercano(lat,lon):
    puntos = Punto.objects.annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('id', 'lat_float', 'lon_float')
    #print(puntos)
    masCercano = 0
    disMasCercano = -1
    #print('buscando punto mas cercano')
    for i in puntos:
        finalLat = i['lat_float']
        finalLon = i['lon_float']
        initDist = haversine((lat,lon),(finalLat,finalLon))*1000
        dist = round(initDist,1)
        #print(dist)
        if dist < disMasCercano or disMasCercano == -1:
            disMasCercano=dist
            masCercano = i['id']
    return masCercano,disMasCercano

#funcion que realiza el grafo
def obtener_conexiones():
    #print("usando Dijkstar")
    graph = Graph()
    conexiones = Linea.objects.values('punto_inicio', 'punto_fin', 'peso')
    #print(puntoCercano)
    for i in conexiones:
        #print(i['punto_inicio'])
        graph.add_edge(i['punto_inicio'], i['punto_fin'], i['peso'])
        graph.add_edge(i['punto_fin'], i['punto_inicio'], i['peso'])
    return graph