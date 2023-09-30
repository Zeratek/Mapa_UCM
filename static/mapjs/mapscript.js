function createMap(center,zoom){
    let map = L.map('map').setView(center, zoom);
    let initialTile = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {minZoom:15,maxZoom: 20,attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/" target="_blank">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/" target="_blank">OpenStreetMap France</a>'});
    initialTile.addTo(map);
    return map;
};

function RellenarMapaIniciales() 
{
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
}
//funcion que quita capas y layers del mapa
function quitar(valor,objetos) {
    //console.log(valor);
    //console.log(typeof objetos);
    if (typeof objetos === "number") {
        filteredLayers = allBuildings.getLayers().filter(function(layer) 
        {
            return layer.options.piso === objetos && layer.options.nombre_fk !== "-";
        });
        console.log(filteredLayers);
        if (valor) {
            filteredLayers.forEach(element => {
                buildings.addLayer(element);
            });
        } 
        else {
            filteredLayers.forEach(element => {
                buildings.removeLayer(element);
            });
        }
    } else {
        objetos.forEach(element => {
        if (valor) {
            element.addTo(map);
        } 
        else {
            element.removeFrom(map);
        }
    });
    }
}

//Control customizado para capas
function customCtrl(m) {
    control=L.Control.extend({
        onAdd: function(map) {
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            container.innerHTML =   
            '<div class="btn-group-vertical" role="group" aria-label="First group">'+
                '<button type="button" class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#layersModal">'+
                    '<i class="bi bi-stack"></i>'+
                '</button>'+
            '</div>'
            ;
            return container;
        }});
    return control;
};

function buscarInformacionEficio() 
{
    let obj = document.getElementById("inputListaEdificios");
    let valor = obj.value;
    let existe = null;
    listaEdificacionesIniciales.forEach(edificacion => {
        if (edificacion.nombre === valor) {
            existe=edificacion.id;
        }
    });
    if (existe) {
        let estructura=null;
        allBuildings.getLayers().forEach(build => {
            if (build.options.id_value===existe) {
                estructura=build;
            }
        });
        if (estructura) {
            let layerName = 'flexCheckDefault'+estructura.options.piso;
            let layerselect = document.getElementById(layerName);
            if (layerselect.checked===false) {
                layerselect.checked=true;
                quitar(valor,estructura.options.piso)
            }
            //alert('cambia de color');
            estructura.setStyle({fillColor: 'red'});
            //map.setView(estructura.getBounds().getCenter());
            map.fitBounds(estructura.getBounds());
        } else {
            alert('no se encontro la estructura');
        }
    } else {
        alert('no existe');
    }
}

function BuildingOptions(e,map) 
{
    selectedLayer = e.layer;
    var popupContent = 
        '<div class="btn-group-vertical" role="group" aria-label="sec group">'+
            '<button onclick="UserPosConf(true)" class="btn btn-secondary">'+
                'Como llegar'+
            '</button>'+
        '</div>'
    ;
    L.popup()
    .setLatLng(e.latlng)
    .setContent(popupContent)
    .openOn(map);
    L.DomEvent.stopPropagation(e);
}
function Ruta() {
    console.log("ruta");
    console.log(link_ruta);
    map.locate({ setView: true, maxZoom: 1, enableHighAccuracy: true });
}
function onLocationError(e) {
    stopLocate();
    ejecuteLocation=true;
    alert("No se pudo obtener la ubicación precisa del usuario.");
    }
function onLocationFound(e) {
    
    let coords = e.latlng;
    console.log(coords);
    if (userPositionMarker) {
        userPositionMarker.setLatLng(coords);
    } else {
        userPositionMarker = L.circle(coords,{radius:1}).addTo(map).bindPopup("Estás aquí");
    }
}
function MapOptions(e,map) {
    contextmenuPosition = e.latlng;
    let btnStop = '';
    if (ejecuteLocation) 
    {
        btnStop = 
        '<button onclick="stopLocate();cerrarPopup();" class="btn btn-secondary">'+
            'Detener'+
        '</button>';
    }
    var popupContent = 
    '<div class="btn-group-vertical" role="group" aria-label="sec group">'+
        '<button onclick="UserPosConf(false);cerrarPopup();" class="btn btn-secondary">'+
            'Marcar Posicion'+
        '</button>'+
        btnStop+
    '</div>'
    ;
    L.popup()
    .setLatLng(e.latlng)
    .setContent(popupContent)
    .openOn(map);
    L.DomEvent.stopPropagation(e);
}


function UpdateUserPosition() 
{
    console.log('Actualizanco latlon usuario');
    map.locate({ setView: true, enableHighAccuracy: true });
}

function UpdatePosition(position) {
    let coords = [position.coords.latitude, position.coords.longitude];
    if (userPositionMarker) {
        userPositionMarker.setLatLng(coords);
        map.setView(userPositionMarker.getLatLng(), 13);
    } else {
        userPositionMarker = L.circle(coords,{radius:1}).addTo(map).bindPopup("Estás aquí");
        map.setView(userPositionMarker.getLatLng(), 13);
    }
}

function handleError(error) {
    console.log('Error:', error);
    alert(error);
  }
function UserPosConf(gps_info) 
{
    if (gps_info) {
        console.log('Actualizanco latlon usuario');
        //map.locate({ setView: true, enableHighAccuracy: true });
        
        if (ejecuteLocation === false) {
            console.log("a");
            ejecuteLocation=true;
            //idEjecute = setInterval(UpdateUserPosition, 4000);
            idEjecute = navigator.geolocation.watchPosition(UpdatePosition, handleError);
            console.log(idEjecute);
        }
    } else {
        if (userPositionMarker) {
            userPositionMarker.setLatLng(contextmenuPosition);
        } else {
            //userPositionMarker = L.circle(contextmenuPosition,{radius:1}).addTo(map).bindPopup("Estás aquí").openPopup();
            userPositionMarker = L.circle(contextmenuPosition,{radius:1}).addTo(map).bindPopup("Estás aquí");
        }
    }
}

function stopLocate() 
{
    //clearInterval(idEjecute);
    navigator.geolocation.clearWatch(idEjecute);
}
function cerrarPopup() 
{
    map.closePopup();
}