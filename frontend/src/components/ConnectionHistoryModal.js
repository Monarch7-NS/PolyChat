import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ConnectionHistoryModal({ onClose }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await axios.get(`${API_URL}/api/users/connection-log`);
        setLogs(res.data.events || []);
      } catch (err) {
        console.error("Erreur chargement de l'historique", err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  const formatDate = (isoString) => {
    if (!isoString) return "";
    const d = new Date(isoString);
    return d.toLocaleString('fr-FR', { 
      day: '2-digit', month: '2-digit', year: 'numeric', 
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="dashboard-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>&times;</button>
        <div className="dashboard-header">
          <h2>🕒 Historique des Connexions</h2>
        </div>
        <div className="dashboard-body">
          {loading ? (
            <div className="loading-spinner">Chargement de l'historique...</div>
          ) : logs.length === 0 ? (
            <div className="empty-state-content">Aucun historique disponible.</div>
          ) : (
            <div className="table-container">
              <table className="stats-table">
                <thead>
                  <tr>
                    <th>Utilisateur</th>
                    <th>Événement</th>
                    <th>Date & Heure</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, idx) => (
                    <tr key={idx}>
                      <td>{log.username}</td>
                      <td>
                        <span className={`event-badge ${log.event}`}>
                          {log.event === 'login' ? 'Connexion' : 'Déconnexion'}
                        </span>
                      </td>
                      <td>{formatDate(log.timestamp)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
        <div className="profile-footer">
          <button className="btn-primary" onClick={onClose}>Fermer</button>
        </div>
      </div>
    </div>
  );
}

export default ConnectionHistoryModal;
