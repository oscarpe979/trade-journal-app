import React from 'react';
import { NavLink } from 'react-router-dom';
import './SideNavbar.css';
import { FaTachometerAlt, FaCalendarAlt, FaChartBar, FaBook, FaFileUpload, FaSignOutAlt } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

const SideNavbar: React.FC = () => {
  const { logout } = useAuth();

  return (
    <div className="side-navbar">
      <div className="navbar-logo">
        <NavLink to="/">TradeJournal</NavLink>
      </div>
      <nav className="navbar-links">
        <NavLink to="/dashboard" className="navbar-link">
          <FaTachometerAlt />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/calendar" className="navbar-link">
          <FaCalendarAlt />
          <span>Calendar</span>
        </NavLink>
        <NavLink to="/reports" className="navbar-link">
          <FaChartBar />
          <span>Reports</span>
        </NavLink>
        <NavLink to="/trades" className="navbar-link">
          <FaBook />
          <span>Trades</span>
        </NavLink>
      </nav>
      <div className="navbar-import">
        <button className="import-trades-button">
          <FaFileUpload />
          <span>Import Trades</span>
        </button>
      </div>
      <div className="navbar-user">
        <div className="user-info">
          <img src="https://via.placeholder.com/40" alt="User Avatar" />
          <span>oscarpe97</span>
        </div>
        <button onClick={logout} className="logout-button">
          <FaSignOutAlt />
        </button>
      </div>
    </div>
  );
};

export default SideNavbar;
