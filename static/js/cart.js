let updateBtns = document.querySelectorAll(".update-cart");
let size = document.querySelectorAll(".sizes");
updateBtns.forEach((btn) => {
  btn.addEventListener("click", function () {
    let productId = this.dataset.product;
    let action = this.dataset.action;

    if (user === "AnonymousUser") {
      addCookieItem(productId, action);
    } else {
      updateUserOrder(productId, action);
    }
  });
});

function addCookieItem(productId, action) {
  console.log(productId, action);
  if (action == "add") {
    if (cart[productId] == undefined) {
      cart[productId] = { quantity: 1 };
    } else {
      cart[productId]["quantity"] += 1;
    }
  }
  if (action == "remove") {
    cart[productId]["quantity"] -= 1;
    if (cart[productId]["quantity"] <= 0) {
      delete cart[productId];
    }
  }
  location.reload();
  document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
}

function updateUserOrder(productId, action) {
  let url = "/update_item/";
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({
      productId: productId,
      action: action,
    }),
  })
    .then((response) => {
      console.log(response);
      return response.json();
    })
    .then((data) => {
      location.reload();
      console.log("data:", data);
    });
}
