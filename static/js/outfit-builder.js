let selectedItems = [];

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    const data = ev.dataTransfer.getData("text");
    const draggedItem = document.getElementById(data);
    
    const clone = draggedItem.cloneNode(true);
    document.getElementById("canvas").appendChild(clone);

    selectedItems.push(data);
}

document.querySelectorAll(".draggable-item").forEach(el => {
    el.addEventListener("dragstart", drag)
});

document.getElementById("saveOutfitForm").addEventListener("submit", function () {
    document.getElementById("item_ids").value = JSON.stringify(selectedItems);
});