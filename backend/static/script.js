// Obtener todos los usuarios y mostrarlos
fetch("http://127.0.0.1:8000/usuarios")
  .then(response => response.json())
  .then(data => {
      const lista = document.getElementById("usuarios-list");
      data.forEach(u => {
          const li = document.createElement("li");
          li.textContent = `${u.nombre} - ${u.correo}`;
          lista.appendChild(li);
      });
  });
