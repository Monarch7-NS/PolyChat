import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [username, setUsername] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [messages, setMessages] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [messageInput, setMessageInput] = useState('');

  // Récupérer les utilisateurs en ligne
  const fetchOnlineUsers = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/users/online`);
      setOnlineUsers(response.data.users || []);
    } catch (error) {
      console.error('Erreur lors de la récupération des utilisateurs:', error);
    }
  };

  // Connexion de l'utilisateur
  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username.trim()) return;

    try {
      await axios.post(`${API_URL}/api/users/login`, { username });
      setIsLoggedIn(true);
      fetchOnlineUsers();
      // Rafraîchir la liste des utilisateurs toutes les 5 secondes
      setInterval(fetchOnlineUsers, 5000);
    } catch (error) {
      console.error('Erreur lors de la connexion:', error);
      alert('Erreur de connexion');
    }
  };

  // Déconnexion
  const handleLogout = async () => {
    try {
      await axios.post(`${API_URL}/api/users/logout`, { username });
      setIsLoggedIn(false);
      setUsername('');
      setOnlineUsers([]);
      setMessages([]);
      setSelectedUser(null);
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    }
  };

  // Récupérer l'historique avec un utilisateur
  const fetchConversation = async (otherUser) => {
    try {
      const response = await axios.get(
        `${API_URL}/api/messages/conversation`,
        { params: { user1: username, user2: otherUser } }
      );
      setMessages(response.data.messages || []);
      setSelectedUser(otherUser);
    } catch (error) {
      console.error('Erreur lors de la récupération des messages:', error);
    }
  };

  // Envoyer un message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageInput.trim() || !selectedUser) return;

    try {
      await axios.post(`${API_URL}/api/messages/send`, {
        from: username,
        to: selectedUser,
        content: messageInput,
      });
      setMessageInput('');
      await fetchConversation(selectedUser);
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="App">
        <div className="login-container">
          <h1>PolyChat</h1>
          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Nom d'utilisateur"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <button type="submit">Se connecter</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header>
        <h1>PolyChat</h1>
        <div className="user-info">
          <span>Connecté en tant que: {username}</span>
          <button onClick={handleLogout}>Déconnexion</button>
        </div>
      </header>

      <div className="chat-container">
        <aside className="users-panel">
          <h2>Utilisateurs en ligne</h2>
          <ul>
            {onlineUsers
              .filter((user) => user !== username)
              .map((user) => (
                <li
                  key={user}
                  onClick={() => fetchConversation(user)}
                  className={selectedUser === user ? 'active' : ''}
                >
                  {user}
                </li>
              ))}
          </ul>
        </aside>

        <main className="messages-panel">
          {selectedUser ? (
            <>
              <h2>Conversation avec {selectedUser}</h2>
              <div className="messages-list">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`message ${msg.from === username ? 'sent' : 'received'}`}
                  >
                    <strong>{msg.from}:</strong> {msg.content}
                    <small>{new Date(msg.timestamp).toLocaleString()}</small>
                  </div>
                ))}
              </div>
              <form onSubmit={handleSendMessage} className="message-form">
                <input
                  type="text"
                  placeholder="Votre message..."
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                />
                <button type="submit">Envoyer</button>
              </form>
            </>
          ) : (
            <div className="no-selection">
              <p>Sélectionnez un utilisateur pour commencer le chat</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
