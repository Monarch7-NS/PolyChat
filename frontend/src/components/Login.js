import React, { useState } from 'react';

function Login({ onLogin }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const switchMode = (newMode) => {
    setMode(newMode);
    setError('');
    setPassword('');
    setConfirmPassword('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username.trim()) {
      setError('Le pseudo est requis');
      return;
    }
    if (password.length < 4) {
      setError('Le mot de passe doit contenir au moins 4 caractères');
      return;
    }
    if (mode === 'register' && password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    setLoading(true);
    try {
      await onLogin(username.trim(), password, mode);
    } catch (err) {
      setError(err.message || 'Erreur, veuillez réessayer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">✨</div>
        <h1>PolyChat</h1>
        <p>
          {mode === 'login'
            ? 'Connectez-vous pour rejoindre la conversation.'
            : 'Créez votre compte en quelques secondes.'}
        </p>

        <div className="auth-tabs">
          <button
            type="button"
            className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
            onClick={() => switchMode('login')}
          >
            Connexion
          </button>
          <button
            type="button"
            className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
            onClick={() => switchMode('register')}
          >
            Inscription
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Pseudo"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
            required
            minLength={2}
          />
          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={4}
          />
          {mode === 'register' && (
            <input
              type="password"
              placeholder="Confirmer le mot de passe"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          )}

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading
              ? '...'
              : mode === 'login'
              ? 'Se connecter'
              : "S'inscrire"}
          </button>
        </form>

        {mode === 'login' && (
          <p className="auth-hint">
            Comptes démo : <strong>Alice</strong> / <strong>password123</strong>
            <br />
            Admin : <strong>admin</strong> / <strong>admin1234</strong>
          </p>
        )}
      </div>
    </div>
  );
}

export default Login;
