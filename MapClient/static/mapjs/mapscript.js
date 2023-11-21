// funcion que permite mostrar el mapa de OpenStreetMap
function createMap(center,zoom){
    let map = L.map('map').setView(center, zoom);
    let initialTile = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {minZoom:15,maxZoom: 20,attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/" target="_blank">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/" target="_blank">OpenStreetMap France</a>'});
    initialTile.addTo(map);
    return map;
};

//fuuncion que rellena con las estructuras en el mapa
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
//funcion que quita capas o layers del mapa
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
//funcion que muestra busca la edificacion acerca el mapa y muestra la informacion en barra lateral
function buscarInformacionEficio() 
{
    let obj = document.getElementById("inputListaEdificios");
    let valor = obj.value;
    let existe = null;
    //console.log("entro");
    if (selectedLayer) {
        selectedLayer.setStyle({fillColor: 'grey'});
        //console.log("entro");
    }
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
            selectedLayer = estructura;
            InformacionEdificacion();
        } else {
            alert('no se encontro la estructura');
        }
    } else {
        alert('no existe');
    }
}

//funcion que muestra los popups
function BuildingOptions(e,map) 
{   
    if (selectedLayer) {
        selectedLayer.setStyle({fillColor: 'grey'});
        //console.log("entro");
    }
    selectedLayer = e.layer;
    selectedLayer.setStyle({fillColor: 'red'});
    var popupContent = 
        '<div class="btn-group-vertical" role="group" aria-label="sec group">'+
            '<button onclick="UserPosConf(true);cerrarPopup();" class="btn btn-secondary">'+
                'Como llegar'+
            '</button>'+
            '<button onclick="InformacionEdificacion();cerrarPopup();" class="btn btn-secondary" data-bs-toggle="offcanvas" href="#SideBar" role="button" aria-expanded="false" aria-controls="SideBar">'+
                'Informacion'+
            '</button>'+
        '</div>'
    ;
    L.popup()
    .setLatLng(e.latlng)
    .setContent(popupContent)
    .openOn(map);
    L.DomEvent.stopPropagation(e);
}

//funcion que muestra el popup para terminar la geolocalizacion
function MapOptions(e,map) {
    contextmenuPosition = e.latlng;
    let btnStop = '';
    if (ejecuteLocation) 
    {
        btnStop = 
        '<button onclick="stopLocate();cerrarPopup();" class="btn btn-secondary">'+
            'Detener'+
        '</button>';
        L.popup()
        .setLatLng(e.latlng)
        .setContent(btnStop)
        .openOn(map);
    }
    L.DomEvent.stopPropagation(e);
}

//funcion que actualiza la posicion del usuario y crea la ruta 
function UpdatePosition(position) {
    let coords = [position.coords.latitude, position.coords.longitude];
    let fetchLink;
    if (userPositionMarker) {
        userPositionMarker.setLatLng(coords);
        //map.setView(userPositionMarker.getLatLng(), 18);
        //map.fitBounds(userPositionMarker.getLatLng());
        //map.flyTo(userPositionMarker.getLatLng(), 20);
    } else {
        userPositionMarker = L.circle(coords,{radius:5}).addTo(map).bindPopup("Estás aquí");
        //map.setView(userPositionMarker.getLatLng(), 18);
        //map.fitBounds(userPositionMarker.getLatLng());
        //map.flyTo(userPositionMarker.getLatLng(), 20);
    }
    fetchLink = link_ruta.replace("p_lat", coords[0]);
    fetchLink = fetchLink.replace("p_lon", coords[1]);
    fetchLink = fetchLink.replace("e_id", targetGPSLayer.options.id_value);
    fetch(fetchLink)
        .then(response => response.json())
        .then(data =>{
            if (data[0] === null) {
                stopLocate();
                alert("no tiene entradas o camino existente");
            } else {
                if (ejecuteLocation === true) {
                    userPositionMarker.getPopup().setContent("Estás aquí, Distancia destino: "+data[2]+"metros");
                    puntosRuta = data[0];
                    caminoRuta = data[1];
                    if (routePoints.getLayers().length != 0 && routesPolylines.getLayers().length != 0) {
                        routePoints.clearLayers();
                        routesPolylines.clearLayers();
                    }
                    puntosRuta.forEach(element => {
                        var circle = L.circle([element.lat_float,element.lon_float], {radius: 2,fillColor:"blue",feature: 'oldPoint',id_value:element.id}).addTo(routePoints);
                    });
                    let element = puntosRuta[0];
                    //console.log(element)
                    var polyline = L.polyline([coords, [element.lat_float,element.lon_float]],{feature: 'oldPoly',id_value:element.id}).addTo(routesPolylines);
                
                    caminoRuta.forEach(element => {
                        var polyline = L.polyline([[element.punto_inicio_lat_float,element.punto_inicio_lon_float], [element.punto_fin_lat_float,element.punto_fin_lon_float]],{feature: 'oldPoly',id_value:element.id}).addTo(routesPolylines);
                    });
                }
            }
        });
}

//funcion que muestra el error al realizar intentar geolocalizacion
function handleError(error) {
    //console.log('Error:', error);
    //alert(error);
    stopLocate();
    alert('Error: No se ha logrado acceder al GPS');
}

//funcion que inicia la geolocalizacion
function UserPosConf() 
{
    if (ejecuteLocation) {
        stopLocate();
    }
    targetGPSLayer = selectedLayer;
    if (ejecuteLocation === false) {
        ejecuteLocation=true;
        idEjecute = navigator.geolocation.watchPosition(UpdatePosition, handleError);
        //console.log(idEjecute);
    }
}

//Funcion que coloca en la barra laterar la informacion de la edificacion seleccionada
function InformacionEdificacion() 
{
    //id_value
    edificacionSeleccionada = listaEdificacionesIniciales.filter(function(edif) {
        return edif.id === selectedLayer.options.id_value;
    });
    edificacionSelect = edificacionSeleccionada[0];
    //console.log(edificacionSeleccionada);
    let SideBar = document.getElementById('SideBar');
    let SideBarTitleElem = document.getElementById('SideBarTitle');
    let SideBodyElem = document.getElementById('SideBarBodyv2');
    SideBarTitleElem.innerHTML = edificacionSelect.nombre;
    texto = edificacionSelect.informacion.replace(/\n/g, "<br>");
    SideBodyElem.innerHTML = texto;
    //var offcanvasInstance = bootstrap.Offcanvas.getInstance(SideBar);
    //var offcanvasInstance = new bootstrap.Offcanvas(SideBar);
    //offcanvasInstance.show();
}

//funcion que termina la geolocalizacion
function stopLocate() 
{
    //clearInterval(idEjecute);
    navigator.geolocation.clearWatch(idEjecute);
    ejecuteLocation = false;
    targetGPSLayer = null;
    if (routePoints.getLayers().length != 0 && routesPolylines.getLayers().length != 0) {
        routePoints.clearLayers();
        routesPolylines.clearLayers();
    }
    
}
//funcion que cierra los popups
function cerrarPopup() 
{
    map.closePopup();
}