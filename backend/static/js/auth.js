const formRegistro = document.getElementById("form-registro");
const formLogin = document.getElementById("form-login");
const mensajeDiv = document.getElementById("mensaje");

const registroDiv = document.getElementById("registro-div");
const loginDiv = document.getElementById("login-div");

const showRegister = document.getElementById("show-register");
const showLogin = document.getElementById("show-login");

// Función para mostrar mensajes
function mostrarMensaje(texto, tipo) {
    mensajeDiv.innerText = texto;
    mensajeDiv.className = tipo; // 'success' o 'error'
    
    // Ocultar mensaje después de 5 segundos
    setTimeout(() => {
        mensajeDiv.style.display = 'none';
        mensajeDiv.className = '';
    }, 5000);
}

// Alternar vistas
showRegister.addEventListener("click", () => {
    loginDiv.style.display = "none";
    registroDiv.style.display = "block";
    mensajeDiv.style.display = "none";
});

showLogin.addEventListener("click", () => {
    registroDiv.style.display = "none";
    loginDiv.style.display = "block";
    mensajeDiv.style.display = "none";
});

// Registro
formRegistro.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(formRegistro);

    try {
        const res = await fetch("/auth/register", {
            method: "POST",
            body: formData
        });
        const result = await res.json();

        if (res.ok) {
            mostrarMensaje("✓ Registro exitoso. Redirigiendo al login...", "success");
            formRegistro.reset();

            setTimeout(() => {
                registroDiv.style.display = "none";
                loginDiv.style.display = "block";
                mostrarMensaje("Ahora puedes iniciar sesión", "success");
            }, 1500);
        } else {
            mostrarMensaje("✗ Error: " + (result.detail || "Error en el registro"), "error");
        }
    } catch (error) {
        mostrarMensaje("✗ Error de conexión: " + error.message, "error");
    }
});

// Login
formLogin.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(formLogin);

    try {
        const res = await fetch("/auth/login", {
            method: "POST",
            body: formData
        });
        const result = await res.json();

        if (res.ok) {
            mostrarMensaje("✓ Login exitoso. Redirigiendo...", "success");
            
            // ✅ Guardar token y usuario en localStorage
            localStorage.setItem("access_token", result.access_token);
            localStorage.setItem("usuario", JSON.stringify(result.usuario));
            
            console.log("Usuario logueado:", result.usuario);
            
            // Redirigir según el rol
            setTimeout(() => {
                const rol = result.usuario.rol;
                
                if (rol === "administrador") {
                    window.location.href = "/dashboard/admin";
                } else if (rol === "conductor") {
                    window.location.href = "/dashboard/conductor";
                } else {
                    window.location.href = "/dashboard/pasajero";
                }
            }, 1000);
        } else {
            mostrarMensaje("✗ " + result.detail, "error");
        }
    } catch (error) {
        mostrarMensaje("✗ Error de conexión: " + error.message, "error");
    }
});

// Verificar si ya hay sesión activa al cargar la página
document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("access_token");
    const usuario = localStorage.getItem("usuario");
    
    if (token && usuario) {
        const userData = JSON.parse(usuario);
        mostrarMensaje("Ya tienes una sesión activa. Redirigiendo...", "success");
        
        setTimeout(() => {
            const rol = userData.rol;
            if (rol === "administrador") {
                window.location.href = "/dashboard/admin";
            } else if (rol === "conductor") {
                window.location.href = "/dashboard/conductor";
            } else {
                window.location.href = "/dashboard/pasajero";
            }
        }, 1000);
    }
});