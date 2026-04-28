class UbicacionApp {
    constructor(formId, tablaId, cuerpoTablaId){
        this.form = document.getElementById(formId);
        this.tabla = document.getElementById(tablaId);
        this.cuerpo = document.getElementById(cuerpoTablaId);

        this.form.addEventListener('submit', (event) => this.manejarSubmit(event))
    }

    manejarSubmit(event){
        event.preventDefault(); // Evita que el formulario se envíe y la página se recargue provocando que los datos se muestren rapidamente
        this.generarUbicacion();
    }

    generarUbicacion() {
        //const mu = parseFloat(document.getElementById("mu").value);
        //const sigma = parseFloat(document.getElementById("sigma").value);
        const latitude = parseFloat(document.getElementById("latitude").value);
        const longitude = parseFloat(document.getElementById("longitude").value);
        const cantCoord = parseInt(document.getElementById("cantCoord").value);
        const info = {
            latitude: latitude,
            longitude: longitude,
            cantCoord: cantCoord
        };
        fetch('/api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(info),
        })
            .then(response => {
                if (!response.ok) throw new Error ('Error ${response.status}');
                return response.json();
            })
            .then(data => 
                this.agregarInfoTablaUbiAleatorias(data)
            )
            .catch((error) => 
                console.error('Error: ', error)
            );
        }

    agregarInfoTablaUbiAleatorias(data) {
        this.cuerpo.innerHTML = "";
        Object.values(data).forEach(element => {
            Object.values(element).forEach((p, index) => {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${p.Lat}</td>
                    <td>${p.Lon}</td>
                `;
                this.cuerpo.appendChild(fila);
            });
        });
        this.tabla.appendChild(this.cuerpo);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new UbicacionApp('ubiForm', 'tablaLista', 'tbodyapi');
});