import React, { useEffect, useState } from 'react';
import { getTrades } from '../services/tradeService';
import { useAuth } from '../contexts/AuthContext';

const TradesPage: React.FC = () => {
  const { user, token } = useAuth();
  const [trades, setTrades] = useState<any[]>([]);

  useEffect(() => {
    const fetchTrades = async () => {
      if (user && token) {
        try {
          const response = await getTrades(token);
          setTrades(response);
        } catch (error) {
          console.error('Error fetching trades:', error);
        }
      }
    };

    fetchTrades();
  }, [user, token]);

  return (
    <div>
      <h1>Trades</h1>
      <table>
        <thead>
          <tr>
            <th>Exec Time</th>
            <th>Spread</th>
            <th>Side</th>
            <th>Qty</th>
            <th>Pos Effect</th>
            <th>Symbol</th>
            <th>Exp</th>
            <th>Strike</th>
            <th>Type</th>
            <th>Price</th>
            <th>Net Price</th>
            <th>Order Type</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={trade.id}>
              <td>{trade.execution_time}</td>
              <td>{trade.spread}</td>
              <td>{trade.side}</td>
              <td>{trade.quantity}</td>
              <td>{trade.position_effect}</td>
              <td>{trade.symbol}</td>
              <td>{trade.expiration_date}</td>
              <td>{trade.strike_price}</td>
              <td>{trade.option_type}</td>
              <td>{trade.price}</td>
              <td>{trade.net_price}</td>
              <td>{trade.order_type}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TradesPage;
