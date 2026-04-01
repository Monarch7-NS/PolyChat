import React, { useState } from 'react';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin(username);
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">✨</div>
        <h1>PolyChat</h1>
        <p>Rejoignez la conversation. Connectez-vous maintenant.</p>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Pseudo"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
            required
          />
          <button type="submit">Commencer</button>
        </form>
      </div>
    </div>
  );
}

export default Login;
