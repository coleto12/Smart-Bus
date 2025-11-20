// Función auxiliar para peticiones con token
async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem("access_token");
    
    if (!token) {
        window.location.href = "/auth";
        return;
    }
    
    const headers = {
        ...options.headers,
        "Authorization": `Bearer ${token}`
    };
    
    const response = await fetch(url, { ...options, headers });
    
    if (response.status === 401) {
        // Token expirado o inválido
        localStorage.removeItem("access_token");
        localStorage.removeItem("usuario");
        alert("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
        window.location.href = "/auth";
        return null;
    }
    
    return response;
}

// Función para verificar si hay sesión activa
function isAuthenticated() {
    return localStorage.getItem("access_token") !== null;
}

// Función para cerrar sesión
function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("usuario");
    window.location.href = "/auth";
}

// Función para obtener datos del usuario desde localStorage
function getUsuario() {
    const usuario = localStorage.getItem("usuario");
    return usuario ? JSON.parse(usuario) : null;
}

// Verificar si el usuario tiene un rol específico
function hasRole(rol) {
    const usuario = getUsuario();
    return usuario && usuario.rol === rol;
}

