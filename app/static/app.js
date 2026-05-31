const statusOutput = document.querySelector("#status-output");
const ordersList = document.querySelector("#orders-list");

function showStatus(payload, isError = false) {
  statusOutput.classList.toggle("error", isError);
  statusOutput.textContent =
    typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await response.json();

  if (!response.ok) {
    throw payload;
  }

  return payload;
}

function formValue(form, name) {
  return new FormData(form).get(name).trim();
}

function renderOrders(orders) {
  if (!orders.length) {
    ordersList.textContent = "No orders found";
    return;
  }

  ordersList.replaceChildren(
    ...orders.map((order) => {
      const row = document.createElement("article");
      row.className = "order-row";

      const itemsText = order.items
        .map((item) => {
          const total = item.line_total || item.total_price;
          return `Product #${item.product_id}: ${item.quantity} x ${item.unit_price} = ${total}`;
        })
        .join("\n");

      row.innerHTML = `
        <strong>Order #${order.id} | Client #${order.client_id} | Total ${order.total_amount}</strong>
        <pre></pre>
      `;
      row.querySelector("pre").textContent = itemsText;
      return row;
    }),
  );
}

document.querySelector("#load-health").addEventListener("click", async () => {
  try {
    showStatus(await apiRequest("/health"));
  } catch (error) {
    showStatus(error, true);
  }
});

document.querySelector("#client-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;

  try {
    const payload = await apiRequest("/api/clients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: formValue(form, "name"),
        email: formValue(form, "email"),
        phone: formValue(form, "phone"),
      }),
    });
    showStatus(payload);
    form.reset();
  } catch (error) {
    showStatus(error, true);
  }
});

document.querySelector("#product-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;

  try {
    const payload = await apiRequest("/api/products", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: formValue(form, "name"),
        sku: formValue(form, "sku"),
        price: formValue(form, "price"),
      }),
    });
    showStatus(payload);
    form.reset();
  } catch (error) {
    showStatus(error, true);
  }
});

document.querySelector("#order-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;

  try {
    const payload = await apiRequest("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        client_id: Number(formValue(form, "client_id")),
        items: [
          {
            product_id: Number(formValue(form, "product_id")),
            quantity: Number(formValue(form, "quantity")),
          },
        ],
      }),
    });
    showStatus(payload);
    form.reset();
  } catch (error) {
    showStatus(error, true);
  }
});

document.querySelector("#orders-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const clientId = formValue(form, "client_id");

  try {
    const payload = await apiRequest(`/api/clients/${clientId}/orders`);
    showStatus(payload);
    renderOrders(payload.data);
  } catch (error) {
    showStatus(error, true);
  }
});

document.querySelector("#clear-orders").addEventListener("click", () => {
  ordersList.textContent = "No orders loaded";
});
