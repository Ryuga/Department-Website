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
$(document).ready(function (){
    $('.selectEvent').click(function(e) {
        e.stopPropagation(); // Prevent the click event from propagating to the card
    });
    $('.programItemCard').click(function() {
        let checkbox = $(this).find('.selectEvent');
        checkbox.prop('checked', !checkbox.prop('checked'))
        checkbox.change();
    });
});

$(document).ready(function(){
        let event_ids = [];
        let event_names = [];
        let total_price = 0;

    $('.selectEvent').change(function(){
        if($(this).prop("checked") ===  true){
            event_ids.push($(this).attr("event_id"))
            event_names.push([$(this).attr("value"), $(this).attr("price")])
            $(this).closest(".card").addClass("bg-success-subtle")
        }else {
            let popIndex = event_ids.indexOf($(this).attr("event_id"));
            let namePopIndex = event_names.findIndex(item => item[0] === $(this).attr("value") && item[1] === $(this).attr("price"));
            if (popIndex !== -1) {
                event_ids.splice(popIndex, 1);
            }
            if (namePopIndex !== -1) {
                event_names.splice(namePopIndex, 1)
            }
            $(this).closest(".card").removeClass("bg-success-subtle")
        }
        let x = ``;
        total_price = 0;
        $.each(event_names, function (i, value){
            x +=
            `
            <tr>
                  <td>${value[0]}</td>
                  <td>${value[1]}</td>
            </tr>
            `
            total_price+=parseInt(value[1]);
        });
        $('.costSummary').html(x);
        $('.totalPrice').html(total_price);
    })

    $('#makePaymentBtn').click(function (){
        if ((event_ids !== undefined || event_ids.length !== 0) && (total_price !== 0)) {
            $("#modalTxnAmt").val(total_price);
            $("#modalEventsList").val(event_ids);
            $("#paymentConfirmationModal").modal('show');
        }
    });

});

$(document).ready(function (){
    $('#SearchBtn').click(function (){
        let csrftoken = getCookie("csrftoken")
        let reg_id = $('#regIdInput').val();
        $.ajax({
        url: `/event/registration/details/${reg_id}/?ajax=true`,
        headers: {'X-CSRFToken': csrftoken},
        type: 'GET',
        success:function (data)
        {
            $('#userDataRefresh').html(data);
        },
        });
    })
    $('#allotIdBtn').click(function (){
        let csrftoken = getCookie("csrftoken")
        let reg_id = $('#regIdInput').val();
        $.ajax({
        url: `/event/registration/details/${reg_id}/?allot=true`,
        headers: {'X-CSRFToken': csrftoken},
        type: 'GET',
        success:function (data)
        {
            $('#userDataRefresh').html(data);
        },
        });
    });
})

$(document).ready(function (){
    $('#checkEmailBtn').click(function (){
        let csrftoken = getCookie("csrftoken")
        let email = $('#registrationEmailId').val();
        let event_link = $('#registrationEventLink').val();
        console.log(event_link)
        $.ajax({
        url: `/${event_link}/registration/?ajax=true&email=${email}`,
        headers: {'X-CSRFToken': csrftoken},
        type: 'GET',
        success:function (data)
        {
            $('#eventRegistrationCardSection').html(data);
        },
        });
    })
    $(".alert-dismissible").fadeTo(2000, 500).slideUp(500, function(){
    $(".alert-dismissible").alert('close');
});
})

$(document).ready(function (){
    $('.deleteAccCheckBox').change(function() {
        if ($(this).prop("checked") === true) {
            $("#deleteAccBtn").removeClass("disabled");
        }
        else {
            $("#deleteAccBtn").addClass("disabled");
        }
    });
    $('#deleteAccBtn').click(function (){
        let csrftoken = getCookie("csrftoken")
        $.ajax({
        url: `/settings/`,
        headers: {'X-CSRFToken': csrftoken},
        type: 'DELETE',
        success:function (data)
        {
            location.reload(true)
        },
        error: function (resp){
            if(resp.status == 406) {
                $("#banAccAlert").fadeTo(5000, 500).slideUp(500, function () {
                    $("#banAccAlert").alert("close")
                });
            }
            else {
                $("#deleteAccAlert").fadeTo(2000, 500).slideUp(500, function () {
                    $("#deleteAccAlert").alert("close")
                });
            }
        }
        });
    });
});

function getPageLoadCount() {
  const cookieValue = document.cookie.replace(/(?:(?:^|.*;\s*)pageLoads\s*\=\s*([^;]*).*$)|^.*$/, "$1");
  return parseInt(cookieValue) || 0;
}

function setPageLoadCount(count) {
  const expirationDate = new Date();
  expirationDate.setDate(expirationDate.getDate() + 1); // Cookie will expire in 1 day
  const cookieString = `pageLoads=${count}; expires=${expirationDate.toUTCString()}; path=/`;
  document.cookie = cookieString;
}

function trackPageLoadForAccustom() {
  const currentLoadCount = getPageLoadCount();
  if (currentLoadCount < 3) {
      setPageLoadCount(currentLoadCount + 1);
      return false
  }
  return true
}