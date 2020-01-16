// From https://bootsnipp.com/snippets/6XlB5

var me = {};

var you = {};

function formatAMPM(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
}

//-- No use time. It is a javaScript effect.
function insertChat(who, text, time = 0){
    var control = "";
    var date = formatAMPM(new Date());

    if (who == "me"){

        control = '<li style="width:100%">' +
                        '<div class="msj macro">' +
                            '<div class="text text-l">' +
                                '<p>'+ text +'</p>' +
                                '<p><small>'+date+'</small></p>' +
                            '</div>' +
                        '</div>' +
                    '</li>';
    }else{
        control = '<li style="width:100%;">' +
                        '<div class="msj-rta macro">' +
                            '<div class="text text-r">' +
                                '<p>'+text+'</p>' +
                                '<p><small>'+date+'</small></p>' +
                            '</div>' +
                        '<div class="avatar" style="padding:0px 0px 0px 10px !important"></div>' +
                  '</li>';
    }
    setTimeout(
        function(){
            document.getElementById("chat-list").innerHTML += control;
        }, time);

}

function resetChat(){
    document.getElementById("chat-list").innerHTML = "";
}

$(".mytext").on("keyup", function(e){
    if (e.which == 13){
        var text = $(this).val();
        var url = $(this).attr("data-url");
        if (text !== ""){
            insertChat("me", text);
            url += "?word=" + encodeURI(text)
            getJSON(url, function(status, data) {})
            $(this).val('');
        }
    }
});

//-- Clear Chat
resetChat();
