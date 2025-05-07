document.addEventListener("DOMContentLoaded", () => {
    // ==================== CARGAR CARRITO ====================
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let cartItemsList = document.getElementById("cart-items-list");
    let cartTotal = document.getElementById("cart-total");
  
    function updateCartPage() {
      cartItemsList.innerHTML = "";
      let total = 0;
  
      if (cart.length === 0) {
        cartItemsList.innerHTML = "<li>No hay productos en el carrito.</li>";
      }
  
      cart.forEach((item) => {
        total += item.qty * item.price;
  
        let li = document.createElement("li");
        li.innerHTML = `
          <div class="cart-item">
            <img src="${item.image}" alt="${item.name}" width="50">
            <span>${item.name} - $${item.price} x ${item.qty}</span>
          </div>
        `;
        cartItemsList.appendChild(li);
      });
  
      cartTotal.textContent = `$${total.toFixed(2)}`;
    }
  
    updateCartPage();
  
    // ==================== CARGAR PEDIDOS ====================
    async function cargarMisPedidos() {
      try {
        const res = await fetch('/get_pedidos');
        if (!res.ok) throw new Error('No autenticado o sin pedidos');
        const pedidos = await res.json();
  
        const tbody = document.getElementById('orders-body');
        tbody.innerHTML = '';
  
        if (pedidos.length === 0) {
          tbody.innerHTML = `<tr><td colspan="5">No tienes pedidos aún.</td></tr>`;
          return;
        }
  
        pedidos.forEach(p => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${p.id_pedido || p.numero_pedido}</td>
            <td>${p.fecha_estimada}</td>
            <td>${p.estado_pedido || p.estado_envio}</td>
            <td>$${(p.total).toFixed(2)}</td>
            <td><button class="details-btn" data-pedido-id="${p.id_pedido || p.numero_pedido}">Ver Detalles</button></td>
          `;
          tbody.appendChild(tr);
        });
  
      } catch (err) {
        console.error('Error cargando pedidos:', err);
      }
    }
  
    cargarMisPedidos();
  
    // ==================== FILTRAR PEDIDOS ====================
    document.getElementById("order-filter").addEventListener("keyup", function () {
      const filter = this.value.toLowerCase();
      const rows = document.querySelectorAll("#orders-body tr");
      rows.forEach((row) => {
        const numero = row.querySelector("td")?.textContent.toLowerCase();
        row.style.display = numero.includes(filter) ? "" : "none";
      });
    });
  
    // ==================== MANEJAR MODAL ====================
    const modal = document.getElementById('modal-overlay');
    const modalClose = document.getElementById('modal-close');
    const modalBody = document.getElementById('modal-body');
  
    document.getElementById('orders-body').addEventListener('click', async (e) => {
      if (e.target.classList.contains('details-btn')) {
        const pedidoId = e.target.getAttribute('data-pedido-id');
  
        try {
          const response = await fetch(`/api/detalle_pedido/${pedidoId}`);
          const data = await response.json();
  
          if (response.ok) {
            const { pedido, lineas } = data;
  
            let html = `
              <p><strong>Fecha Compra:</strong> ${pedido.fecha_compra}</p>
              <p><strong>Empresa Envío:</strong> ${pedido.empresa_envio}</p>
              <p><strong>Dirección Envío:</strong> ${pedido.direccion_envio}</p>
              <p><strong>Total Pedido:</strong> $${pedido.total.toFixed(2)}</p>
              <table style="width:100%; border-collapse: collapse;">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio Unitario</th>
                    <th>Imagen</th>
                  </tr>
                </thead>
                <tbody>
            `;
  
            lineas.forEach(producto => {
                html += `
                  <tr>
                    <td>${producto.nombre}</td>
                    <td>${producto.cantidad}</td>
                    <td>$${producto.precio_unitario.toFixed(2)}</td>
                    <td><img class="modal-imgs" src="/static/${producto.url_imagen}" alt="${producto.nombre}"/></td>
                  </tr>
                `;
              });
              
  
            html += '</tbody></table>';
            modalBody.innerHTML = html;
            modal.style.display = 'flex';
          } else {
            modalBody.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
            modal.style.display = 'flex';
          }
        } catch (err) {
          console.error(err);
          modalBody.innerHTML = `<p style="color:red;">Error al obtener los datos del pedido.</p>`;
          modal.style.display = 'flex';
        }
      }
    });
  
    modalClose.addEventListener('click', () => {
      modal.style.display = 'none';
    });
  });
  