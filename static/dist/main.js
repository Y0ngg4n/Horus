function SearchAndFilter() {
    var input = document.getElementById("search-bar");
    var filter = input.value.toUpperCase();
    var items = document.getElementsByClassName("service-item");
    var groups = document.getElementsByClassName("service-item-group");
    for (let x = 0; x < items.length; x++) {
        let url = items[x].getElementsByClassName("service-item-url")[0]
        let item_name = items[x].getElementsByClassName("service-item-name")[0]
        let description = items[x].getElementsByClassName("service-item-description")[0]
        let group_item = items[x].parentElement.parentElement
        let group_item_label = group_item.getElementsByClassName("service-item-group-label")[0]
        if ((item_name && item_name.innerHTML.toUpperCase().indexOf(filter) > -1)
            || (description && description.innerHTML.toUpperCase().indexOf(filter) > -1)
            || (url && url.innerHTML.toUpperCase().indexOf(filter) > -1)
            || (group_item_label && group_item_label.innerHTML.toUpperCase().indexOf(filter) > -1)) {
            items[x].style.display = "";
        } else {
            items[x].style.display = "none";
        }
    }

    for (let x = 0; x < groups.length; x++) {
        let serviceItems = groups[x].getElementsByClassName("service-item");
        let count = 0;
        for (let z = 0; z < serviceItems.length; z++) {
            if (serviceItems && serviceItems[z] && serviceItems[z].style.display === "") {
                count++;
            }
        }
        if (count > 0) {
            groups[x].style.display = "";
        } else {
            groups[x].style.display = "none";
        }
    }
}
