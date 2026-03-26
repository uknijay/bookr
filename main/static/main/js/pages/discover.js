$(document).ready(function () {
$("#discover-search-form").on("submit", function (e) {
    e.preventDefault();

    const form = $(this);
    const url = form.attr("action");
    const data = form.serialize();

    $.ajax({
    url: url,
    type: "GET",
    data: data,
    headers: {
        "X-Requested-With": "XMLHttpRequest"
    },
    success: function (response) {
        $("#discover-results").html(response);

    },
    error: function () {
        alert("Search failed | Please try again.");
    }
    });
});
});