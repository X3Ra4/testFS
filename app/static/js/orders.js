(function () {
  function getOrderRows() {
    return Array.from(document.querySelectorAll(".order-item-row")).map(function (row) {
      return {
        productSelect: row.querySelector(".order-product-select"),
        quantityInput: row.querySelector(".order-quantity-input")
      };
    });
  }

  function parsePositiveNumber(value) {
    var parsed = Number(value);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
  }

  function updateOrderTotalPreview() {
    var preview = document.querySelector("#order-total-preview");

    if (!preview) {
      return;
    }

    var total = getOrderRows().reduce(function (sum, row) {
      var selectedOption = row.productSelect ? row.productSelect.selectedOptions[0] : null;
      var price = parsePositiveNumber(selectedOption ? selectedOption.dataset.price : null);
      var quantity = parsePositiveNumber(row.quantityInput ? row.quantityInput.value : null);

      if (!row.productSelect || !row.productSelect.value || quantity <= 0) {
        return sum;
      }

      return sum + price * quantity;
    }, 0);

    preview.textContent = total.toFixed(2);
  }

  document.addEventListener("DOMContentLoaded", function () {
    getOrderRows().forEach(function (row) {
      if (row.productSelect) {
        row.productSelect.addEventListener("change", updateOrderTotalPreview);
      }

      if (row.quantityInput) {
        row.quantityInput.addEventListener("input", updateOrderTotalPreview);
      }
    });

    updateOrderTotalPreview();
  });
})();
