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

var sendingFeedback = false;

function sendFeedback(url){
    if (sendingFeedback)
        return;
    sendingFeedback = true;
    getJSON(url, function(status, data){
        error = data["error"]
        message = data["message"]
        if (error){
            alert(error);
        } else if (message){
            alert(message);
        }
        sendingFeedback = false;
    });
}

