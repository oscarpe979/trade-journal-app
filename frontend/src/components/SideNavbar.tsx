import React from 'react';
import { NavLink } from 'react-router-dom';
import './SideNavbar.css';
import { FaTachometerAlt, FaBook, FaPlus, FaSignOutAlt } from 'react-icons/fa';

const SideNavbar: React.FC = () => {
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
        <NavLink to="/trades" className="navbar-link">
          <FaBook />
          <span>Trades</span>
        </NavLink>
        <NavLink to="/journal" className="navbar-link">
          <FaBook />
          <span>Journal</span>
        </NavLink>
        <NavLink to="/new-trade" className="navbar-link">
          <FaPlus />
          <span>New Trade</span>
        </NavLink>
      </nav>
      <div className="navbar-user">
        <div className="user-info">
          <img src="https://via.placeholder.com/40" alt="User Avatar" />
          <span>oscarpe97</span>
        </div>
        <button className="logout-button">
          <FaSignOutAlt />
        </button>
      </div>
    </div>
  );
};

export default SideNavbar;
