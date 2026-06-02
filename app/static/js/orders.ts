type OrderRow = {
  productSelect: HTMLSelectElement | null;
  quantityInput: HTMLInputElement | null;
};

function getOrderRows(): OrderRow[] {
  return Array.from(document.querySelectorAll<HTMLTableRowElement>(".order-item-row")).map((row) => ({
    productSelect: row.querySelector<HTMLSelectElement>(".order-product-select"),
    quantityInput: row.querySelector<HTMLInputElement>(".order-quantity-input"),
  }));
}

function parsePositiveNumber(value: string | null | undefined): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
}

function updateOrderTotalPreview(): void {
  const preview = document.querySelector<HTMLElement>("#order-total-preview");

  if (!preview) {
    return;
  }

  const total = getOrderRows().reduce((sum, row) => {
    const selectedOption = row.productSelect?.selectedOptions[0];
    const price = parsePositiveNumber(selectedOption?.dataset.price);
    const quantity = parsePositiveNumber(row.quantityInput?.value);

    if (!row.productSelect?.value || quantity <= 0) {
      return sum;
    }

    return sum + price * quantity;
  }, 0);

  preview.textContent = total.toFixed(2);
}

document.addEventListener("DOMContentLoaded", () => {
  getOrderRows().forEach((row) => {
    row.productSelect?.addEventListener("change", updateOrderTotalPreview);
    row.quantityInput?.addEventListener("input", updateOrderTotalPreview);
  });

  updateOrderTotalPreview();
});
