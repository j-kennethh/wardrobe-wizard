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
    ev.target.appendChild(draggedItem.cloneNode(true));
}

document.querySelectorAll(".draggable-item").forEach(el => {
    el.addEventListener("dragstart", drag)
});