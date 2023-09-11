from django.shortcuts import render, redirect
from django.http import JsonResponse
#from MapAdmin.models import Buildings,MapPoints
# Create your views here.

def index(request):
    buildings = []#list(Buildings.objects.values('id','name','point__lat', 'point__lon'))
    return render(request, 'index.html',{'Buildings':buildings})

def building_info(request, buildingID):
    buildingInfo = []#list(Buildings.objects.filter(id = buildingID).values('id','name'))
    print(buildingInfo)
    return JsonResponse(buildingInfo, safe=False)
