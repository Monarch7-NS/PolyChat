import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Avatar from './Avatar';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function StatCard({ label, value, icon }) {
  return (
    <div className="admin-stat-card">
      <div className="admin-stat-icon">{icon}</div>
      <div className="admin-stat-value">{value ?? '—'}</div>
      <div className="admin-stat-label">{label}</div>
    </div>
  );
}

function AdminDashboard({ username, onLogout, onExitAdmin }) {
  const [overview, setOverview] = useState(null);
  const [topSender, setTopSender] = useState(null);
  const [topReceiver, setTopReceiver] = useState(null);
  const [dailyActivity, setDailyActivity] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [connectionLog, setConnectionLog] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [ovRes, senderRes, receiverRes, actRes, usersRes, logRes] = await Promise.allSettled([
        axios.get(`${API_URL}/api/stats/overview`),
        axios.get(`${API_URL}/api/stats/top-sender`),
        axios.get(`${API_URL}/api/stats/top-receiver`),
        axios.get(`${API_URL}/api/stats/daily-activity`),
        axios.get(`${API_URL}/api/stats/all-users`),
        axios.get(`${API_URL}/api/users/connection-log?n=100`),
      ]);
      if (ovRes.status === 'fulfilled') setOverview(ovRes.value.data);
      if (senderRes.status === 'fulfilled') setTopSender(senderRes.value.data);
      if (receiverRes.status === 'fulfilled') setTopReceiver(receiverRes.value.data);
      if (actRes.status === 'fulfilled') setDailyActivity(actRes.value.data.activity || []);
      if (usersRes.status === 'fulfilled') setAllUsers(usersRes.value.data.users || []);
      if (logRes.status === 'fulfilled') setConnectionLog(logRes.value.data.events || []);
    } catch (_) {}
    setLoading(false);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const formatDate = (iso) => {
    if (!iso) return '—';
    return new Date(iso).toLocaleString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  };

  const tabs = [
    { id: 'overview', label: '📊 Vue générale' },
    { id: 'users', label: '👥 Utilisateurs' },
    { id: 'activity', label: '📈 Activité' },
    { id: 'logs', label: '🕒 Connexions' },
  ];

  return (
    <div className="admin-page">
      {/* Header */}
      <header className="admin-header">
        <div className="admin-header-left">
          <span className="admin-logo">🛡️</span>
          <div>
            <h1 className="admin-title">PolyChat Admin</h1>
            <span className="admin-subtitle">Tableau de bord administrateur</span>
          </div>
        </div>
        <div className="admin-header-right">
          <span className="admin-user-badge">
            <Avatar username={username} size={28} />
            {username}
          </span>
          <button className="admin-btn-secondary" onClick={onExitAdmin} title="Revenir au chat">
            💬 Chat
          </button>
          <button className="admin-btn-danger" onClick={onLogout} title="Déconnexion">
            ⏻ Déconnexion
          </button>
        </div>
      </header>

      {/* Tabs */}
      <nav className="admin-tabs">
        {tabs.map((t) => (
          <button
            key={t.id}
            className={`admin-tab-btn ${activeTab === t.id ? 'active' : ''}`}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
          </button>
        ))}
        <button className="admin-refresh-btn" onClick={fetchAll} title="Rafraîchir">
          🔄 Rafraîchir
        </button>
      </nav>

      <div className="admin-content">
        {loading && <div className="admin-loading">Chargement...</div>}

        {/* ── Vue générale ───────────────────────────────────────────────── */}
        {!loading && activeTab === 'overview' && (
          <div>
            <div className="admin-cards-row">
              <StatCard label="Utilisateurs" value={overview?.total_users} icon="👤" />
              <StatCard label="Messages" value={overview?.total_messages} icon="💬" />
              <StatCard label="Conversations" value={overview?.total_conversations} icon="🗂️" />
            </div>

            <div className="admin-section-grid">
              <div className="admin-section-box">
                <h3 className="admin-section-title">🥇 Top Expéditeur</h3>
                {topSender ? (
                  <div className="admin-top-user">
                    <Avatar username={topSender.username} size={48} />
                    <div>
                      <div className="admin-top-name">{topSender.username}</div>
                      <div className="admin-top-count">{topSender.message_count} messages envoyés</div>
                    </div>
                  </div>
                ) : <p className="admin-empty">Aucune donnée</p>}
              </div>

              <div className="admin-section-box">
                <h3 className="admin-section-title">📬 Top Destinataire</h3>
                {topReceiver ? (
                  <div className="admin-top-user">
                    <Avatar username={topReceiver.username} size={48} />
                    <div>
                      <div className="admin-top-name">{topReceiver.username}</div>
                      <div className="admin-top-count">{topReceiver.message_count} messages reçus</div>
                    </div>
                  </div>
                ) : <p className="admin-empty">Aucune donnée</p>}
              </div>
            </div>
          </div>
        )}

        {/* ── Utilisateurs ───────────────────────────────────────────────── */}
        {!loading && activeTab === 'users' && (
          <div className="admin-section-box">
            <h3 className="admin-section-title">👥 Tous les utilisateurs ({allUsers.length})</h3>
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Utilisateur</th>
                    <th>Rôle</th>
                    <th>Messages envoyés</th>
                    <th>Messages reçus</th>
                    <th>Total</th>
                    <th>Inscription</th>
                  </tr>
                </thead>
                <tbody>
                  {allUsers.map((u) => (
                    <tr key={u.username}>
                      <td>
                        <div className="admin-user-cell">
                          <Avatar username={u.username} size={28} />
                          <span>{u.username}</span>
                        </div>
                      </td>
                      <td>
                        <span className={`role-badge ${u.role}`}>
                          {u.role === 'admin' ? '🛡️ Admin' : '👤 User'}
                        </span>
                      </td>
                      <td>{u.messages_sent}</td>
                      <td>{u.messages_received}</td>
                      <td><strong>{u.messages_sent + u.messages_received}</strong></td>
                      <td>{u.created_at ? formatDate(u.created_at) : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ── Activité quotidienne ────────────────────────────────────────── */}
        {!loading && activeTab === 'activity' && (
          <div className="admin-section-box">
            <h3 className="admin-section-title">📈 Activité des 7 derniers jours</h3>
            {dailyActivity.length === 0 ? (
              <p className="admin-empty">Aucune activité enregistrée</p>
            ) : (
              <>
                <div className="admin-bar-chart">
                  {(() => {
                    const max = Math.max(...dailyActivity.map((d) => d.messages), 1);
                    return [...dailyActivity].reverse().map((d) => (
                      <div key={d.date} className="admin-bar-item">
                        <div className="admin-bar-count">{d.messages}</div>
                        <div
                          className="admin-bar"
                          style={{ height: `${(d.messages / max) * 150}px` }}
                        />
                        <div className="admin-bar-date">
                          {new Date(d.date).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })}
                        </div>
                      </div>
                    ));
                  })()}
                </div>

                <div className="admin-table-wrap" style={{ marginTop: '24px' }}>
                  <table className="admin-table">
                    <thead>
                      <tr><th>Date</th><th>Messages</th></tr>
                    </thead>
                    <tbody>
                      {dailyActivity.map((d) => (
                        <tr key={d.date}>
                          <td>{new Date(d.date).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}</td>
                          <td><strong>{d.messages}</strong></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        )}

        {/* ── Journal de connexions ───────────────────────────────────────── */}
        {!loading && activeTab === 'logs' && (
          <div className="admin-section-box">
            <h3 className="admin-section-title">🕒 Journal de connexions ({connectionLog.length} événements)</h3>
            {connectionLog.length === 0 ? (
              <p className="admin-empty">Aucun événement enregistré (Redis vide)</p>
            ) : (
              <div className="admin-table-wrap">
                <table className="admin-table">
                  <thead>
                    <tr><th>Utilisateur</th><th>Événement</th><th>Date & Heure</th></tr>
                  </thead>
                  <tbody>
                    {connectionLog.map((e, i) => (
                      <tr key={i}>
                        <td>
                          <div className="admin-user-cell">
                            <Avatar username={e.username} size={24} />
                            <span>{e.username}</span>
                          </div>
                        </td>
                        <td>
                          <span className={`event-badge ${e.event}`}>
                            {e.event === 'login' ? '🟢 Connexion' : '🔴 Déconnexion'}
                          </span>
                        </td>
                        <td>{formatDate(e.timestamp)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;
