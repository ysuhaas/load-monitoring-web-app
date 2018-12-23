$(document).ready(function () {
    // Connect to SocketIO server
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    console.log('Connected to server!');
    myChart = drawChart();

    //receive details from server
    socket.on('cpuUtil', function (msg) {
        console.log("Received new utilization datapoint: " + msg.util);
        // Construct a moment time object for this timestamp (ISO 8601)
        m = moment(msg.timestamp)
        // Add to chart
        addUtilDataPoint(msg.util, m, myChart);
    });
});

function drawChart() {
    // Global parameters:
    // do not resize the chart canvas when its container does (keep at 600x400px)
    Chart.defaults.global.responsive = true;

    var chartConfig = {
        type: 'line',
        data: {
            datasets: [{
                label: 'CPU Utilization',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 1)',
                fill: false,
                lineTension: 0,
                data: []
            }]
        },
        options: {
            title: {
                display: true,
                text: 'CPU Utilization'
            },
            scales: {
                xAxes: [{
                    type: 'realtime',
                    realtime: {
                        duration: 600000,
                        delay: 2000,
                        pause: false
                    }
                }],
                yAxes: [{
                    type: 'linear',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Utilization (%)'
                    },
                    ticks: {
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                }]
            },
            tooltips: {
                mode: 'nearest',
                intersect: false
            },
            hover: {
                mode: 'nearest',
                intersect: false
            },
            plugins: {
                streaming: {
                    frameRate: 30
                }
            }
        }
    }

    // get chart canvas
    var ctx = document.getElementById("myChart").getContext("2d");

    // create the chart using the chart canvas
    var myChart = new Chart(ctx, chartConfig);

    return myChart;
}

function addUtilDataPoint(util, timestamp, myChart) {
    // append the new data to the existing chart data
    myChart.data.datasets[0].data.push({
        x: timestamp,
        y: util
    });
    // console.log(JSON.stringify(myChart.data.datasets[0].data));

    // update chart datasets keeping the current animation
    myChart.update({
        preservation: true
    });
}

