document.addEventListener("DOMContentLoaded", function () {
  const urlParams = new URLSearchParams(window.location.search);
  const tablaSeleccionada = urlParams.get("tabla");

  if (tablaSeleccionada) {
    let filterField = "";
    if (tablaSeleccionada === "cliente" || tablaSeleccionada === "empleado") {
      filterField = "CEDULA";
    } else if (tablaSeleccionada === "producto") {
      filterField = "ID";
    } else if (tablaSeleccionada === "cuenta") {
      filterField = "NOMBRE_USUARIO";
    } else if (tablaSeleccionada === "pedido_producto") {
      filterField = "PRODUCTO_ID";
    }

    fetch(`/api/datos_tabla?tabla=${tablaSeleccionada}`)
      .then((response) => response.json())
      .then((data) => {
        let contenedor = document.getElementById("main");
        contenedor.innerHTML = "";

        if (data.datos.length > 0) {
          if (filterField) {
            contenedor.insertAdjacentHTML(
              "beforeend",
              `<div id="filtroContainer"></div><input type="text" id="filterInput" placeholder="Filtrar por ${filterField}">`
            );
          }

          let tablaHTML = `<h3>${tablaSeleccionada.toUpperCase()}</h3>
          <table border="1" id="tablaDatos"><tr>`;
          Object.keys(data.datos[0]).forEach((col) => {
            tablaHTML += `<th>${col.toUpperCase()}</th>`;
          });
          tablaHTML += `<th>Acciones</th></tr>`;

          data.datos.forEach((fila) => {
            tablaHTML += "<tr>";
            Object.entries(fila).forEach(([col, valor]) => {
              if (col === "id") {
                tablaHTML += `<td data-id="${fila.id}" data-col="${col}">${valor}</td>`;
              } else {
                tablaHTML += `<td contenteditable="true" data-id="${fila.id}" data-col="${col}">${valor}</td>`;
              }
            });
            tablaHTML += `<td><button class="eliminar" data-id="${fila.id}" style="background-color: red; color: white; border: none; padding: 5px; cursor: pointer;">Eliminar</button></td>`;
            tablaHTML += "</tr>";
          });

          tablaHTML += `</table>`;
          contenedor.insertAdjacentHTML("beforeend", tablaHTML);
          cargarFormularioNuevoRegistro(data.datos[0]);
          agregarEventos();

          if (filterField) {
            const filterInput = document.getElementById("filterInput");
            const headerCells = document.querySelectorAll("#tablaDatos th");
            let filterIndex = -1;

            headerCells.forEach((th, index) => {
              if (th.innerText.trim().toUpperCase() === filterField) {
                filterIndex = index;
              }
            });

            const aplicarFiltro = (valor) => {
              const tableRows = document.querySelectorAll("#tablaDatos tr:not(:first-child)");
              tableRows.forEach((row) => {
                const cell = row.cells[filterIndex];
                if (cell) {
                  row.style.display = cell.innerText.toUpperCase().includes(valor.toUpperCase()) ? "" : "none";
                }
              });
            };

            filterInput.addEventListener("keyup", function () {
              aplicarFiltro(this.value);
            });
          }
        } else {
          contenedor.innerHTML = `<h3>No hay datos en la tabla ${tablaSeleccionada.toUpperCase()}</h3>`;
        }
      })
      .catch((error) => console.error("Error al obtener datos:", error));
  } else {
    document.getElementById("main").innerHTML = "<h3>Selecciona una tabla para ver los datos.</h3>";
  }
});

function cargarFormularioNuevoRegistro(datosEjemplo) {
  const formulario = document.getElementById("inputsDinamicos");
  formulario.innerHTML = "";

  Object.keys(datosEjemplo).forEach((columna) => {
    if (columna !== "id") {
      formulario.innerHTML += `
        <div>
          <label for="${columna}">${columna.toUpperCase()}:</label>
          <input type="text" id="${columna}" name="${columna}">
        </div>
      `;
    }
  });

  document.getElementById("formularioDatos").addEventListener("submit", function (e) {
    e.preventDefault();
    let nuevoRegistro = {};

    Object.keys(datosEjemplo).forEach((columna) => {
      if (columna !== "id" || columna !== "id_pedido") {
        let valor = document.getElementById(columna).value.trim();
        nuevoRegistro[columna] = valor;
      }
    });

    insertarRegistro(nuevoRegistro);
  });
}

function insertarRegistro(datos) {
  const urlParams = new URLSearchParams(window.location.search);
  const tablaSeleccionada = urlParams.get("tabla");

  fetch(`/api/insertar?tabla=${tablaSeleccionada}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Registro agregado correctamente");
        location.reload();
      } else {
        alert("Error al agregar el registro");
      }
    })
    .catch((error) => {
      console.error("Error al agregar el registro:", error);
      alert("Hubo un problema al agregar el registro.");
    });
}

function agregarEventos() {
  document
    .querySelectorAll("#tablaDatos td[contenteditable='true']")
    .forEach((td) => {
      td.addEventListener("blur", function () {
        let id = this.dataset.id;
        let columna = this.dataset.col;
        let nuevoValor = this.innerText.trim();
        actualizarRegistro(id, columna, nuevoValor);
      });
    });

  document.querySelectorAll(".eliminar").forEach((btn) => {
    btn.addEventListener("click", function () {
      let id = this.dataset.id;
      eliminarRegistro(id);
    });
  });
}

function actualizarRegistro(id, columna, valor) {
  const urlParams = new URLSearchParams(window.location.search);
  const tablaSeleccionada = urlParams.get("tabla");

  fetch(`/api/modificar?tabla=${tablaSeleccionada}&id=${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ [columna]: valor }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data.mensaje);
    })
    .catch((error) => console.error("Error al actualizar datos:", error));
}

function eliminarRegistro(id) {
  if (!confirm("¿Seguro que deseas eliminar este registro?")) return;

  const urlParams = new URLSearchParams(window.location.search);
  const tablaSeleccionada = urlParams.get("tabla");

  fetch(`/api/eliminar?tabla=${tablaSeleccionada}&id=${id}`, {
    method: "DELETE",
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.mensaje);
      location.reload();
    })
    .catch((error) => console.error("Error al eliminar datos:", error));
}
