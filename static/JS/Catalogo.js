function eliminarProducto(productoId) {
    $.ajax({
      url: '/eliminar_producto',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ 'id': productoId }),
      success: function(response) {
        if (response.success) {
          $('#product-' + productoId).remove();
          alert(response.message);
        } else {
          alert('Error al eliminar el producto: ' + response.message);
        }
      },
      error: function() {
        alert('Hubo un problema al intentar eliminar el producto');
      }
    });
  }
  function abrirModalModificar(producto) {
$('#mod_id').val(producto.id);
$('#mod_nombre_producto').val(producto.nombre_producto);
$('#mod_descripcion').val(producto.descripcion);
$('#mod_cantidad_disponible').val(producto.cantidad_disponible);
$('#mod_precio').val(producto.precio);

// Mostrar el modal correctamente
$('#modalModificar').css('display', 'flex');
}

function cerrarModalModificar() {
$('#modalModificar').css('display', 'none');
}

// Cerrar modal al hacer clic fuera de él
$(window).on('click', function(event) {
if ($(event.target).is('#modalModificar')) {
  cerrarModalModificar();
}
});


  function cerrarModalModificar() {
    $('#modalModificar').css('display', 'none');
  }

  $('#formModificar').on('submit', function(e) {
    e.preventDefault();
    let formData = new FormData(this);
    $.ajax({
      url: '/modificar_producto/' + $('#mod_id').val(),
      method: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      success: function(response) {
        if (response.success) {
          alert(response.message);
          location.reload();
        } else {
          alert('Error al modificar el producto: ' + response.message);
        }
      },
      error: function() {
        alert('Hubo un problema al intentar modificar el producto');
      }
    });
  });

  $(window).on('click', function(event) {
    if ($(event.target).is('#modalModificar')) {
      cerrarModalModificar();
    }
  });