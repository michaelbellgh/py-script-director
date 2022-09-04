function filterTags(tag, classType) {
    const cards = document.getElementsByClassName("card mb-4 shadow-sm");
    filtered_element = null;
    for (let i = 0, n=cards.length; i < n; ++i) {
        tagElement = cards[i].getElementsByClassName(classType)[0];
        if(tagElement.innerText != tag) {
            cards[i].style.display = "none";
        }
        else {
            filtered_element = tagElement;
        }
    }
    filter_element = document.getElementById("filterDivBlock");
    copiedNode = filtered_element.cloneNode(true);
    filter_element.appendChild(copiedNode);
    filter_element.parentNode.style.display = "inline";
}

function unFilterTags(tag, classType) {
    const cards = document.getElementsByClassName("card mb-4 shadow-sm");
    for (let i = 0, n=cards.length; i < n; ++i) {
        tagElement = cards[i].getElementsByClassName(classType)[0];
        if(tagElement.innerText == tag) {
            cards[i].style.display = "flex";
        }
        
    }
    copiedNode.removeEventListener('click', filterTags(tag, classType));
    copiedNode.addEventListener('click', function(event) {
        unFilterTags(tag, classType);
        copiedNode.remove();
    });
}