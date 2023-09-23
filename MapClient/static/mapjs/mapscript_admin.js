function createMap(center,zoom){
    let map = L.map('map').setView(center, zoom);
    let initialTile = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {minZoom:15,maxZoom: 20,attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/" target="_blank">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/" target="_blank">OpenStreetMap France</a>'});
    initialTile.addTo(map);
    return map;
};
//Funcion que rellena el mapa con los datos de la BD
function RellenarMapaIniciales() {
    
    puntosMapaIniciales.forEach(element => {
        var circle = L.circle([element.lat_float,element.lon_float], {radius: 2,fillColor:"blue",feature: 'oldPoint',id_value:element.id}).addTo(routePoints);
    });
    lineasMapaIniciales.forEach(element => {
        var polyline = L.polyline([[element.punto_inicio_lat_float,element.punto_inicio_lon_float], [element.punto_fin_lat_float,element.punto_fin_lon_float]],{feature: 'oldPoly',id_value:element.id}).addTo(routesPolylines);
    });
    estructurasMapaIniciales.forEach(element => {
        let lista = element.coords.map(function(coord) 
        {
            return [coord.latitud,coord.longitud]
        });
        //console.log(lista);
        var polygon = L.polygon(lista,{color: 'grey',fillColor: 'grey',feature:'oldBuild',id_value:element.id,piso:element.piso,nombre_fk:element.nombre_fk}).addTo(allBuildings);
        polygon.bindTooltip(element.nombre, {
            permanent: false,
            direction: "center",
            opacity: 0.7
        });
        if (element.piso === 1) 
        {
            buildings.addLayer(polygon);
        }
    });
    var modalDiv =  document.getElementById('layersModalBody'); 
    listaPisos.forEach(element => {
        
        var div = document.createElement('div');
        let chek = '';
        div.className = 'form-check';
        if (element === 1) {
            chek = 'checked'
        }
        div.innerHTML = '<input class="form-check-input" onchange="quitar(this.checked,' + element + ')" type="checkbox" value="" id="flexCheckDefault' + element + '"'+chek+'><label class="form-check-label" for="flexCheckDefault' + element + '">Piso ' + element + '</label>';
        modalDiv.appendChild(div);
    });
    
};

function rellenarLayerOpciones() 
{
    for (var piso in featureGroups) {
        var div = document.createElement('div');
        div.className = 'form-check';
        div.innerHTML = '<input class="form-check-input" onchange="quitar(this.checked,[' + featureGroups[piso] + '])" type="checkbox" value="" id="flexCheckDefault' + piso + '"><label class="form-check-label" for="flexCheckDefault' + piso + '">Piso ' + piso + '</label>';
        document.body.appendChild(div);
    }
}
//Control customizado para herramientas y capas

function customCtrl(m) {
    control=L.Control.extend({
        onAdd: function(map) {
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            container.innerHTML =   
            '<div class="btn-group-vertical" role="group" aria-label="First group">'+
                '<button type="button" class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#layersModal">'+
                    '<i class="bi bi-stack"></i>'+
                '</button>'+
                '<button type="button" class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#toolsModal">'+
                    '<i class="bi bi-tools"></i>'+
                '</button>'+
            '</div>'
            ;
            return container;
        }});
    return control;
};

//Funcion que despliega popup con las opciones de las lineas de camino
function RouteLinesOptions(e,map) {
    selectedLayer = e.layer;
        var popupContent = 
            '<div class="btn-group-vertical" role="group" aria-label="sec group">'+
                '<button onclick="removeLine()" class="btn btn-secondary">'+
                    'Eliminar Camino'+
                '</button>'+
            '</div>'
        ;
        L.popup()
        .setLatLng(e.latlng)
        .setContent(popupContent)
        .openOn(map);
        L.DomEvent.stopPropagation(e);
};

//Funcion que despliega popup con las opciones de los puntos de camino
function RoutePointsOptions(e,map) {
    selectedLayer = e.layer;
        var popupContent = 
            '<div class="btn-group-vertical" role="group" aria-label="sec group">'+
                '<button onclick="removeCircle()" class="btn btn-secondary">'+
                    'Eliminar'+
                '</button>'+
                '<button onclick="addCircleToVariable()" class="btn btn-secondary">'+
                    'Escoger'+
                '</button>'+
            '</div>'
        ;
        L.popup()
        .setLatLng(e.latlng)
        .setContent(popupContent)
        .openOn(map);
        L.DomEvent.stopPropagation(e);
};

//Funcion que despliega popup con las opciones de los construccion de edificaciones
function BuildingPointsOptions(e,map) {
    selectedCircle = e.layer;
    var popupContent = 
        '<div class="btn-group-vertical" role="group" aria-label="sec group">'+
            '<button onclick="removeCirclesBuilding()" class="btn btn-secondary">'+
                'Eliminar Puntos'+
            '</button>'+
            '<button onclick="crearEdificio()" class="btn btn-secondary">'+
                'Crear Estructura'+
            '</button>'+
        '</div>'
    ;
    L.popup()
    .setLatLng(e.latlng)
    .setContent(popupContent)
    .openOn(map);
    L.DomEvent.stopPropagation(e);
};

//funcion que remueve todos los circulos de estructura
function removeCirclesBuilding() {
    buildingPoints.clearLayers();
    buildingPolylines.clearLayers();
}

//Funcion que crea la estructura con los puntos creados
function crearEdificio() 
{
    cerrarPopup()
    if (buildingPoints.getLayers().length > 2) 
    {
        let ListaPuntos = buildingPoints.getLayers().map(function(layer) 
        {
            var latlng = layer.getLatLng();
            return [latlng.lat,latlng.lng];
        });
        console.log(ListaPuntos);
        var polygon = L.polygon(ListaPuntos,{color: 'grey',fillColor: 'grey'}).addTo(buildStructures);
        //map.fitBounds(polygon.getBounds());
        buildingPoints.clearLayers();
        buildingPolylines.clearLayers();
    } 
    else 
    {
        alert("Se necesitan mas de dos puntos");
    }
}

//Funcion que envia a Django los datos de los cambios realizados en el mapa para guardarlos
function saveData(link) {
    var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var dict = ListaParaGuardar();
    var xhr = new XMLHttpRequest();
    xhr.open('POST', link);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', csrf_token);
    xhr.onload = function() {
    if (xhr.status === 200) {
        console.log('Success');
        //location.reload()
    } else {
        console.log('Error');
    }
    };
    xhr.send(JSON.stringify(dict));
}

//Funcion que filtra y devulve todos los cambios de layers realizados para poder guardar los cambios
function ListaParaGuardar() 
{
    //Variable que devuelve los caminos nuevos
    var newPolylines = routesPolylines.getLayers().filter(function(layer) 
    {
        return layer.options.feature === 'newPoly';
    }).map(function(layer) 
    {
        var latlngs = layer.getLatLngs();
        return {
            lat1: latlngs[0].lat,
            lon1: latlngs[0].lng,
            lat2: latlngs[1].lat,
            lon2: latlngs[1].lng,
            feature: layer.options.feature
        };
    });
    //Variable que devuelve los puntos nuevos
    var newCircles = routePoints.getLayers().filter(function(layer) 
    {
        return layer.options.feature === 'newPoint';
    }).map(function(layer) 
    {
        var latlng = layer.getLatLng();
        return {
          lat: latlng.lat,
          lon: latlng.lng,
          feature: layer.options.feature
        };
    });
    var newBuildEstructure = allBuildings.getLayers().filter(function(layer) 
    {
        return layer.options.feature === 'newBuild' || layer.options.feature === 'updBuild';
    }).map(function(layer){
        var latlngs = layer.getLatLngs();
        console.log(latlngs);
        if (!('new_id_value' in selectedLayer.options)) {
            return {
                coords:latlngs,
                feature: layer.options.feature,
                id: layer.options.id_value
            };
        } else {
            return {
                feature: layer.options.feature,
                id: layer.options.id_value,
                new_id: layer.options.new_id_value
            };
        }
    });
    console.log(newBuildEstructure);
    //lista de nuevas entradas
    var newEntrances = listaEntradas.filter(function(entry) {
        return entry.feature === 'newEntry'||entry.feature === 'delEntry'
    });
    //Variable que devuelve los datos a eliminar
    var dLayers = deletedLayers.getLayers().map(function(layer) 
    {
        return {
            id : layer.options.id_value,
            feature: layer.options.feature
          };
    });

    
    console.log(dLayers);
    //console.log(newPolylines);
    //console.log(newCircles);}
    listaFinal = [newCircles,newPolylines,newBuildEstructure,newEntrances,dLayers]
    //listaFinal = [newCircles,newPolylines,newBuildEstructure,dLayers]
    return listaFinal;
}

function CambiarOpcion(valor) {
    opcionesTrabajo = valor;
    newRoute = false;
    selectedCircle = null;
    lastCircle = null;
    secondLastCircle = null;
    console.log(opcionesTrabajo)
}
//funcion que muestra la estructura del edificio uniendo Circulos con Polylines
function estructuraEdificio() 
{
    let largo = buildingPoints.getLayers().length;
    let auxPrimero = null;
    let auxSegundo = null;
    buildingPolylines.clearLayers();
    buildingPoints.eachLayer(function(layer) 
    {
        if (auxPrimero === null) 
        {
            auxPrimero = layer;
        } 
        else 
        {
            auxSegundo = auxPrimero;
            auxPrimero = layer;
            var polyline = L.polyline([auxPrimero.getLatLng(), auxSegundo.getLatLng()],{feature: 'newPoly'}).addTo(buildingPolylines);
        }
    });
    if (auxSegundo != buildingPoints.getLayers()[0] && auxSegundo != null) 
    {
        auxSegundo = buildingPoints.getLayers()[0];
        var polyline = L.polyline([auxPrimero.getLatLng(), auxSegundo.getLatLng()],{feature: 'newPoly'}).addTo(buildingPolylines);
    }
}

function BuildingOptions(e,map) 
{
    selectedLayer = e.layer;
    var popupContent = 
        '<div class="btn-group-vertical" role="group" aria-label="sec group">'+
            '<button onclick="removeBuild()" class="btn btn-secondary">'+
                'Eliminar'+
            '</button>'+
            '<button onclick="cerrarPopup()" class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#buildingModal">'+
                'Añadir Estructura'+
            '</button>'+
        '</div>'
    ;
    L.popup()
    .setLatLng(e.latlng)
    .setContent(popupContent)
    .openOn(map);
    L.DomEvent.stopPropagation(e);
}

function CreatedBuildingOptions(e,map) 
{
    selectedLayer = e.layer;
    var popupContent = 
        '<div class="btn-group-vertical" role="group" aria-label="sec group">'+
            '<button onclick="removeBuild()" class="btn btn-secondary">'+
                'Eliminar'+
            '</button>'+
            '<button onclick="cerrarPopup()" class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#buildingModal">'+
                'Añadir Estructura'+
            '</button>'+
            '<button onclick="BuildingEntrance()" class="btn btn-secondary">'+
                'Añadir entradas'+
            '</button>'+
        '</div>'
    ;
    L.popup()
    .setLatLng(e.latlng)
    .setContent(popupContent)
    .openOn(map);
    L.DomEvent.stopPropagation(e);
}
//Funcion que añade o quita entradas a los edificios o salas
function BuildingEntrance() 
{
    cerrarPopup()
    selectedBuild = selectedLayer;
    if (entrances) {
        UnckeckEntrance();
    }
    let id_filtro = selectedBuild.options.id_value;
    let listaFiltrada = listaEntradas.filter(function(elemento) 
    {
        return elemento.edificio__id === id_filtro;
    });
    listaFiltrada.forEach(element => {
        let circuloFiltrado = null;
        routePoints.getLayers().forEach(elem => {
            if (elem.options.id_value === element.punto_camino__id) {
                circuloFiltrado = elem;
            }
        });
        if (circuloFiltrado) {
            circuloFiltrado.setStyle({fillColor: 'red'});
            auxiliarEntranceList.addLayer(circuloFiltrado);
        }
    });
    entrances=true;
}
//Funcion que desmarca las entradas 
function UnckeckEntrance() 
{
    auxiliarEntranceList.getLayers().forEach(element => {
        element.setStyle({fillColor: 'blue'});
        auxiliarEntranceList.removeLayer(element);
    });
    //auxiliarEntranceList.clearLayers();
}
//Funcion que decide si es nuevo o se esta actualizando un layer de structura de edificacion
function asociarEstructura() 
{
    if (!('feature' in selectedLayer.options)) 
    {
        console.log('Nuevo')
        asociarEdificacionAEstructura();
    } else {
        console.log('Antiguo')
        EditarAsEdificacionAEstructura();
    }
}

//Funcion que asocia la estructura creada con una edificacion(edificio,sala,oficina,etc)
function asociarEdificacionAEstructura() 
{
    let select = document.getElementById('selectorEdificacion');
    let opcionSeleccionada = select.options[select.selectedIndex].value;
    console.log(opcionSeleccionada);
    if (opcionSeleccionada==="0") {
        return;
    }
    selectedLayer.options.feature = "newBuild";
    selectedLayer.options.id_value = parseInt(opcionSeleccionada);
    let selectedDict = buscar_diccionario_id(listaEdificacionesIniciales,parseInt(opcionSeleccionada))
    selectedLayer.options.piso = selectedDict.piso;
    selectedLayer.options.nombre_fk = selectedDict.nombre_fk;
    selectedLayer.bindTooltip(selectedDict.nombre, {
        permanent: false,
        direction: "center",
        opacity: 0.7
    });
    let layerName = 'flexCheckDefault'+selectedDict.piso;
    if (document.getElementById(layerName).checked) 
    {
        console.log("añade al buildings");
        buildStructures.removeLayer(selectedLayer);
        allBuildings.addLayer(selectedLayer);
        buildings.addLayer(selectedLayer);
    } else 
    {
        console.log("no lo añade al buildings");
        buildStructures.removeLayer(selectedLayer);
        allBuildings.addLayer(selectedLayer);
    }
    //console.log(opcionSeleccionada); 
}

//funcion que actualiza la asociacion de estructura 
function EditarAsEdificacionAEstructura() 
{
    let select = document.getElementById('selectorEdificacion');
    let opcionSeleccionada = select.options[select.selectedIndex].value;
    if (opcionSeleccionada==="0") {
        return;
    }
    let selectedDict = buscar_diccionario_id(listaEdificacionesIniciales,parseInt(opcionSeleccionada))
    if (selectedLayer.options.feature === "newBuild") 
    {
        selectedLayer.options.id_value = parseInt(opcionSeleccionada);
        selectedLayer.options.piso = selectedDict.piso;
        selectedLayer.options.nombre_fk = selectedDict.nombre_fk;
        console.log('Entro a nuewBuild')
        var tooltip = selectedLayer.getTooltip();
        tooltip.setContent(selectedDict.nombre);
    } else 
    {
        selectedLayer.options.feature = "updBuild";
        selectedLayer.options.new_id_value = parseInt(opcionSeleccionada);
        var tooltip = selectedLayer.getTooltip();
        tooltip.setContent(selectedDict.nombre);
    }
    let layerName = 'flexCheckDefault'+selectedDict.piso;
    if (document.getElementById(layerName).checked) 
    {
        console.log("añade al buildings");
        buildings.addLayer(selectedLayer);
    }
}

function removeLine() 
{
    cerrarPopup();
    if (selectedLayer.options.feature === "newPoly")
    {
        routesPolylines.removeLayer(selectedLayer);
    }
    else
    {
        selectedLayer.options.feature = "delPoly";
        routesPolylines.removeLayer(selectedLayer);
        deletedLayers.addLayer(selectedLayer);
        //console.log(selectedLayer);
        //console.log(deletedLayers.getLayers());
    }
}

function removeBuild() 
{
    cerrarPopup();
    if (selectedLayer.options.feature === "newBuild")
    {
        buildings.removeLayer(selectedLayer);
    }
    else
    {
        selectedLayer.options.feature = "delBuild";
        buildings.removeLayer(selectedLayer);
        deletedLayers.addLayer(selectedLayer);
        //console.log(selectedLayer);
        //console.log(deletedLayers.getLayers());
    }
}

//funcion que encuentra el objeto de la lista
function buscar_diccionario_id(lista, id) 
{
    for (let i = 0; i < lista.length; i++) 
    {
      if (lista[i].id === id) 
      {
        return lista[i];
      }
    }
    return null;
}
//funcion que cierra el popup abierto por las opciones
function cerrarPopup() 
{
    map.closePopup();
}
