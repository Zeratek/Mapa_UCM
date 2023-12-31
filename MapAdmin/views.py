from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout, login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from .models import Punto,Linea,Edificacion,EstructuraEdificacion,EntradasEdificacion
from django.db.models import FloatField,Value,Q,F,Count
from django.db.models.functions import Cast,Coalesce
from django.core.paginator import Paginator
from django.db import models
import json
from .forms import createEdificationForm,loginForm
import math
import heapq
from haversine import haversine

#pagina de login
def login_page(request):
    if request.method == 'GET':
        return render(request, 'adminLogin.html', {'form': loginForm})
    else:
        user = authenticate(request, username = request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request, 'adminLogin.html', {'form': loginForm})
        else:
            login(request,user)
            return redirect('adminIndex')

def logout_page(request):
    logout(request)
    return redirect('adminLogin')

#pagina de mapa con herramientas
@login_required(login_url="adminLogin")
def index(request):
    puntosMapa = list(Punto.objects.annotate(lat_float=Cast('lat', FloatField())).annotate(lon_float=Cast('lon', FloatField())).values('id', 'lat_float', 'lon_float'))
    lineasMapa = list(Linea.objects.annotate(punto_inicio_lat_float=Cast('punto_inicio__lat', FloatField())).annotate(punto_inicio_lon_float=Cast('punto_inicio__lon', FloatField())).annotate(punto_fin_lat_float=Cast('punto_fin__lat', FloatField())).annotate(punto_fin_lon_float=Cast('punto_fin__lon', FloatField())).values('id', 'punto_inicio_lat_float', 'punto_inicio_lon_float', 'punto_fin_lat_float', 'punto_fin_lon_float'))
    listaEdificaciones = list(Edificacion.objects.all().annotate(nombre_fk = Coalesce('pertenece__nombre', Value('-'))).values('id','nombre','piso','nombre_fk'))
    listaEntradas = list(EntradasEdificacion.objects.all().values('id','edificio__id','punto_camino__id'))
    estructurasMapa = listaOrdenadaEstructuras()
    pisos = list(Edificacion.objects.values_list('piso', flat=True).distinct())
    return render(request, 'indexAdmin.html',{'puntosMapa':puntosMapa,'lineasMapa':lineasMapa,'listaEdificaciones':listaEdificaciones,'estructurasMapa':estructurasMapa,'pisos':pisos,'listaEntradas':listaEntradas})

#funcion que guarda los cambios del mapa
@login_required(login_url="adminLogin")
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
                    #latitud = round(diccionario['lat'],10)
                    #longitud = round(diccionario['lon'],10)
                    punto = Punto(lat=diccionario['lat'], lon=diccionario['lon'])
                    punto.save()
                    #print("punto guardado")
                elif diccionario['feature'] == 'newPoly':
                    puntoUno = Punto.objects.get(lat = diccionario['lat1'],lon =diccionario['lon1'])
                    puntoDos = Punto.objects.get(lat = diccionario['lat2'],lon =diccionario['lon2'])
                    initDist= haversine((diccionario['lat1'], diccionario['lon1']), (diccionario['lat2'], diccionario['lon2']))*1000
                    distancia = round(initDist,1)
                    linea = Linea(punto_inicio=puntoUno,punto_fin=puntoDos,peso=distancia)
                    linea.save()
                    #print("linea guardada")
                elif diccionario['feature'] == 'newBuild':
                    obj = Edificacion.objects.get(id=diccionario['id'])
                    #print(diccionario["coords"])
                    for item in diccionario["coords"][0]:
                        estructura = EstructuraEdificacion(edificacion=obj,lat=item['lat'],lon=item['lng'])
                        estructura.save()
                        #print("punto de estructura guardado")
                    #print("estructura guardada")
                elif diccionario['feature'] == 'updBuild':
                    obj = Edificacion.objects.get(id=diccionario['new_id'])
                    puntos = EstructuraEdificacion.objects.filter(edificacion__id=diccionario['id'])
                    for punto in puntos:
                        punto.edificacion = obj
                        punto.save()
                    #print('Se han actualizado los puntos de estructura')
                elif diccionario['feature'] == 'newEntry':
                    obj_edificio = Edificacion.objects.get(id=diccionario['edificio__id'])
                    obj_Punto = Punto.objects.get(id=diccionario['punto_camino__id'])
                    entrada = EntradasEdificacion(edificio=obj_edificio,punto_camino=obj_Punto)
                    entrada.save()
                    #print("Entrada Guardada")
                else:
                    if diccionario['feature'] == 'delPoint':
                        obj = get_object_or_404(Punto,id=diccionario['id'])
                    elif diccionario['feature'] == 'delPoly':
                        obj = get_object_or_404(Linea,id=diccionario['id'])
                    elif diccionario['feature'] == 'delBuild':
                        obj = EstructuraEdificacion.objects.filter(edificacion__id=diccionario['id'])
                    elif diccionario['feature'] == 'delEntry':
                        obj = get_object_or_404(EntradasEdificacion,id=diccionario['id'])
                        #print("se encontro la entrada")
                    try:
                        obj.delete()
                        #print("se elimino")
                    except:
                        print('No se encontro ningun objeto')
    return JsonResponse([],safe=False)

#pagina de creacion de edificaciones
@login_required(login_url="adminLogin")
@require_http_methods(["GET", "POST"])
def createEdificationPage(request):
    if request.method == 'GET':
        return render(request, 'adminCreateEdification.html',{'titulo_form':"Crear Edificacion",'form':createEdificationForm})
    elif request.method == 'POST':
        form = createEdificationForm(request.POST)
        if form.is_valid():
            newEdification = form.save(commit = False)
            newEdification.save()
            return redirect('viewEdification')
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

#pagina de edicion de edificaciones
@login_required(login_url="adminLogin")
@require_http_methods(["GET", "POST"])
def updateEdificationPage(request,e_id):
    objeto = get_object_or_404(Edificacion,id = e_id)
    if request.method == 'GET':
        form = createEdificationForm(instance = objeto)
        return render(request, 'adminCreateEdification.html',{'titulo_form':"Editar Edificacion",'form':form})
    elif request.method == 'POST':
        form = createEdificationForm(request.POST,instance = objeto)
        if form.is_valid():
            newEdification = form.save(commit = False)
            newEdification.save()
            return redirect('viewEdification')
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

#funcion que borra la edificacion por boton
@login_required(login_url="adminLogin")
def deleteEdificationPage(request,e_id):
    objeto = get_object_or_404(Edificacion,id = e_id)
    if objeto:
        try:
            objeto.delete()
            #print("se elimino")
            return redirect('viewEdification')
        except:
            #print('No se encontro ningun objeto')
            return redirect('viewEdification')

#vista de edificaciones
@login_required(login_url="adminLogin")
def viewEdificationPage(request):
    return render(request, 'adminEdificationView.html')

#funcion que actualiza la vista de ediciaciones
@login_required(login_url="adminLogin")
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
