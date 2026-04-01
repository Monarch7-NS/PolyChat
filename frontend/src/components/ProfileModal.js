import React from 'react';
import Avatar from './Avatar';

function ProfileModal({ username, onClose }) {
  if (!username) return null;

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
          <div className="profile-info-item">
            <span className="info-label">Bio</span>
            <p className="info-value">Passionné de messagerie temps réel et de NoSQL.</p>
          </div>
          <div className="profile-info-item">
            <span className="info-label">Localisation</span>
            <p className="info-value">PolyTech, France</p>
          </div>
        </div>
        <div className="profile-footer">
          <button className="btn-primary" onClick={onClose}>Fermer</button>
        </div>
      </div>
    </div>
  );
}

export default ProfileModal;
