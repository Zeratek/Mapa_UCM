from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from .models import Punto,Linea,Edificacion,EstructuraEdificacion
from django.db.models import FloatField,Value,Q,F,Count
from django.db.models.functions import Cast,Coalesce
from django.core.paginator import Paginator
from django.db import models
import json
from itertools import groupby
from .forms import createEdificationForm
from collections import defaultdict
# Create your views here.
def index(request):
    #buildings = list(Buildings.objects.values('id','name','point__lat', 'point__lon'))
    puntosMapa = list(Punto.objects.annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('id', 'lat_float', 'lon_float'))
    lineasMapa = list(Linea.objects.annotate(punto_inicio_lat_float=Cast('punto_inicio__lat', FloatField())).annotate(punto_inicio_lon_float=Cast('punto_inicio__lon', FloatField())).annotate(punto_fin_lat_float=Cast('punto_fin__lat', FloatField())).annotate(punto_fin_lon_float=Cast('punto_fin__lon', FloatField())).values('id', 'punto_inicio_lat_float', 'punto_inicio_lon_float', 'punto_fin_lat_float', 'punto_fin_lon_float'))
    listaEdificaciones = Edificacion.objects.all().values()

    listaEdificacionesEstructura = listaEstructuras()
    print(listaEdificacionesEstructura)
    

    """
    queryset = EstructuraEdificacion.objects.values_list('edificacion', 'lat')
    print(queryset)
    result = {}
    for edificacion, group in groupby(queryset, lambda x: x[0]):
        result[edificacion] = [x[1] for x in group]
    """
    # Crear un diccionario con valores predeterminados de lista vacía
    #for objeto in listaEdificaciones:
    #listaEdificacionesEstructura = EstructuraEdificacion.objects.values('edificacion').annotate(lats=))
    #print(listaEdificacionesEstructura)
    #print(puntosMapa)
    #print(lineasMapa)
    return render(request, 'indexAdmin.html',{'puntosMapa':puntosMapa,'lineasMapa':lineasMapa,'listaEdificaciones':listaEdificaciones})


def saveData(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        #print(data)
        for lista in data:
            if not lista:
                continue
            for diccionario in lista:
                #print(diccionario['feature'])
                if diccionario['feature'] == 'newPoint':
                    latitud = round(diccionario['lat'],10)
                    longitud = round(diccionario['lon'],10)
                    punto = Punto(lat=diccionario['lat'], lon=diccionario['lon'])
                    punto.save()
                    print("punto guardado")
                elif diccionario['feature'] == 'newPoly':
                    latitudUno = round(diccionario['lat1'],10)
                    longitudUno = round(diccionario['lon1'],10)
                    latitudDos = round(diccionario['lat2'],10)
                    longitudDos = round(diccionario['lon2'],10)
                    puntoUno = Punto.objects.get(lat = latitudUno,lon =longitudUno)
                    puntoDos = Punto.objects.get(lat = latitudDos,lon =longitudDos)
                    linea = Linea(punto_inicio=puntoUno,punto_fin=puntoDos)
                    linea.save()
                    print("linea guardada")
                elif diccionario['feature'] == 'newBuild':
                    obj = Edificacion.objects.get(id=diccionario['id'])
                    print(diccionario["coords"])
                    for item in diccionario["coords"][0]:
                        latitud = round(item['lat'],10)
                        longitud = round(item['lng'],10)
                        estructura = EstructuraEdificacion(edificacion=obj,lat=latitud,lon=longitud)
                        estructura.save()
                        print("punto de estructura guardado")
                    print("estructura guardada")
                elif diccionario['feature'] == 'delPoint':
                    #print(diccionario['id'])
                    #print(diccionario['feature'])
                    try:
                        obj = Punto.objects.get(id=diccionario['id'])
                        obj.delete()
                        print("El objeto se eliminó correctamente.")
                    except Punto.DoesNotExist:
                        print("El objeto no existe.")

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
    #edificaciones = list(Edificacion.objects.all().annotate(nombre_fk = Coalesce('pertenece__nombre', Value('-'))).values('id','nombre','nombre_fk'))
    #print(edificaciones)
    return render(request, 'adminEdificationView.html')
    #return render(request, 'adminEdificationView.html',{'edificaciones':edificaciones})

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

    edificationList = Edificacion.objects.filter(query).annotate(nombre_fk = Coalesce('pertenece__nombre', Value('-'))).values('id','nombre','nombre_fk')
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
def listaEstructuras():
    lista = EstructuraEdificacion.objects.annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('edificacion', 'lat_float', 'lon_float')
    if lista:
        result = {}
        for c in lista:
            if c['edificacion'] not in result:
                result[c['edificacion']] = []
            result[c['edificacion']].append({'latitud': c['lat_float'], 'longitud': c['lon_float']})
        new_result = []
        for k,v in result.items():
            new_result.append({'id': k, 'coordenadas': v})
        return new_result
    else:
        return []