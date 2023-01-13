
window.onload = init;

function init() {
    major_group_elements = document.getElementsByClassName("btn btn-sm btn-outline-secondary mr-1 bg-primary text-white bg-info major_group");
    for (let i = 0, n=major_group_elements.length; i < n; ++i) {
        major_group_elements[i].addEventListener("click", function(event) {
            filterTags(major_group_elements[i].innerText, "major_group")
        });
    }
    minor_group_elements = document.getElementsByClassName("btn btn-sm btn-outline-secondary bg-light minor_group");
    for (let i = 0, n=minor_group_elements.length; i < n; ++i) {
        minor_group_elements[i].addEventListener("click", function(event) {
            filterTags(minor_group_elements[i].innerText, "minor_group")
        });
    }
}



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
    copiedNode.addEventListener('click', function(event) {
        unFilterTags(copiedNode.innerText, classType, copiedNode);
    });
    filter_element.appendChild(copiedNode);
    filter_element.parentNode.style.display = "inline";
    
}

function unFilterTags(tag, classType, callingElement) {
    const cards = document.getElementsByClassName("card mb-4 shadow-sm");
    for (let i = 0, n=cards.length; i < n; ++i) {
        tagElement = cards[i].getElementsByClassName(classType)[0];
        if(tagElement.innerText != tag) {
            cards[i].style.display = "flex";
        }
        
    }
    filter_element = document.getElementById("filterDivBlock");
    if (filter_element.children.length <= 1) {
        filter_element.parentNode.style.display = "none";
    };
    callingElement.remove();
}