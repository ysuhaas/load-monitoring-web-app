$(document).ready(function(){
    // Connect to SocketIO server
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    console.log('Connected to server!');

    //receive details from server
    socket.on('cpuUtil', function(msg) {
        console.log("Received new utilization datapoint: " + msg.util);
        data = '' + '<p>' + msg.util.toString() + '</p>';
        $('#data').html(data);
    });
});