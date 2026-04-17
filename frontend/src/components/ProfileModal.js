import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Avatar from './Avatar';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ProfileModal({ username, onClose }) {
  const [stats, setStats] = useState(null);
  const [lastSeen, setLastSeen] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!username) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const [statsRes, lastSeenRes] = await Promise.all([
          axios.get(`${API_URL}/api/stats/user-activity/${username}`),
          axios.get(`${API_URL}/api/users/${username}/last-seen`).catch(() => ({ data: null }))
        ]);
        
        setStats(statsRes.data);
        if (lastSeenRes.data) {
          setLastSeen(lastSeenRes.data);
        }
      } catch (err) {
        console.error("Erreur chargement profil", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [username]);

  if (!username) return null;

  const formatDate = (isoString) => {
    if (!isoString) return "Inconnue";
    const d = new Date(isoString);
    return d.toLocaleString('fr-FR', { 
      day: '2-digit', month: '2-digit', year: 'numeric', 
      hour: '2-digit', minute: '2-digit' 
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="profile-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>&times;</button>
        <div className="profile-header">
          <Avatar username={username} size={80} />
          <h2>{username}</h2>
          <span className="profile-status">Utilisateur PolyChat</span>
        </div>
        <div className="profile-body">
          {loading ? (
            <div className="loading-spinner">Chargement des données...</div>
          ) : (
            <>
              <div className="profile-info-item">
                <span className="info-label">Dernière connexion</span>
                <p className="info-value">
                  {lastSeen && lastSeen.last_login ? formatDate(lastSeen.last_login) : "Actuellement en ligne ou inconnu"}
                </p>
              </div>
              <div className="profile-info-item">
                <span className="info-label">Messages Envoyés</span>
                <p className="info-value">{stats?.messages_sent || 0}</p>
              </div>
              <div className="profile-info-item">
                <span className="info-label">Messages Reçus</span>
                <p className="info-value">{stats?.messages_received || 0}</p>
              </div>
              <div className="profile-info-item">
                <span className="info-label">Meilleur Contact</span>
                <p className="info-value">{stats?.top_contact || "Aucun contact"}</p>
              </div>
            </>
          )}
        </div>
        <div className="profile-footer">
          <button className="btn-primary" onClick={onClose}>Fermer</button>
        </div>
      </div>
    </div>
  );
}

export default ProfileModal;
