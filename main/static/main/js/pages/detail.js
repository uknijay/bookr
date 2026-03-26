
function bookEvent() {
    var form = document.getElementById("bookForm");

    var xhttp = new XMLHttpRequest();
    var formData = new FormData(form);

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            
            var response = JSON.parse(this.responseText);

            document.getElementById("bookMessage").innerHTML = response.message;


            if (response.success) {
                document.getElementById("bookButton").disabled = true;
                document.getElementById("bookButton").value = "Booked";

                document.getElementById("capacityText").innerHTML = response.currentCapacity + "/" + response.maxCapacity;

                document.getElementById("capacityBar").style.width = response.capacityPercent + "%";
            }
        }
    };

    xhttp.open("POST", form.action, true);
    xhttp.send(formData);
}

function unbookEvent() {
    var form = document.getElementById("unbookForm");

    var xhttp = new XMLHttpRequest();
    var formData = new FormData(form);

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);

            document.getElementById("unbookMessage").innerHTML = response.message;

            if (response.success) {
                document.getElementById("unbookButton").innerHTML = "Unbooked";
                document.getElementById("unbookButton").disabled = true;

                document.getElementById("capacityText").innerHTML =
                    response.currentCapacity + "/" + response.maxCapacity;

                document.getElementById("capacityBar").style.width =
                    response.capacityPercent + "%";
            }
        }
    };

    xhttp.open("POST", form.action, true);
    xhttp.send(formData);
}

var bookForm = document.getElementById("bookForm");
if (bookForm) {
    bookForm.onsubmit = function(event) {
        event.preventDefault();
        bookEvent();
    };
}
var unbookForm = document.getElementById("unbookForm");
if (unbookForm) {
    unbookForm.onsubmit = function(event) {
        event.preventDefault();
        unbookEvent();
    };
}