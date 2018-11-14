function show() {
    document.getElementById("overDiv").style.display = "block";
    document.getElementById("hsDiv").style.display = "block";
}

function closeDiv() {
    document.getElementById("overDiv").style.display = "none";
    document.getElementById("hsDiv").style.display = "none";
}

$("#category").change(function () {
    var url = $("#category").val();
    if (url == 'more') {
        $("#edui1").css({
            "position": "fixed !important",
            "filter": "alpha(opacity=65)",
            "opacity": "0.65",
            "z-index": "110",
            "position": "absolute"
        });

        show();
        $("#content_sub").css('margin-top', '610px');
    }
})