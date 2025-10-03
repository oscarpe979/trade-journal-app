export interface UserLogin {
  username: string;
  password: string;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface Order {
  id: number;
  execution_time: string;
  spread?: string;
  side: string;
  quantity: number;
  position_effect: string;
  symbol: string;
  expiration_date?: string;
  strike_price?: number;
  option_type?: string;
  price: number;
  net_price: number;
  order_type?: string;
}