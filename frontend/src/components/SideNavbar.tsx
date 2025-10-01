import React, { useRef } from 'react';
import { NavLink } from 'react-router-dom';
import './SideNavbar.css';
import { FaTachometerAlt, FaCalendarAlt, FaChartBar, FaBook, FaFileUpload, FaSignOutAlt } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';
import { uploadOrders } from '../services/orderService';

const SideNavbar: React.FC = () => {
  const { user, logout, token } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && user && token) {
      try {
        await uploadOrders(file, token);
        alert('Orders uploaded successfully');
      } catch (error) {
        alert('Error uploading orders: ' + error );
      }
    }
  };

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
        <button className="import-trades-button" onClick={handleImportClick}>
          <FaFileUpload />
          <span>Import Trades</span>
        </button>
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileChange}
          accept=".csv"
        />
      </div>
      <div className="navbar-user">
        <div className="user-info">
          <span>{user ? user.email : ''}</span>
        </div>
        <button onClick={logout} className="logout-button" title='Log Out'>
          <FaSignOutAlt />
        </button>
      </div>
    </div>
  );
};

export default SideNavbar;
