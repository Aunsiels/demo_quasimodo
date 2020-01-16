function makeCardVisible() {
    if (document.getElementById("tabooCard").classList.contains('d-none')){
       document.getElementById("tabooCard").classList.remove('d-none');
    }
}

function makeCardInvisible(){
    if (!document.getElementById("tabooCard").classList.contains('d-none')){
       document.getElementById("tabooCard").classList.add('d-none');
    }
}

// From https://stackoverflow.com/questions/12460378/how-to-get-json-from-url-in-javascript
var getJSON = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
      var status = xhr.status;
      if (status === 200) {
        callback(null, xhr.response);
      } else {
        callback(status, xhr.response);
      }
    };
    xhr.send();
};

function load_new_card(url){
    getJSON(url, function(status, data) {
        var word_to_guess = data["word_to_guess"];
        var forbidden_words = data["forbidden_words"];
        document.getElementById("card_title").innerHTML = word_to_guess;
        document.getElementById("forbidden_word0").innerHTML = forbidden_words[0];
        document.getElementById("forbidden_word1").innerHTML = forbidden_words[1];
        document.getElementById("forbidden_word2").innerHTML = forbidden_words[2];
        document.getElementById("forbidden_word3").innerHTML = forbidden_words[3];
        document.getElementById("forbidden_word4").innerHTML = forbidden_words[4];
        makeCardVisible();
        insertChat("you", "Here is your card", 0);
    });
}

function try_to_guess(url){
    getJSON(url, function(status, data) {
        var guessed = data["guessed"];
        var is_correct = data["is_correct"];

        if (guessed == "No idea"){
            insertChat("you", "I have no idea...");
        } else {
            insertChat("you", "I think it is " + guessed);
        }

        if (is_correct){
            insertChat("you", "I won!");
        }
    });
}