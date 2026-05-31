type Client = {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  created_at: string;
};

type Product = {
  id: number;
  name: string;
  sku: string;
  price: string;
  created_at: string;
};

type OrderItem = {
  id: number;
  product_id: number;
  product_name?: string;
  sku?: string;
  unit_price: string;
  quantity: number;
  line_total: string;
};

type Order = {
  id: number;
  client_id: number;
  items: OrderItem[];
  total_amount: string;
  created_at: string;
};

type CreateOrderRequest = {
  client_id: number;
  items: {
    product_id: number;
    quantity: number;
  }[];
};

type ApiSuccess<T> = {
  data: T;
  message: string;
};

type ApiError = {
  error: string;
  details: string;
};

async function createOrder(payload: CreateOrderRequest): Promise<Order> {
  const response = await fetch("http://127.0.0.1:5000/api/orders", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const result = (await response.json()) as ApiSuccess<Order> | ApiError;

  if (!response.ok) {
    const error = result as ApiError;
    throw new Error(error.details || "Failed to create order");
  }

  return (result as ApiSuccess<Order>).data;
}

createOrder({
  client_id: 1,
  items: [
    {
      product_id: 1,
      quantity: 2,
    },
  ],
});
