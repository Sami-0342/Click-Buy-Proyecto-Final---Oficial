document.addEventListener("DOMContentLoaded", function () {
    let cartCount = localStorage.getItem("cartCount") || 0;
    let cartBadge = document.getElementById("cart-count");

    function updateCartCount() {
        cartBadge.textContent = cartCount;
        cartBadge.style.visibility = cartCount > 0 ? "visible" : "hidden";
    }

    updateCartCount(); // Actualizar al cargar la página

    document.querySelectorAll(".btn-modificar").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault(); // Evitar navegación por ahora
            cartCount++;
            localStorage.setItem("cartCount", cartCount);
            updateCartCount();
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let cartBadge = document.getElementById("cart-count");
    let cartItemsContainer = document.getElementById("cart-items");
    let cartTotal = document.getElementById("cart-total");
    let clearCartBtn = document.getElementById("clear-cart");
    let miniCart = document.getElementById("mini-cart");

    function updateCartUI() {
        cartItemsContainer.innerHTML = "";
        cartBadge.textContent = cart.length;
        cartBadge.style.visibility = cart.length > 0 ? "visible" : "hidden";
        miniCart.style.display = cart.length > 0 ? "block" : "none";

        let total = 0;

        cart.forEach((item, index) => {
            total += item.qty * item.price;

            let li = document.createElement("li");
            li.innerHTML = `
                <div class="cart-item">
                    <img src="${item.image}" alt="${item.name}">
                    <span>${item.name} - $${item.price}</span>
                    <div class="qty-controls">
                        <button class="qty-btn" data-index="${index}" data-action="decrease">-</button>
                        <span>${item.qty}</span>
                        <button class="qty-btn" data-index="${index}" data-action="increase">+</button>
                    </div>
                    <button class="remove-btn" data-index="${index}">❌</button>
                </div>
            `;
            cartItemsContainer.appendChild(li);
        });

        cartTotal.textContent = `$${total.toFixed(2)}`;
        localStorage.setItem("cart", JSON.stringify(cart));
    }

    document.querySelectorAll(".btn-modificar").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            let productCard = this.closest(".product-card");
            let productId = productCard.id.split("-")[1];
            let productName = productCard.querySelector("h3").textContent;
            let productPrice = parseFloat(productCard.querySelector(".product-price").textContent.replace("Precio: $", ""));
            let productImage = productCard.querySelector(".product-image") ? productCard.querySelector(".product-image").src : "";
            let productStock = parseInt(productCard.querySelector("p:nth-of-type(2)").textContent.replace("Cantidad disponible: ", ""));

            let existingItem = cart.find(item => item.id === productId);
            if (existingItem) {
                if (existingItem.qty < productStock) {
                    existingItem.qty++;
                }
            } else {
                cart.push({ id: productId, name: productName, price: productPrice, image: productImage, qty: 1, stock: productStock });
            }

            updateCartUI();
        });
    });

    cartItemsContainer.addEventListener("click", function (event) {
        let button = event.target;
        let index = button.getAttribute("data-index");

        if (button.classList.contains("qty-btn")) {
            let action = button.getAttribute("data-action");

            if (action === "increase" && cart[index].qty < cart[index].stock) {
                cart[index].qty++;
            } else if (action === "decrease") {
                cart[index].qty--;
                if (cart[index].qty === 0) {
                    cart.splice(index, 1);
                }
            }

            updateCartUI();
        }

        if (button.classList.contains("remove-btn")) {
            cart.splice(index, 1);
            updateCartUI();
        }
    });

    clearCartBtn.addEventListener("click", function () {
        cart = [];
        updateCartUI();
    });

    updateCartUI();
});
