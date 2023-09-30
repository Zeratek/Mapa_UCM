function HicieronClick(){
    let Hola = id;
    return alert(Hola);
};
function HicieronClick2(id){
    let urlF = '/buildinginfo/'+id
    fetch(urlF).then(response => response.json()).then(data=>{
        
    })
    return alert(urlF);
};

function HicieronClick3(id){
    let urlF = '/buildinginfo/'+id
    fetch(urlF).then(response => response.json()).then(data=>{
        document.getElementById("SideBarTitle").textContent  = data[0]['name'];
    })
};