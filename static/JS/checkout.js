// checkout.js

function renderCheckoutCart() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const list = document.getElementById('checkout-cart-list');
    const totalSpan = document.getElementById('checkout-total');
    list.innerHTML = '';
    let total = 0;
  
    cart.forEach(item => {
      total += item.qty * item.price;
      const li = document.createElement('li');
      li.textContent = `${item.name} x ${item.qty} — $${(item.qty * item.price).toFixed(2)}`;
      list.appendChild(li);
    });
  
    totalSpan.textContent = `$${total.toFixed(2)}`;
  }
  
  function mostrarAlerta(msg, tipo) {
    const c = document.getElementById('checkout-alert');
    c.textContent = msg;
    c.className = tipo === 'success' ? 'alert-success' : 'alert-error';
    setTimeout(() => { 
      c.textContent = ''; 
      c.className = ''; 
    }, 3000);
  }
  
  document.addEventListener('DOMContentLoaded', renderCheckoutCart);
  
  document.getElementById('checkout-form').addEventListener('submit', async e => {
    e.preventDefault();
  
    // 1. Recoger los datos del formulario y el carrito
    const empresa_envio   = document.getElementById('empresa_envio').value;
    const direccion_envio = document.getElementById('direccion_envio').value;
    const metodo_pago     = document.getElementById('metodo_pago').value;
    const cart            = JSON.parse(localStorage.getItem('cart') || '[]');
  
    if (cart.length === 0) {
      return mostrarAlerta('El carrito está vacío', 'error');
    }
  
    if (!empresa_envio || !direccion_envio || !metodo_pago) {
      return mostrarAlerta('Completa todos los campos.', 'error');
    }
  
    try {
      // 2. Enviar el pedido al servidor
      const res = await fetch('/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ empresa_envio, direccion_envio, metodo_pago, cart })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message);
  
      // 3. Limpiar el carrito en localStorage
      localStorage.removeItem('cart');
      localStorage.setItem('cartCount', '0');
      if (typeof window.actualizarMiniCarrito === 'function') {
        window.actualizarMiniCarrito();
      }
  
      // 4. Mostrar alerta de éxito
      mostrarAlerta(data.message, 'success');
  
      // 5. Forzar descarga del PDF de la factura
      const link = document.createElement('a');
      link.href     = `/checkout/pdf/${data.id}`;
      link.download = `factura_${data.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  
      // 6. Redirigir tras un breve retardo
      setTimeout(() => {
        window.location.href = data.redirect_url || '/carrito';
      }, 500);
  
    } catch (err) {
      mostrarAlerta(err.message, 'error');
    }
  });
  