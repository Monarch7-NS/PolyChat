import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Avatar from './Avatar';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function GlobalStatsModal({ onClose }) {
  const [stats, setStats] = useState({
    topSender: null,
    topReceiver: null,
    dailyActivity: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [senderRes, receiverRes, dailyRes] = await Promise.all([
          axios.get(`${API_URL}/api/stats/top-sender`).catch(() => ({ data: null })),
          axios.get(`${API_URL}/api/stats/top-receiver`).catch(() => ({ data: null })),
          axios.get(`${API_URL}/api/stats/daily-activity`).catch(() => ({ data: { activity: [] } }))
        ]);

        setStats({
          topSender: senderRes.data,
          topReceiver: receiverRes.data,
          dailyActivity: dailyRes.data.activity || []
        });
      } catch (err) {
        console.error("Erreur chargement des statistiques", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="dashboard-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>&times;</button>
        <div className="dashboard-header">
          <h2>📊 Statistiques Globales</h2>
        </div>
        <div className="dashboard-body">
          {loading ? (
            <div className="loading-spinner">Chargement des statistiques...</div>
          ) : (
            <div className="stats-grid">
              <div className="stat-box">
                <h3>👑 Top Expéditeur</h3>
                {stats.topSender ? (
                  <div className="stat-user">
                    <Avatar username={stats.topSender.username} size={50} />
                    <div>
                      <div className="stat-name">{stats.topSender.username}</div>
                      <div className="stat-value">{stats.topSender.message_count} messages envoyés</div>
                    </div>
                  </div>
                ) : (
                  <div className="empty-state-content">Pas de données</div>
                )}
              </div>
              <div className="stat-box">
                <h3>🎯 Top Destinataire</h3>
                {stats.topReceiver ? (
                  <div className="stat-user">
                    <Avatar username={stats.topReceiver.username} size={50} />
                    <div>
                      <div className="stat-name">{stats.topReceiver.username}</div>
                      <div className="stat-value">{stats.topReceiver.message_count} messages reçus</div>
                    </div>
                  </div>
                ) : (
                  <div className="empty-state-content">Pas de données</div>
                )}
              </div>
            </div>
          )}

          <div className="daily-stats">
            <h3>Activité Récente</h3>
            {stats.dailyActivity.length === 0 ? (
                <div className="empty-state-content">Aucun message récent</div>
            ) : (
                <div className="table-container">
                    <table className="stats-table">
                    <thead>
                        <tr>
                        <th>Date</th>
                        <th>Nombre de messages</th>
                        </tr>
                    </thead>
                    <tbody>
                        {stats.dailyActivity.map((day, idx) => (
                        <tr key={idx}>
                            <td>{day.date}</td>
                            <td>{day.messages}</td>
                        </tr>
                        ))}
                    </tbody>
                    </table>
                </div>
            )}
          </div>
        </div>
        <div className="profile-footer" style={{ marginTop: '24px' }}>
          <button className="btn-primary" onClick={onClose}>Fermer</button>
        </div>
      </div>
    </div>
  );
}

export default GlobalStatsModal;
