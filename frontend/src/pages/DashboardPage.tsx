import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../App.css';

const DashboardPage: React.FC = () => {
  const { logout } = useAuth();

  return (
    <div>
      <nav className="dashboard-nav">
        <div className="nav-links">
          <Link to="/dashboard">Dashboard</Link>
          {/* Future links will go here */}
        </div>
        <button onClick={logout} className="logout-button">Logout</button>
      </nav>
      <div className="dashboard-content">
        <h1>Dashboard</h1>
        <p>Welcome to your TradeJournal dashboard!</p>
      </div>
    </div>
  );
};

export default DashboardPage;
