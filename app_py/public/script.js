class App{
    constructor(){
        this.div = document.getElementById("content");;
    }

    getDataDay(){
        fetch("/data")
        .then(response => response.json())
        .then(data => {
            data = data[0]
            // const keys = Object.keys(data)
            // const l = keys.length - 1
            // this.plotActualData(data[keys[l]]);
            this.renderData(data);
        });
    }

    renderData(data){
        console.log(data);
        // let html = "";
        // for(let i = 0; i < data.length; i++){
        //     html += `<p>${data[i].name}</p>`;
        // }
        // this.div.innerHTML = html;
    }

    plotActualData(data){
        
    }
}

let app = new App();

app.getDataDay();