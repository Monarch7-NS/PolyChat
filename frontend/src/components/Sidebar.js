import React, { useState } from 'react';
import Avatar from './Avatar';

function formatTime(iso) {
  const d = new Date(iso);
  const now = new Date();
  if (d.toDateString() === now.toDateString()) {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  return d.toLocaleDateString([], { day: '2-digit', month: '2-digit' });
}

function Sidebar({ username, role, conversations, onlineUsers, selectedUser, onSelectUser, onLogout, searchResults, onSearch, onOpenStats, onOpenHistory, onShowProfile, onOpenAdmin }) {
  const [search, setSearch] = useState('');

  const filtered = conversations.filter((c) =>
    c.other_user.toLowerCase().includes(search.toLowerCase())
  );

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    onSearch(e.target.value);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-user" style={{ cursor: 'pointer' }} onClick={() => onShowProfile(username)} title="Voir mes statistiques">
          <Avatar username={username} size={36} />
          <span className="sidebar-username">{username}</span>
        </div>
        <div className="sidebar-actions">
          {onOpenAdmin && (
            <button className="icon-btn admin-btn" onClick={onOpenAdmin} title="Dashboard Admin">
              🛡️
            </button>
          )}
          <button className="logout-btn" onClick={onLogout} title="Déconnexion">
            ⏻
          </button>
        </div>
      </div>

      <div className="sidebar-search">
        <input
          type="text"
          placeholder="Rechercher / Nouveau chat..."
          value={search}
          onChange={handleSearchChange}
        />
        {search && searchResults && searchResults.length > 0 && (
          <div className="new-chat-results">
            <div className="conversations-label">Nouveaux correspondants</div>
            {searchResults.map((u) => (
              <div
                key={u}
                className="search-result-item"
                onClick={() => {
                  setSearch('');
                  onSelectUser(u);
                }}
              >
                {u}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="conversations-label">Messages</div>

      <div className="conversations-list">
        {filtered.length === 0 && (
          <div className="empty-conversations">
            {search ? 'Aucun résultat' : 'Aucune conversation'}
          </div>
        )}
        {filtered.map((conv) => (
          <div
            key={conv.other_user}
            className={`conversation-item ${selectedUser === conv.other_user ? 'active' : ''}`}
            onClick={() => onSelectUser(conv.other_user)}
          >
            <div 
              className="conv-avatar-wrap" 
              style={{ cursor: 'zoom-in' }}
              title="Voir les stats de ce contact"
              onClick={(e) => { e.stopPropagation(); onShowProfile(conv.other_user); }}
            >
              <Avatar username={conv.other_user} size={40} />
              {onlineUsers.has(conv.other_user) && <span className="online-dot" />}
            </div>
            <div className="conv-info">
              <div className="conv-top">
                <span className="conv-name">{conv.other_user}</span>
                <span className="conv-time">
                  {conv.updated_at ? formatTime(conv.updated_at) : ''}
                </span>
              </div>
              <div className="conv-bottom">
                <span className="conv-last-msg">{conv.last_message}</span>
                {conv.unread_count > 0 && (
                  <span className="unread-badge">{conv.unread_count}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}

export default Sidebar;
