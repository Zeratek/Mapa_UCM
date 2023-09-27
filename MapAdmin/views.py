from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from .models import Punto,Linea,Edificacion,EstructuraEdificacion,EntradasEdificacion
from django.db.models import FloatField,Value,Q,F,Count
from django.db.models.functions import Cast,Coalesce
from django.core.paginator import Paginator
from django.db import models
import json
from .forms import createEdificationForm
import math
import heapq

# Create your views here.
def index(request):
    puntosMapa = list(Punto.objects.annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('id', 'lat_float', 'lon_float'))
    lineasMapa = list(Linea.objects.annotate(punto_inicio_lat_float=Cast('punto_inicio__lat', FloatField())).annotate(punto_inicio_lon_float=Cast('punto_inicio__lon', FloatField())).annotate(punto_fin_lat_float=Cast('punto_fin__lat', FloatField())).annotate(punto_fin_lon_float=Cast('punto_fin__lon', FloatField())).values('id', 'punto_inicio_lat_float', 'punto_inicio_lon_float', 'punto_fin_lat_float', 'punto_fin_lon_float'))
    listaEdificaciones = list(Edificacion.objects.all().annotate(nombre_fk = Coalesce('pertenece__nombre', Value('-'))).values('id','nombre','piso','nombre_fk'))
    listaEntradas = list(EntradasEdificacion.objects.all().values('id','edificio__id','punto_camino__id'))
    pruebaDJ()
    estructurasMapa = listaOrdenadaEstructuras()
    pisos = list(Edificacion.objects.values_list('piso', flat=True).distinct())
    return render(request, 'indexAdmin.html',{'puntosMapa':puntosMapa,'lineasMapa':lineasMapa,'listaEdificaciones':listaEdificaciones,'estructurasMapa':estructurasMapa,'pisos':pisos,'listaEntradas':listaEntradas})

def pruebaDJ():
    graph = {
    '1': {'2': 17,'5': 13},
    #'1': {'5': 13},
    '2': {'3': 10},
    '3': {'4': 5},
    '5': {'4': 5},
    '4': {}
    }

    start = '1'
    end = '4'

    shortest_distance, shortest_path = dijkstra(graph, start, end)
    print(f"Distancia más corta: {shortest_distance}")
    print(f"Camino más corto: {shortest_path}")

def saveData(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        for lista in data:
            if not lista:
                continue
            for diccionario in lista:
                #print(diccionario['feature'])
                if diccionario['feature'] == 'newPoint':
                    #latitud = round(diccionario['lat'],10)
                    #longitud = round(diccionario['lon'],10)
                    punto = Punto(lat=diccionario['lat'], lon=diccionario['lon'])
                    punto.save()
                    #print("punto guardado")
                elif diccionario['feature'] == 'newPoly':
                    puntoUno = Punto.objects.get(lat = diccionario['lat1'],lon =diccionario['lon1'])
                    puntoDos = Punto.objects.get(lat = diccionario['lat2'],lon =diccionario['lon2'])
                    
                    #distancia = haversine(latitudUno, longitudUno, latitudDos, longitudDos)
                    distancia = haversine(diccionario['lat1'], diccionario['lon1'], diccionario['lat2'], diccionario['lon2'])
                    linea = Linea(punto_inicio=puntoUno,punto_fin=puntoDos,peso=distancia)
                    linea.save()
                    print(distancia)
                    print("linea guardada")
                elif diccionario['feature'] == 'newBuild':
                    obj = Edificacion.objects.get(id=diccionario['id'])
                    print(diccionario["coords"])
                    for item in diccionario["coords"][0]:
                        estructura = EstructuraEdificacion(edificacion=obj,lat=item['lat'],lon=item['lng'])
                        estructura.save()
                        print("punto de estructura guardado")
                    print("estructura guardada")
                elif diccionario['feature'] == 'updBuild':
                    obj = Edificacion.objects.get(id=diccionario['new_id'])
                    puntos = EstructuraEdificacion.objects.filter(edificacion__id=diccionario['id'])
                    for punto in puntos:
                        punto.edificacion = obj
                        punto.save()
                    print('Se han actualizado los puntos de estructura')
                elif diccionario['feature'] == 'newEntry':
                    obj_edificio = Edificacion.objects.get(id=diccionario['edificio__id'])
                    obj_Punto = Punto.objects.get(id=diccionario['punto_camino__id'])
                    entrada = EntradasEdificacion(edificio=obj_edificio,punto_camino=obj_Punto)
                    entrada.save()
                    print("Entrada Guardada")
                else:
                    if diccionario['feature'] == 'delPoint':
                        obj = get_object_or_404(Punto,id=diccionario['id'])
                    elif diccionario['feature'] == 'delPoly':
                        obj = get_object_or_404(Linea,id=diccionario['id'])
                    elif diccionario['feature'] == 'delBuild':
                        obj = EstructuraEdificacion.objects.filter(edificacion__id=diccionario['id'])
                    elif diccionario['feature'] == 'delEntry':
                        obj = get_object_or_404(EntradasEdificacion,id=diccionario['id'])
                        print("se encontro la entrada")
                    try:
                        obj.delete()
                        print("se elimino")
                    except:
                        print('No se encontro ningun objeto')
    return JsonResponse([],safe=False)

@require_http_methods(["GET", "POST"])
def createEdificationPage(request):
    if request.method == 'GET':
        return render(request, 'adminCreateEdification.html',{'form':createEdificationForm})
    elif request.method == 'POST':
        form = createEdificationForm(request.POST)
        if form.is_valid():
            newEdification = form.save(commit = False)
            newEdification.save()
            return redirect('viewEdification')
    else:
        return HttpResponseNotAllowed(["GET", "POST"])
    
@require_http_methods(["GET", "POST"])
def updateEdificationPage(request,e_id):
    objeto = get_object_or_404(Edificacion,id = e_id)
    if request.method == 'GET':
        form = createEdificationForm(instance = objeto)
        return render(request, 'adminCreateEdification.html',{'form':form})
    elif request.method == 'POST':
        form = createEdificationForm(request.POST,instance = objeto)
        if form.is_valid():
            newEdification = form.save(commit = False)
            newEdification.save()
            return redirect('viewEdification')
    else:
        return HttpResponseNotAllowed(["GET", "POST"])
    
def viewEdificationPage(request):
    return render(request, 'adminEdificationView.html')

def viewEdificationPageList(request,name,option):
    query = Q()
    #print(type(option))
    if name != 'all':
        query &= Q(nombre__icontains=name)
    if option != '1':
        if option == '2':
            query &= Q(pertenece__isnull=False)
        else:
            query &= Q(pertenece__isnull=True)

    edificationList = Edificacion.objects.filter(query).annotate(nombre_fk = Coalesce('pertenece__nombre', Value('-'))).values('id','nombre','piso','nombre_fk').order_by('id')
    paginator = Paginator(edificationList, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    data = list(page_obj)

    json_data = {
        'page': page_obj.number,
        'total_pages': paginator.num_pages,
        'data': data,
    }
    return JsonResponse(json_data, safe=False)


#FUNCIONES AUXILIARES
#funcion que devuelve la lista de coordenadas por cada estructura
def listaOrdenadaEstructuras():
    #lista = EstructuraEdificacion.objects.annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('edificacion','edificacion__nombre', 'lat_float', 'lon_float')
    lista = EstructuraEdificacion.objects.annotate(nombre_fk = Coalesce('edificacion__pertenece__nombre', Value('-'))).annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('edificacion','edificacion__nombre','edificacion__piso','nombre_fk', 'lat_float', 'lon_float')
    #print(lista)
    diccionario = {}

    for item in lista:
        id = item['edificacion']
        nombre = item['edificacion__nombre']
        piso = item['edificacion__piso']
        nombre_fk = item['nombre_fk']
        latitud = item['lat_float']
        longitud = item['lon_float']
        
        if id in diccionario:
            diccionario[id]['coords'].append({'latitud': latitud, 'longitud': longitud})
        else:
            diccionario[id] = {'id': id, 'nombre': nombre,'piso':piso,'nombre_fk':nombre_fk, 'coords':[{'latitud': latitud, 'longitud': longitud}]}

    resultado = list(diccionario.values())
    return resultado

# funcion que calcula la distancia entre coordenadas
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # radio de la Tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    resultado = latitudUno = round(R * c,1)
    return resultado


def dijkstra(graph, start, end):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    queue = [(0, start)]
    previous_nodes = {node: None for node in graph}
    
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        
        if current_node == end:
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = previous_nodes[current_node]
            path.reverse()
            return distances[end], path
        
        if current_distance > distances[current_node]:
            continue
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))
    
    return -1, []