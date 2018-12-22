$(document).ready(function () {
    // Connect to SocketIO server
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    console.log('Connected to server!');
    drawChart();
    //receive details from server
    socket.on('cpuUtil', function (msg) {
        console.log("Received new utilization datapoint: " + msg.util);
        data = '' + '<p>' + msg.util.toString() + '</p>';
        $('#data').html(data);
    });
});

function drawChart() {
    // Global parameters:
    // do not resize the chart canvas when its container does (keep at 600x400px)
    Chart.defaults.global.responsive = true;

    // define the chart data
    var chartData = {
        labels: ["January", "February", "March", "April", "May", "June", "July", "August"],
        datasets: [{
            label: 'Monthly Data',
            fill: true,
            lineTension: 0.1,
            backgroundColor: "rgba(75,192,192,0.4)",
            borderColor: "rgba(75,192,192,1)",
            borderCapStyle: 'butt',
            borderDash: [],
            borderDashOffset: 0.0,
            borderJoinStyle: 'miter',
            pointBorderColor: "rgba(75,192,192,1)",
            pointBackgroundColor: "#fff",
            pointBorderWidth: 1,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: "rgba(75,192,192,1)",
            pointHoverBorderColor: "rgba(220,220,220,1)",
            pointHoverBorderWidth: 2,
            pointRadius: 1,
            pointHitRadius: 10,
            data: [10, 9, 8, 7, 6, 4, 7, 8],
            spanGaps: false
        }]
    }

    // get chart canvas
    var ctx = document.getElementById("myChart").getContext("2d");

    // create the chart using the chart canvas
    var myChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
    });
}

