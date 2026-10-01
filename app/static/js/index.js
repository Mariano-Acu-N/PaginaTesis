class SimularClimaPuntosYHoras {
    constructor(formId, saveBtnId) {
        //this.dataGlobal = {id_Simulacion: null, fechaHora_Simulacion:null, ubicacion: null, clima: null, tiempo: null };
        this.dataGlobal = {id_Simulacion: null, ubicacion: null, clima: null, tiempo: null };
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
        this.metodoUbicacionActual = metodo; // Guardamos si es 'ciudad', 'coord' o 'cp'

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

            // 1. Habilitamos todos los inputs base (incluyendo los radio buttons)
            inputs.forEach(i => i.disabled = false);

            // 2. Aplicamos filtros específicos según la sección
            if (sectionId === 'tiempo') {
                // Si es Tiempo, decide si bloquea probabilidades (Laplace vs Manual)
                this.actualizarInterfazTemporal();
            }
            else if (sectionId === 'clima') {
                // Si es Clima, decide si bloquea temperatura/humedad (API vs Manual)
                this.actualizarInterfazClima();
            }

        } else {
            card.classList.add('opacity-75', 'border-secondary');
            card.classList.remove('border-danger');
            content.style.display = 'none';
        }
    }

    actualizarInterfazTemporal() {
        // Verificamos si la opción seleccionada es Laplace
        const metodoObtencionTiempo = document.getElementById('radioLaplace').checked;
        // Obtenemos todos los inputs dentro del contenedor de probabilidades
        const inputsProb = document.querySelectorAll('#grupo-probabilidades input');
        inputsProb.forEach(input => {
            // Bloqueamos si es Laplace, habilitamos si es Manual
            input.disabled = metodoObtencionTiempo;
            if (metodoObtencionTiempo) {
                // Opcional: Limpiar el valor o mostrar un indicador de que se usarán valores internos
                input.value = "";
                input.classList.add('bg-light'); // Le da un tono grisáceo para notar el bloqueo
            } else {
                input.classList.remove('bg-light');
                input.focus(); // Opcional: poner el foco en el primero para invitar a escribir
            }
        });
    }

    actualizarInterfazClima() {
        // 1. Detectamos si la opción "API" está marcada
        const metodoObtencionClima = document.getElementById('radioClimaAPI').checked;

        // 2. Buscamos todos los inputs de la sección ambiente
        const inputs = document.querySelectorAll('#grupo-clima-inputs input');

        inputs.forEach(input => {
            // 3. Si es API, desactivamos (disabled = true). Si es Manual, activamos (false)
            input.disabled = metodoObtencionClima;

            if (metodoObtencionClima) {
                input.value = ""; // Limpiamos para que no queden datos viejos
                input.classList.add('bg-light'); // Efecto visual de campo bloqueado
            } else {
                input.classList.remove('bg-light'); // Restauramos el aspecto normal
            }
        });
    }

    // --- LÓGICA DE SIMULACIÓN ---
    async manejarSubmit(event) {
        event.preventDefault();

        // 1. Declaramos las variables vacías
        let city = null;
        let lat = null;
        let lon = null;
        let cp = null;
        
        // Endpoint explícito para reiniciar la variable primera_sim en el backend antes de ejecutar la simulación
        await fetch('/reiniciarSimulacion', { method: 'POST' });
        
        // 2. Capturamos DATOS ÚNICAMENTE de la solapa activa
        // Esto evita que si hay algo escrito en "Coordenadas" pero estás en "Ciudad", se mezcle.
        if (this.metodoUbicacionActual === 'ciudad') {
            city = document.getElementById('input-ciudad').value;
            const info = { city };
            await this.postJSON('/obtenerLatLon', info, (data) => {
                lat = data.lat;
                lon = data.lng;
                
                const esLatValida = isFinite(lat) && Math.abs(lat) <= 90;
                const esLonValida = isFinite(lon) && Math.abs(lon) <= 180;
            
                if (!esLatValida) {
                    Swal.fire({
                    title: '¡Atención!',
                    text: 'Coordenada de latitud inválida',
                    icon: 'warning',
                    confirmButtonText: 'Aceptar',
                    confirmButtonColor: '#3085d6'
                });
                return; // Cortamos la ejecución si no hay ubicación
                }
                else if (!esLonValida) {
                    Swal.fire({
                    title: '¡Atención!',
                    text: 'Coordenada de longitud inválida',
                    icon: 'warning',
                    confirmButtonText: 'Aceptar',
                    confirmButtonColor: '#3085d6'
                });
                return; // Cortamos la ejecución si no hay ubicación
                }
            });
        }
        else if (this.metodoUbicacionActual === 'coord') {
            lat = document.getElementById('input-lat').value;
            lon = document.getElementById('input-lng').value;
            // Validación de Coordenadas
            if (lat && lon) {
                const esLatValida = isFinite(lat) && Math.abs(lat) <= 90;
                const esLonValida = isFinite(lon) && Math.abs(lon) <= 180;
            
            if (!esLatValida) {
                Swal.fire({
                title: '¡Atención!',
                text: 'Coordenada de latitud inválida',
                icon: 'warning',
                confirmButtonText: 'Aceptar',
                confirmButtonColor: '#3085d6'
            });
            return; // Cortamos la ejecución si no hay ubicación
            }
            else if (!esLonValida) {
                Swal.fire({
                title: '¡Atención!',
                text: 'Coordenada de longitud inválida',
                icon: 'warning',
                confirmButtonText: 'Aceptar',
                confirmButtonColor: '#3085d6'
            });
            return; // Cortamos la ejecución si no hay ubicación
            }
        }
        }
        //else if (this.metodoUbicacionActual === 'cp') {
        else if (this.metodoUbicacionActual === 'cp') {
            cp = document.getElementById('input-cp').value;
            // Validación de codigo postal
            if (!this.validarFormatoCodigoPostal(cp)) {
                Swal.fire({
                title: '¡Atención!',
                text: 'Formato inválido del Código Postal (ejemplo de formato válido 4200, Argentina)',
                icon: 'warning',
                confirmButtonText: 'Aceptar',
                confirmButtonColor: '#3085d6'
            });
            return; // Detiene la ejecución si no hay opciones activas
            }
            const info = { cp };
            await this.postJSON('/obtenerLatLon', info, (data) => {
                lat = data.lat;
                lon = data.lng;
            });
        }

        // 3. Ejecución condicional (Solo si el switch está ON y no hay datos previos)
        // Usamos las validaciones para no repetir simulaciones ya hechas

        // --- SIMULACIÓN GEOGRÁFICA ---
        if (document.getElementById('checkPois').checked) {
            this.simularContextoGeografico(lat, lon);
        }
        // --- SIMULACIÓN AMBIENTAL ---
        if (document.getElementById('checkClima').checked) {
        // Pasamos los datos de ubicación por si el clima depende de la zona
            this.simularContextoAmbiental(lat, lon);
        }
        // --- SIMULACIÓN TEMPORAL ---
        if (document.getElementById('checkTiempo').checked) {
            this.simularContextoTemporal(lat, lon);
        }

        if (!document.getElementById('checkPois').checked && !document.getElementById('checkClima').checked && !document.getElementById('checkTiempo').checked) {
            Swal.fire({
                title: '¡Atención!',
                text: 'Para comenzar la generación de los datos debe seleccionar una de las opciones configurables.',
                icon: 'warning',
                confirmButtonText: 'Aceptar',
                confirmButtonColor: '#3085d6'
            });
            return; // Detiene la ejecución si no hay opciones activas
        }
    }

    ////////////////////////// --- CONTEXTO TEMPORAL --- //////////////////////////
    simularContextoTemporal(lat, lng) {
        // inicio = performance.now();
        const hrMin = document.getElementById("hrMin").value;
        const hrMax = document.getElementById("hrMax").value;
        const cantDatosT = parseInt(document.getElementById("cantDatosT").value);
        const p1 = parseFloat(document.getElementById("prob1").value);
        const p2 = parseFloat(document.getElementById("prob2").value);
        const p3 = parseFloat(document.getElementById("prob3").value);
        const p4 = parseFloat(document.getElementById("prob4").value);
        const metodoObtencionTiempo = document.getElementById('radioLaplace').checked;
        if (this.validarHora(hrMin)) {
            if (this.validarHora(hrMax)) {
                if(this.horaAMinutos(hrMin) <= this.horaAMinutos(hrMax)) {
                    metodoObtencionTiempo ? this.generarHr_Tiempos(hrMin, hrMax, cantDatosT, p1, p2, p3, p4, lat, lng, 0) : this.validarProbTransInvDisc(hrMin, hrMax, cantDatosT, p1, p2, p3, p4, lat, lng, 1)
                } else {
                    Swal.fire({
                        title: '¡Atención!',
                        text: 'La hora máxima debe ser mayor que hora mínima',
                        icon: 'warning',
                        confirmButtonText: 'Aceptar',
                        confirmButtonColor: '#3085d6'
                    });
                }
            } else {
                Swal.fire({
                    title: '¡Atención!',
                    text: 'Por favor, indique la hora de fin para el contexto temporal.',
                    icon: 'warning',
                    confirmButtonText: 'Aceptar',
                    confirmButtonColor: '#3085d6'
                });
            }
        } else {
            Swal.fire({
                title: '¡Atención!',
                text: 'Por favor, indique la hora de inicio para el contexto temporal.',
                icon: 'warning',
                confirmButtonText: 'Aceptar',
                confirmButtonColor: '#3085d6'
            });
        }
    }

    validarHora(horaTexto) {
        // Expresión regular para HH o HH:MM
        const regex = /^([01]\d|2[0-3])(:[0-5]\d)?$/; // "24:00" = false (Hora inválida), "12:60" = false (Minuto inválido), "hola" = false
        return regex.test(horaTexto);
    }

    horaAMinutos(entrada) {
        // Si ya es un número o un texto sin ":", asumimos que son solo horas
        if (!String(entrada).includes(':')) {
            return Number(entrada) * 60;
        }
        
        // Si tiene ":", separamos horas y minutos
        const [horas, minutos] = entrada.split(':').map(Number);
        return (horas * 60) + minutos;
    }

    validarProbTransInvDisc(hrdesde, hrhasta, cantDatosT, p1, p2, p3, p4, lat, lng, b) {
        let totalProb = 0;
        if (!Number.isNaN(p1)) {
            if (!Number.isNaN(p2)) {
                if (!Number.isNaN(p3)) {
                    if (!Number.isNaN(p4)) {
                        totalProb = p1 + p2 + p3 + p4;
                        if (totalProb === 100) {
                            const prob1 = p1 / 100;
                            const prob2 = p2 / 100;
                            const prob3 = p3 / 100;
                            const prob4 = p4 / 100;
                            this.generarHr_Tiempos(hrdesde, hrhasta, cantDatosT, prob1, prob2, prob3, prob4, lat, lng, b);
                        } else {
                            Swal.fire({
                                title: '¡Atención!',
                                text: 'La suma de las probabilidades debe ser igual a 100%',
                                icon: 'warning',
                                confirmButtonText: 'Aceptar',
                                confirmButtonColor: '#3085d6'
                            });
                        }
                    } else {
                        Swal.fire({
                            title: '¡Atención!',
                            text: 'Debe ingresar una probabilidad para 1 hr o más',
                            icon: 'warning',
                            confirmButtonText: 'Aceptar',
                            confirmButtonColor: '#3085d6'
                        });
                    }
                } else {
                    Swal.fire({
                        title: '¡Atención!',
                        text: 'Debe ingresar una probabilidad para 30-50 min',
                        icon: 'warning',
                        confirmButtonText: 'Aceptar',
                        confirmButtonColor: '#3085d6'
                    });
                }
            } else {
                Swal.fire({
                    title: '¡Atención!',
                    text: 'Debe ingresar una probabilidad para 15-30 min',
                    icon: 'warning',
                    confirmButtonText: 'Aceptar',
                    confirmButtonColor: '#3085d6'
                });
            }
        } else {
            Swal.fire({
                title: '¡Atención!',
                text: 'Debe ingresar una probabilidad para < 15 min',
                icon: 'warning',
                confirmButtonText: 'Aceptar',
                confirmButtonColor: '#3085d6'
            });
        }
    }

    generarHr_Tiempos(hrdesde, hrhasta, cantDatosT, p1, p2, p3, p4, lat, lng, b) {
        const info = { hrdesde, hrhasta, cantDatosT, p1, p2, p3, p4, lat, lng, b };
        this.postJSON('/simularContextoTemporal', info, (data) => {
            this.consolidarDatosSimulados(data, 3);
            this.agregarTiempoLibreATablaCoord(data.tiempo)
        });
    };

    agregarTiempoLibreATablaCoord(data) {
        const cuerpoTLibre = document.getElementById("tbodyTLibre");
        cuerpoTLibre.innerHTML = "";
        const cuerpoHora = document.getElementById("tbodyHora");
        cuerpoHora.innerHTML = "";

        data.forEach(item => {
            if (item.hr_del_dia) {
                const fila = `<tr>
                    <td>${item.hr_del_dia}</td>
                </tr>`;
                cuerpoHora.innerHTML += fila;
            }
        });

        data.forEach(item => {
            if (item.tiempo_libre) {
                const fila = `<tr>
                    <td>${item.tiempo_libre}</td>
                </tr>`
                ;
                cuerpoTLibre.innerHTML += fila;
            }
        });

        document.getElementById('mapaIframe').src = '/static/mapa.html';
        this.saveBtn.disabled = false;
    }

    ////////////////////////// --- CONTEXTO GEOGRAFICO --- //////////////////////////
    simularContextoGeografico(lat, lon) {

        const category = document.getElementById("categories").value;
        const radio = document.getElementById("radio").value;
        //const cantPoints = parseInt(document.getElementById("cantPoints").value);
        const cantPuntos = document.getElementById("cantPuntos").value;
        if (radio.trim() !== "") {
            if (cantPuntos.trim() !== "") {
                if (category.trim() !== "") {
                    const info = { lat, lon, category, radio, cantPuntos };
                    this.postJSON('/simularContextoGeografico', info, (data) => {
                        this.consolidarDatosSimulados(data, 1);
                        this.renderizarResultados(data.puntosGeograficos);
                    });
                } else {
                    Swal.fire({
                        title: '¡Atención!',
                        text: 'Debe seleccionar una categoría de la lista',
                        icon: 'warning',
                        confirmButtonText: 'Aceptar',
                        confirmButtonColor: '#3085d6'
                    });

                }
            } else {
                Swal.fire({
                    title: '¡Atención!',
                    text: 'Debe ingresar la cantidad de datos/puntos a generar para continuar.',
                    icon: 'warning',
                    confirmButtonText: 'Aceptar',
                    confirmButtonColor: '#3085d6'
                });
            }
        } else {
            Swal.fire({
                title: '¡Atención!',
                text: 'Debe ingresar los metros a la redonda para la búsqueda',
                icon: 'warning',
                confirmButtonText: 'Aceptar',
                confirmButtonColor: '#3085d6'
            });

        }
    }

    validarFormatoCodigoPostal(texto) {
        // Patrón: Código alfanumérico (3-10 caracteres), coma, espacio opcional, y nombre de país
        const patron = /^[A-Za-z0-9\-\s]{3,10},\s*[A-Za-zÀ-ÿ\s'\-]+$/;
    
        // .trim() limpia espacios sobrantes al inicio y al final
        return patron.test(texto.trim());
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
    simularContextoAmbiental(lat, lng) {

        // 1. Verificamos cuál método está seleccionado (API o Manual)
        const metodoObtencionClima = document.getElementById("radioClimaAPI").checked;

        // 2. Lógica de Disparo
        const cantAmb = document.getElementById("cantAmb").value;
        if (metodoObtencionClima) {
            // Si es API, llamamos a tu función que busca datos reales (OpenWeather, etc.)
            this.simularContextoAmbienteAPI(lat, lng, cantAmb);
        } else {
            // Si es Manual, llamamos a la función que captura tus inputs (T. Min, T. Max, etc.)
            const tempmin = parseFloat(document.getElementById("tempMin").value)
            const tempmax = parseFloat(document.getElementById("tempMax").value);
            const humDeseada = parseFloat(document.getElementById("humDes").value);
            const humFluctuacion = parseFloat(document.getElementById("humFluc").value);
            this.validarDatosTempHum(tempmin, tempmax, humDeseada, humFluctuacion, lat, lng, cantAmb);
        }
    }

    validarDatosTempHum(tempmin, tempmax, humDeseada, humFluctuacion, lat, lng, cantAmb) {
                    if (tempmax > tempmin) {
                        this.simularContextoAmbienteManual(tempmin, tempmax, humDeseada, humFluctuacion, lat, lng, cantAmb);
                    } else {
                        Swal.fire({
                            title: '¡Atención!',
                            text: 'La temperatura máxima debe ser mayor que la mínima',
                            icon: 'warning',
                            confirmButtonText: 'Aceptar',
                            confirmButtonColor: '#3085d6'
                        });
                    }
    }

    simularContextoAmbienteManual(tempmin, tempmax, humDeseada, humFluctuacion, lat, lng, cantAmb) {
        // const inicio = performance.now();
        const info = { tempmin, tempmax, humDeseada, humFluctuacion, lat, lng, cantAmb};
        this.postJSON('/simularContextoAmbienteManual', info, (data) => {
            this.consolidarDatosSimulados(data, 2);
            this.agregarTempHumTabla(data.clima);
        });
    }

    simularContextoAmbienteAPI(lat, lng, cantAmb) {
        const info = { lat, lng, cantAmb }
        this.postJSON('/simularContextoAmbienteAPI', info, (data) => {
            this.consolidarDatosSimulados(data, 2);
            this.agregarTempHumTabla(data.clima);
        });
    }

    agregarTempHumTabla(data) {
        const cuerpo = document.getElementById("tbodyAmb");
        cuerpo.innerHTML = "";
        // data[0].temp así para que muestre el decimal de la temperatura, el dato ya viene como float
        data.forEach(item => {
            if (item.temp) {
                const fila = `<tr>
                    <td>${(item.temp)}ºC</td>
                    <td>${parseInt(item.hum)} %</td>
                </tr>`;
                cuerpo.innerHTML += fila;
            }
        })

        document.getElementById('mapaIframe').src = '/static/mapa.html';
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
        // Función auxiliar para obtener ISO String en hora local (UTC-3)
        const obtenerFechaHoraLocal = () => {
            const ahora = new Date();
            const offset = ahora.getTimezoneOffset() * 60000; // Desfasaje en ms
            return new Date(ahora.getTime() - offset).toISOString().slice(0, 19);
        };

        // Agrega metadatos de exportación e integridad
        const dataAExportar = {
            metadataExport: {
                fechaHora_Simulacion: obtenerFechaHoraLocal(),
                exportadoPor: "Software de Generacion de Datos de Prueba"
            },
            contenidoSimulacion: this.dataGlobal
        };
        const contenido = JSON.stringify(dataAExportar, null, 2);
        const blob = new Blob([contenido], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'escenario_sintetico.json';
        a.click();
        try {
            JSON.parse(contenido);
            console.log("JSON válido");
        } catch (error) {
            console.log("JSON inválido");
        }
    }

    consolidarDatosSimulados(data, b) {
        this.dataGlobal.id_Simulacion = data.id_Simulacion;
        //this.dataGlobal.fechaHora_Simulacion = data.fechaHora_Generacion;
        if (b == 1) {
            this.dataGlobal.ubicacion = data.puntosGeograficos;
        } 
        else if (b == 2) {
            this.dataGlobal.clima = data.clima;
        } 
        else {
            this.dataGlobal.tiempo = data.tiempo;
        }             
    }
}

// Inicialización global
let simulador;
//let inicio;
document.addEventListener('DOMContentLoaded', () => {
    simulador = new SimularClimaPuntosYHoras('simuladorForm', 'savebtn');
});