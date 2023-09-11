var globalTotalPages = null;
var fetchLinkUsable = null;
function show_list_table(tableID,filterIDS) {
    let tbody = document.querySelector(tableID);
    filterNombre = document.getElementById(filterIDS[0]); 
    filterOpcion = document.getElementById(filterIDS[1]); 
    let filterN = filterNombre.value;
    let filterO = filterOpcion.value;
    tbody.innerHTML = "";
    let fetchLink = flink;
    if (filterN.length === 0) {
        filterN = 'all';
    }
    fetchLink = fetchLink.replace("name", filterN);
    fetchLink = fetchLink.replace("option", filterO);
    fetchLinkUsable = fetchLink;
    fetch(fetchLink)
        .then(response => response.json())
        .then(data =>{
            //console.log(data.total_pages);
            globalTotalPages = data.total_pages
            updatePagination(data.total_pages, data.page);
            fillTable(data.data,'#EdificationTable tbody');
        });
};
function updatePagination(totalPages, currentPage) {
    //console.log(totalPages);
    //console.log(currentPage);
    let pagination = document.querySelector('#paginator');
    pagination.innerHTML = '';
    let startPage = Math.max(currentPage - 3, 1);
    let endPage = Math.min(currentPage + 3, totalPages);
    //console.log(startPage);
    //console.log(endPage);
    for (let i = startPage; i <= endPage; i++) {
        let a = document.createElement('button');
        a.classList.add('btn');
        a.classList.add('btn-outline-secondary');
        if (i === currentPage) {
            a.classList.add('active');
        }
        a.textContent = i;
        a.onclick =  function() {get_data_page_store_log_list(fetchLinkUsable,this.textContent);};
        pagination.appendChild(a);
    }
}
function get_data_page_store_log_list(linkU,pageNum) 
{
    let newLink = linkU+'?page='+pageNum;
    //console.log(newLink);
    //console.log(pageNum);
    fetch(newLink)
        .then(response => response.json())
        .then(data =>{
            //console.log(data);
            fillTable(data.data,'#EdificationTable tbody')
        });
    updatePagination(globalTotalPages,parseInt(pageNum));
}
function fillTable(Data,IdTable) {
    //console.log(Data);
    let tbody = document.querySelector(IdTable);
    let listLength = Data.length;
    tbody.innerHTML = "";
    //let dictLenght = Object.keys(Data[0]).length;
    for (let i = 0; i < listLength; i++)
    {
        let fila = tbody.insertRow();
        let cellNombre = fila.insertCell();
        let cellPertenece = fila.insertCell();
        let cellOpciones = fila.insertCell();
        cellNombre.innerHTML = Data[i].nombre;
        cellPertenece.innerHTML = Data[i].nombre_fk;
        let botonEstado = document.createElement('a');
        let id = Data[i].id;
        id = id.toString();
        botonEstado.href = LinkString.replace("id", id);
        botonEstado.classList.add('btn','btn-danger');
        botonEstado.textContent = 'Editar';
        let div = document.createElement('div');
        div.classList.add('d-grid','gap-2');
        div.appendChild(botonEstado);
        cellOpciones.appendChild(div);
    }
}