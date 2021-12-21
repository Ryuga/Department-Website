
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function(){
        let event_ids = [];
        let event_names = [];

    $('.selectEvent').change(function(){
        if($(this).prop("checked") ==  true){
            event_ids.push($(this).attr("event_id"))
            event_names.push($(this).attr("value"))
    }else {
            let popIndex = event_ids.indexOf($(this).attr("event_id"));
            let namePopIndex = event_names.indexOf($(this).attr("value"));
            if (popIndex !== -1) {
                event_ids.splice(popIndex, 1);
            }
            if (namePopIndex !== -1) {
                event_names.splice(namePopIndex, 1)
            }
        }
    console.log(event_ids);
    console.log(event_names);
    })

});