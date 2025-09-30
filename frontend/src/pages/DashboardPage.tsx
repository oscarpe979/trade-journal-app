import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../App.css';

const DashboardPage: React.FC = () => {
  const { logout } = useAuth();

  return (
      <div className="dashboard-content">
        <h1>Dashboard</h1>
        <p>Welcome to your TradeJournal dashboard!</p>
      </div>
  );
};

export default DashboardPage;
