class SimularClimaYBuscarPuntos {
    constructor(formId, saveBtnId) {
        this.dataGlobal = { puntos: null, clima: null, tiempo: null };
        this.form = document.getElementById(formId);
        this.saveBtn = document.getElementById(saveBtnId);

        this.inicializarEventos();
        this.gestionarInputsUbicacion('ciudad'); // Estado inicial
    }

    inicializarEventos() {
        this.form.addEventListener('submit', (e) => this.manejarSubmit(e));
        this.saveBtn.addEventListener('click', () => this.guardarJSON());
    }

    // --- LÓGICA DE INTERFAZ ---

    gestionarInputsUbicacion(metodo) {
        const config = {
            ciudad: ['input-ciudad'],
            coord: ['input-lat', 'input-lng'],
            cp: ['input-cp']
        };

        // Resetear todos
        Object.values(config).flat().forEach(id => {
            const el = document.getElementById(id);
            if (el) { el.disabled = true; el.required = false; }
        });

        // Activar seleccionados
        config[metodo].forEach(id => {
            const el = document.getElementById(id);
            if (el) { el.disabled = false; el.required = true; }
        });
    }

    toggleSection(sectionId) {
        const isChecked = document.getElementById('check' + sectionId.charAt(0).toUpperCase() + sectionId.slice(1)).checked;
        const card = document.getElementById('card-' + sectionId);
        const content = document.getElementById('content-' + sectionId);
        const inputs = content.querySelectorAll('input, select');

        if (isChecked) {
            card.classList.remove('opacity-75', 'border-secondary');
            card.classList.add('border-danger');
            content.style.display = 'block';
            inputs.forEach(i => i.disabled = false);
        } else {
            card.classList.add('opacity-75', 'border-secondary');
            card.classList.remove('border-danger');
            content.style.display = 'none';
            inputs.forEach(i => { i.disabled = true; i.value = ''; });
        }
    }

    // --- LÓGICA DE SIMULACIÓN ---

    manejarSubmit(event) {
        event.preventDefault();

        // Obtenemos valores de ubicación (el que no esté disabled)
        const city = document.getElementById('input-ciudad').value;
        const lat = document.getElementById('input-lat').value;
        const lng = document.getElementById('input-lng').value;
        const cp = document.getElementById('input-cp').value;

        // 1. Simular Geográfico si está activo
        if (document.getElementById('checkPois').checked) {
            this.simularContextoGeografico(city, cp, lat, lng);
        }

        // 2. Simular Ambiente si está activo
        if (document.getElementById('checkClima').checked) {
            this.simularContextoAmbiental(city, cp, lat, lng);
        }

        // 3. Simular Tiempo si está activo
        if (document.getElementById('checkTiempo').checked) {
            this.simularContextoTemporal();
        }
    }

    ////////////////////////// --- CONTEXTO TEMPORAL --- //////////////////////////
    simularContextoTemporal() {
        const hrMin = document.getElementById("hrMin").value;
        const hrMax = document.getElementById("hrMax").value;
        const cantTLibre = parseInt(document.getElementById("cantTLibre").value);
        const p1 = parseFloat(document.getElementById("prob1").value) / 100;
        const p2 = parseFloat(document.getElementById("prob2").value) / 100;
        const p3 = parseFloat(document.getElementById("prob3").value) / 100;
        const p4 = parseFloat(document.getElementById("prob4").value) / 100;
        const checkTL = document.getElementById('checkTL').checked;
        if (hrMin) {
            if (hrMax) {
                if (!Number.isNaN(cantTLibre)) {
                    checkTL ? this.generarHr_Tiempos(hrMin, hrMax, cantTLibre, p1, p2, p3, p4, 1) : this.generarHr_Tiempos(hrMin, hrMax, cantTLibre, p1, p2, p3, p4, 0);
                } else { alert("Debe ingresar una cantidad para generar los datos de tiempo libre"); }
            } else { alert("Debe ingresar una hora de fin"); }
        } else { alert("Debe ingresar una hora de inicio"); }

        /*if (city || cp || (lat || lon)) {
            if (lat || lon) {
                if (String(lat).trim() === "") {
                    alert("Debe ingresar una latitud valida");
                } else if (String(lon).trim() === "") {
                    alert("Debe ingresar una longitud valida");
                }
                else {
                    const esLatValida = isFinite(lat) && Math.abs(lat) <= 90;
                    const esLonValida = isFinite(lon) && Math.abs(lon) <= 180;
                    if (esLatValida) {
                        if (esLonValida) {
                            if (hrdesde) {
                                if (hrhasta) {
                                    this.generarHora(hrdesde, hrhasta, cantTLibre);
                                }
                                else {
                                    alert("Debe ingresar una hora de fin");
                                }
                            }
                            else {
                                alert("Debe ingresar una hora de inicio");
                            }
                        }
                        else {
                            alert("Debe ingresar una longitud valida");
                        }
                    }
                    else {
                        alert("Debe ingresar una latitud valida");
                    }
                }
                if (this.validarCoordenadas(lat, lon)) {
                    if (hrdesde) {
                        if (hrhasta) {
                            this.generarHora(hrdesde, hrhasta, cantTLibre);
                        }
                        else {
                            alert("Debe ingresar una hora de fin");
                        }
                    }
                    else {
                        alert("Debe ingresar una hora de inicio");
                    }
                }
            } else {
                if (hrdesde) {
                    if (hrhasta) {
                        this.generarHora(hrdesde, hrhasta, cantTLibre);
                    }
                    else {
                        alert("Debe ingresar una hora de fin");
                    }
                }
                else {
                    alert("Debe ingresar una hora de inicio");
                }
            }
        }
        else {
            alert("Debe ingresar una ubicación");
        }*/
    }

    validarCoordenadas(lat, lon) {
        // 1. Verificamos que los valores existan y no sean solo espacios
        if (String(lat).trim() === "") {
            alert("Debe ingresar una latitud valida");
            return false;
        } else if (String(lon).trim() === "") {
            alert("Debe ingresar una longitud valida");
            return false;
        } else {
            // 2. Convertimos a número (por si vienen como string desde el input)
            const ltaNum = Number(lat);
            const lonNum = Number(lon);

            // 3. Validamos rangos reales
            const latOk = !isNaN(ltaNum) && isFinite(ltaNum) && Math.abs(ltaNum) <= 90;
            const lonOk = !isNaN(lonNum) && isFinite(lonNum) && Math.abs(lonNum) <= 180;

            return latOk && lonOk;
        }
    }

    generarHr_Tiempos(hrdesde, hrhasta, cantTLibre, p1, p2, p3, p4, b) {
        //const tabla = document.getElementById('tablaUbicaciones');
        //const filas = tabla.rows;
        //const info = { hrdesde, hrhasta, filas };cantTLibre
        const info = { hrdesde, hrhasta, cantTLibre, p1, p2, p3, p4, b };
        this.postJSON('/simularContextoTemporal', info, (data) => {
            this.dataGlobal.tiempo = data;
            this.agregarTiempoLibreATablaCoord(data)
        });
        /*const tabla = document.getElementById('tablaUbicaciones');
        const filas = tabla.rows;
        const info = { hrdesde, hrhasta, filas };
        this.postJSON('/simularContextoTemporal', info, (data) => {
            this.dataGlobal.tiempo = data;
            this.agregarTiempoLibreATablaCoord(data);
        })*/
    };

    agregarTiempoLibreATablaCoord(data) {

        //const tabla = document.getElementById('tablaUbicaciones');
        const cuerpoTLibre = document.getElementById("tbodyTLibre");
        cuerpoTLibre.innerHTML = "";
        const cuerpoHora = document.getElementById("tbodyHora");
        cuerpoHora.innerHTML = "";

        const fila = `<tr>
                    <td>${data[0].hr_del_dia}</td>
                </tr>`;
        cuerpoHora.innerHTML += fila;

        data.forEach(item => {
            if (item.tiempo_libre) {
                const fila = `<tr>
                    <td>${item.tiempo_libre}</td>
                </tr>`;
                cuerpoTLibre.innerHTML += fila;
            }
        });

        /*const cuerpoUbi = document.getElementById("tbodyUbi"); // Tabla 1 (Referencia)
        const cuerpoTiempo = document.getElementById("tbodyTLibre"); // Tabla 2 (Destino) - Asegúrate que este ID exista en tu HTML
        const filasExistentesUbi = cuerpoUbi.rows;
        const cuerpoHr = document.getElementById("tbodyHora");
    
        // 1. Limpiamos la tabla de destino para que no se dupliquen datos si presionas el botón otra vez
        cuerpoTiempo.innerHTML = "";
        cuerpoHr.innerHTML = "";
    
        const nuevaFilaHr = document.createElement("tr");
        const nuevaCeldaHr = document.createElement("td");
    
        const infoHr = data[0].hr_del_dia;
        nuevaCeldaHr.innerText = infoHr;
    
        nuevaFilaHr.appendChild(nuevaCeldaHr);
        cuerpoHr.appendChild(nuevaFilaHr);
    
        // 2. Recorremos basándonos en la cantidad de filas de la primera tabla
        for (let i = 0; i < filasExistentesUbi.length; i++) {
    
            // Creamos una NUEVA fila para la Tabla 2
            const nuevaFila = document.createElement("tr");
            const nuevaCelda = document.createElement("td");
    
            // Buscamos el dato (empezando en data[1] según tu estructura)
            const infoTiempo = data[i + 1] ? data[i + 1].tiempo_libre : "N/A";
    
            nuevaCelda.innerText = infoTiempo;
    
            // Agregamos la celda a la nueva fila, y la fila al cuerpo de la Tabla 2
            nuevaFila.appendChild(nuevaCelda);
            cuerpoTiempo.appendChild(nuevaFila);
        }*/
    }





    ////////////////////////// --- CONTEXTO GEOGRAFICO --- //////////////////////////
    simularContextoGeografico(city, cp, lat, lon) {
        const category = document.getElementById("categories").value;
        const radio = document.getElementById("radio").value;
        const cant = parseInt(document.getElementById("cantPoints").value);

        const info = { city, cp, lat, lon, category, radio, cant };

        this.postJSON('/simularContextoGeografico', info, (data) => {
            this.dataGlobal.puntos = data;
            this.renderizarResultados(data);
        });
    }

    renderizarResultados(data) {
        const cuerpo = document.getElementById("tbodyUbi");
        cuerpo.innerHTML = "";

        data.forEach(item => {
            if (item.nombre) {
                const fila = `<tr>
                    <td>${item.nombre}</td>
                    <td>${item.lat}</td>
                    <td>${item.lon}</td>
                    <td><span class="badge ${item.en_UNSE ? 'bg-success' : 'bg-secondary'}">${item.en_UNSE}</span></td>
                </tr>`;
                cuerpo.innerHTML += fila;
            }
        });

        document.getElementById('mapaIframe').src = '/static/mapa.html';
        this.saveBtn.disabled = false;
    }

    ////////////////////////// --- CONTEXTO AMBIENTAL --- //////////////////////////

    simularContextoAmbiental(city, cp, lat, lng) {
        const checkTempHum = document.getElementById("checkTempHum").checked;

        if (city || cp || (lat && lng)) {
            if (lat && lng) {
                const esLatValida = isFinite(lat) && Math.abs(lat) <= 90;
                const esLonValida = isFinite(lng) && Math.abs(lng) <= 180;
                if (esLatValida) {
                    if (esLonValida) {
                        checkTempHum ? this.checkboxTempHum() : this.noncheckboxTempHum(city, cp, lat, lng);
                    }
                    else {
                        alert("Debe ingresar una longitud valida");
                    }
                }
                else {
                    alert("Debe ingresar una latitud valida");
                }
            }
            checkTempHum ? this.checkboxTempHum() : this.noncheckboxTempHum(city, cp, lat, lng);
        }
        else {
            alert("Debe ingresar una ubicación");
        }
    }

    checkboxTempHum() {
        const info = this.obtenerDatosTempHum();
        this.postJSON('/checkboxTempHum', info, (data) => {
            this.dataGlobal.clima = data;
            this.agregarTempHumTabla(data);
        });
    }

    noncheckboxTempHum(city, cp, lat, lng) {
        const ciudad = city || cp; // Si city tiene valor, lo usa; si no, usa cp. En caso tener valor ambos se queda con city por ser el primero.
        this.postJSON('/noncheckboxTempHum', { ciudad, lat, lng }, (data) => {
            this.dataGlobal.clima = data;
            this.agregarTempHumTabla(data);
        });
    }

    obtenerDatosTempHum() {
        if (!Number.isNaN(parseFloat(document.getElementById("tempMin").value))) {
            if (!Number.isNaN(parseFloat(document.getElementById("tempMax").value))) {
                if (!Number.isNaN(parseFloat(document.getElementById("humDes").value))) {
                    if (!Number.isNaN(parseFloat(document.getElementById("humFluc").value))) {
                        return {
                            tempmin: parseFloat(document.getElementById("tempMin").value),
                            tempmax: parseFloat(document.getElementById("tempMax").value),
                            humDeseada: parseFloat(document.getElementById("humDes").value),
                            humFluctuacion: parseFloat(document.getElementById("humFluc").value)
                        };
                    } else {
                        alert("Debe ingresar un valor de Fluctuación de humedad");
                    }
                } else {
                    alert("Debe ingresar un valor Deseado de humedad");
                }
            } else {
                alert("Debe ingresar un valor de Teperatura Máxima");
            }
        } else {
            alert("Debe ingresar un valor de Temperatura Mínima");
        }
    }

    agregarTempHumTabla(data) {
        const cuerpo = document.getElementById("tbodyAmb");
        cuerpo.innerHTML = "";

        const fila = `<tr>
                    <td>${parseInt(data[0].temp)}ºC</td>
                    <td>${parseInt(data[0].hum)} %</td>
                </tr>`;
        cuerpo.innerHTML += fila;

        this.saveBtn.disabled = false;
    }


    async postJSON(url, data, callback) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (!response.ok) throw new Error('Error en el servidor');
            const json = await response.json();
            callback(json);
        } catch (error) {
            console.error(error);
            alert("Error al conectar con el servidor Flask");
        }
    }

    guardarJSON() {
        const contenido = JSON.stringify(this.dataGlobal, null, 2);
        const blob = new Blob([contenido], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'escenario_sintetico.json';
        a.click();
    }
}

// Inicialización global
let simulador;
document.addEventListener('DOMContentLoaded', () => {
    simulador = new SimularClimaYBuscarPuntos('simuladorForm', 'savebtn');
});