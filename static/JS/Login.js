
//Login Y Registro Animacion
const btnIN = document.getElementById("btn-sign-in");
const btnUP = document.getElementById("btn-sign-up");

const container = document.querySelector(".container");

btnIN.addEventListener("click",()=>{
container.classList.remove("toggle");
})
btnUP.addEventListener("click",()=>{
container.classList.add("toggle");
})

// Manejo de envío y alerta del login
document.querySelector('.sign-in').addEventListener('submit', async function (event) {
    event.preventDefault(); // Evita que el formulario se envíe de forma tradicional

    const nombrelg = document.getElementById('nombrelg').value;
    const contrasenalg = document.getElementById('contrasenalg').value;

    if (!nombrelg || !contrasenalg) {
        mostrarAlerta("Por favor, complete todos los campos.", "error");
        return;
    }

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ nombrelg, contrasenalg })
        });

        const data = await response.json();

        if (data.success) {
            mostrarAlerta(data.message, "success");
            // Usa redirect_url del servidor para redirigir
            setTimeout(() => {
                window.location.href = data.redirect_url; 
            }, 1500);
        } else {
            mostrarAlerta(data.message, "error");
        }
    } catch (error) {
        mostrarAlerta("Error al conectar con el servidor. Inténtelo de nuevo.", "error");
    }
});

// Función para mostrar mensajes de alerta
function mostrarAlerta(mensaje, tipo) {
    const alertContainer = document.getElementById("alert-container");
    alertContainer.innerHTML = ''; // Limpiar alertas previas

    const alertDiv = document.createElement("div");
    alertDiv.classList.add("alert");
    alertDiv.classList.add(tipo === "success" ? "alert-success" : "alert-error");
    alertDiv.innerText = mensaje;

    alertContainer.appendChild(alertDiv);
    alertContainer.style.display = "block";

    // Ocultar la alerta después de 3 segundos
    setTimeout(() => {
        alertContainer.style.display = "none";
        alertContainer.innerHTML = '';
    }, 3000);
}

//Manejo de alerta del Registro
document.querySelector('.sign-up').addEventListener('submit', async function (event) {
    event.preventDefault(); // Evita que el formulario se envíe de forma tradicional

    const nombre_usuario = document.getElementById('nombrerg').value;
    const contrasena = document.getElementById('contrasenarg').value;
    const email = document.getElementById('emailrg').value;

    // Validar si los campos están vacíos
    if (!nombre_usuario || !contrasena || !email) {
        mostrarAlerta("Por favor, complete todos los campos.", "error");
        return;
    }

    try {
        // Enviar la solicitud al servidor para registrar al usuario
        const response = await fetch('/insertar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ nombrerg: nombre_usuario, contrasenarg: contrasena, emailrg: email })
        });

        const data = await response.json();

        // Mostrar la alerta dependiendo del resultado
        if (data.success) {
            mostrarAlerta(data.message, "success");
            // Redirigir a la página de inicio después de un tiempo
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 1500);
        } else {
            mostrarAlerta(data.message, "error");
        }
    } catch (error) {
        mostrarAlerta("Error al conectar con el servidor. Inténtelo de nuevo.", "error");
    }
});

// Función para mostrar mensajes de alerta
function mostrarAlerta(mensaje, tipo) {
    const alertContainer = document.getElementById("alert-container");
    alertContainer.innerHTML = ''; // Limpiar alertas previas

    const alertDiv = document.createElement("div");
    alertDiv.classList.add("alert");
    alertDiv.classList.add(tipo === "success" ? "alert-success" : "alert-error");
    alertDiv.innerText = mensaje;

    alertContainer.appendChild(alertDiv);
    alertContainer.style.display = "block";

    // Ocultar la alerta después de 3 segundos
    setTimeout(() => {
        alertContainer.style.display = "none";
        alertContainer.innerHTML = '';
    }, 3000);
}