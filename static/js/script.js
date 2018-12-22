$(document).ready(function(){
    // Connect to SocketIO server
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    console.log('Connected to server!');
});