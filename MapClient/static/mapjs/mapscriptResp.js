function createMap(center,zoom){
    let map = L.map('map').setView(center, zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png?noLabels', {maxZoom: 19,attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);
    console.log(center);
    return map;
};





/*
let map = L.map('map').setView(center, zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19,attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);
    return map;


        for (let building of buildings){
            L.marker([building.point__lat,building.point__lon]).addTo(markersGroup).bindPopup('<i>'+building.name+'</i><br><a class="btn btn-outline-info" data-bs-toggle="offcanvas " data-bs-target="#SideBar">informacion</a>')
        }*/
        /*
        for (let building of buildings){
            L.marker([building.point__lat,building.point__lon]).addTo(markersGroup).bindPopup('<i>'+building.name+'</i><br><a href="" onclick="alert(\'hola\')" >informacion</a>')
        }
        */
       /*
       for (let building of buildings){
            L.marker([building.point__lat,building.point__lon]).addTo(markersGroup).bindPopup('<i>'+building.name+'</i><br><button  onclick="HicieronClick2(\'hola\')" >informacion</button>')
        }
       */



        /*
        var layer1 = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19,attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'});

    var layer2 = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19,attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'});

    var overlayMaps = {
    "Capa 1": layer1,
    "Capa 2": layer2
    };

    var map = L.map('map', {
    center: center,
    zoom: zoom,
    layers: [layer1, layer2]
    });

    L.control.layers(null, overlayMaps).addTo(map);
    return map*/