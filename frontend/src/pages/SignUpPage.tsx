import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../App.css'; // Import the main CSS file for global styles

const SignUpPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    setError('');
    // Handle sign-up logic here
    console.log('Sign-up attempt with:', { email, password });
  };

  return (
    <div className="auth-container">
      <h1 className="app-logo">TradeJournal</h1>
      <div className="auth-card">
        <h2>Sign Up</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className={`form-input ${error ? 'error' : ''}`}
            />
            {error && <p className="error-message">{error}</p>}
          </div>
          <button type="submit" className="auth-button">Sign Up</button>
        </form>
        <div className="auth-links">
          <p>
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;