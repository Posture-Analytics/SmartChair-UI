class App{
    constructor(){
        this.div = document.getElementById("content");
        this.div.innerHTML = ''
        this.graph = document.createElement("div");
        this.graph.id = "myPlot";
        this.div.appendChild(this.graph);
        this.dayData = {};
        this.lastMomentData = {};
        this.lastMoment = 0;
        this.times = [];
        this.chart = {};
        this.options = {
            series: {},
            chart: {
                id: 'realtime',
                height: 350,
                type: 'line',
                animations: {
                    enabled: true,
                    easing: 'linear',
                    dynamicAnimation: {
                        speed: 1000
                    }
                },
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                }
            },
            dataLabels: {
                enabled: false
            },
            stroke: {
                curve: 'smooth'
            },
            title: {
                text: 'Dynamic Updating Chart',
                align: 'left'
            },
            markers: {
                size: 0
            },
            xaxis: {
                type: 'datetime',
            },
            yaxis: {
                max: 5000
            },
            legend: {
                show: false
            }
        };
        
    }

    convertData(data){
        var series = [];
        // Transform the data
        Object.keys(data).forEach(function(timestamp) {
            var values = data[timestamp].P;

            values.forEach(function(value, index) {
                if (!series[index]) {
                    series[index] = { name: 'Series ' + (index + 1), data: [] };
                }
                series[index].data.push({ x: new Date(parseInt(timestamp)), y: value });
            });
        });

        this.options.series = series;

        console.table(series);

    }

    getDataDay(){
        fetch("/data")
        .then(response => response.json())
        .then(data => {
            console.log(data);
            this.times = Object.keys(data);
            this.times = Array.from(this.times);
            const l = this.times.length - 1;
            this.convertData(data);
            this.dayData = data;
            if (this.lastMoment < this.times[l]){ 
                this.plotTimesSeriesData();
            }
            this.lastMomentData = data[this.times[l]];
            this.lastMoment = this.times[l];
        });
    }
    

    plotTimesSeriesData(){;
        this.chart = new ApexCharts(this.div, this.options);
        this.chart.render();
    }

    // plotActualData(){
    //     const data = [{
    //         x: this.lastMomentData['p'].length,
    //         y: this.lastMomentData['p'],
    //         type: "bar",
    //         orientation:"v",
    //         marker: {color:"rgba(0,0,255)"}
    //     }];

    //     const layout = {title:"Valor dos sensores de pressão no último momento"};

    //     Plotly.newPlot("myPlot", data, layout);
    // }
}

let app = new App();

app.getDataDay();


window.setInterval(function() {
    app.getDataDay();
    // this.chart.updateSeries([ { data: app.options.series }]);
}, 10000);