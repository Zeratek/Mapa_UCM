function createMap(center,zoom){
    let map = L.map('map').setView(center, zoom);
    let initialTile = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {minZoom:15,maxZoom: 20,attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/" target="_blank">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/" target="_blank">OpenStreetMap France</a>'});
    initialTile.addTo(map);
    return map;
};

//Funcion que rellena el mapa con los datos de la BD
function RellenarMapa() {
    let puntosMapaIniciales = JSON.parse(document.getElementById('puntosMapa_json').textContent);
    let lineasMapaIniciales = JSON.parse(document.getElementById('lineasMapa_json').textContent);
    puntosMapaIniciales.forEach(element => {
        var circle = L.circle([element.lat_float,element.lon_float], {radius: 2,feature: 'oldPoint',id_value:element.id}).addTo(routePoints);
    });
    lineasMapaIniciales.forEach(element => {
        var polyline = L.polyline([[element.punto_inicio_lat_float,element.punto_inicio_lon_float], [element.punto_fin_lat_float,element.punto_fin_lon_float]],{feature: 'oldPoly',id_value:element.id}).addTo(routesPolylines);
    });
};

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

//Funcion que despliega popup con las opciones de los puntos de camino
function RoutePointsOptions(e,map) {
    selectedCircle = e.layer;
        var popupContent = 
            '<div class="btn-group-vertical" role="group" aria-label="sec group">'+
                '<button onclick="removeCircle()" class="btn btn-secondary">'+
                    'Eliminar'+
                '</button>'+
                '<button onclick="addCircleToVariable(selectedCircle)" class="btn btn-secondary">'+
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
            '<button onclick="removeCircle()" class="btn btn-secondary">'+
                'Eliminar'+
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
        var polygon = L.polygon(ListaPuntos,{color: 'grey',fillColor: 'grey'}).addTo(buildings);
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
    
    var newBuildEstructure = buildings.getLayers().filter(function(layer) 
    {
        return layer.options.feature === 'newBuild';
    }).map(function(layer){
        var latlngs = layer.getLatLngs();
        console.log(latlngs);
        return {
            coords:latlngs,
            feature: layer.options.feature,
            id: layer.options.id_value
        };
    });
    console.log(newBuildEstructure);
    /*
    var newBuildEstructure = buildings.getLayers().filter(function(layer) 
    {
        return layer.options.feature === 'newBuild';
    }).map(function(layer){
        console.log(layer);
        var latlng = layer.getLatLngs();
        var coords = latlng.map(function(latlng) {
            return {lat: latlng.lat, lng: latlng.lng};
        });
        return {coords: coords, feature: layer.options.feature};
    });
    console.log(newBuildEstructure);
    */


    //Variable que devuelve los datos a eliminar
    var dLayers = deletedLayers.getLayers().map(function(layer) 
    {
        return {
            id : layer.options.id_value,
            feature: layer.options.feature
          };
    });

    //console.log(newPolylines);
    //console.log(newCircles);
    listaFinal = [newCircles,newPolylines,newBuildEstructure,dLayers]
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
    selectedBuild = e.layer;
    var popupContent = 
        '<div class="btn-group-vertical" role="group" aria-label="sec group">'+
            '<button onclick="removeCircle()" class="btn btn-secondary">'+
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

//Funcion que asocia la estructura creada con una edificacion(edificio,sala,oficina,etc)
function asociarEdificacionAEstructura() 
{
    let select = document.getElementById('selectorEdificacion');
    let opcionSeleccionada = select.options[select.selectedIndex].value;
    if (!('id_value' in selectedBuild.options)) {
        selectedBuild.options.feature = "newBuild";
        selectedBuild.options.id_value = parseInt(opcionSeleccionada);
        console.log(opcionSeleccionada); 
    }
    else
    {
        if (selectedBuild.options.feature === "newBuild") 
        {
            selectedBuild.options.id_value = parseInt(opcionSeleccionada);
        } else 
        {
            selectedBuild.options.feature = "updBuild";
            selectedBuild.options.id_value = parseInt(opcionSeleccionada);
        }
    }
}

//funcion que cierra el popup abierto por las opciones
function cerrarPopup() 
{
    map.closePopup();
}