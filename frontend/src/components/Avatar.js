import React from 'react';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f59e0b', '#ef4444', '#10b981', '#3b82f6'];

function stringToColor(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return COLORS[Math.abs(hash) % COLORS.length];
}

function Avatar({ username, size = 38 }) {
  return (
    <div style={{
      backgroundColor: stringToColor(username),
      width: size,
      height: size,
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: size * 0.4,
      fontWeight: 700,
      color: '#fff',
      flexShrink: 0,
      userSelect: 'none',
    }}>
      {username[0].toUpperCase()}
    </div>
  );
}

export default Avatar;
