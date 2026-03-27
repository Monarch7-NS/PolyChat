import React, { useState, useEffect, useRef } from 'react';
import Avatar from './Avatar';

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDate(iso) {
  const d = new Date(iso);
  const now = new Date();
  if (d.toDateString() === now.toDateString()) return "Aujourd'hui";
  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  if (d.toDateString() === yesterday.toDateString()) return 'Hier';
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' });
}

function TypingDots() {
  return (
    <span className="typing-dots">
      <span /><span /><span />
    </span>
  );
}

function ChatPanel({ username, selectedUser, messages, typingUsers, onSendMessage, onTyping, isOnline }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const typingTimer = useRef(null);
  const isTypingRef = useRef(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typingUsers]);

  // Reset input when changing conversation
  useEffect(() => {
    setInput('');
  }, [selectedUser]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
    if (!isTypingRef.current) {
      isTypingRef.current = true;
      onTyping('typing');
    }
    clearTimeout(typingTimer.current);
    typingTimer.current = setTimeout(() => {
      isTypingRef.current = false;
      onTyping('stop_typing');
    }, 2000);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSendMessage(input);
    setInput('');
    clearTimeout(typingTimer.current);
    isTypingRef.current = false;
    onTyping('stop_typing');
  };

  if (!selectedUser) {
    return (
      <main className="chat-panel empty-state">
        <div className="empty-state-content">
          <div className="empty-state-icon">💬</div>
          <h2>PolyChat</h2>
          <p>Sélectionnez une conversation pour commencer</p>
        </div>
      </main>
    );
  }

  // Group messages by date
  const grouped = [];
  let lastDate = null;
  for (const msg of messages) {
    const date = formatDate(msg.timestamp);
    if (date !== lastDate) {
      grouped.push({ type: 'date', label: date, key: `date-${date}` });
      lastDate = date;
    }
    grouped.push({ type: 'message', ...msg });
  }

  const isTypingForMe = typingUsers.has(selectedUser);

  return (
    <main className="chat-panel">
      <div className="chat-header">
        <Avatar username={selectedUser} size={40} />
        <div className="chat-header-info">
          <span className="chat-header-name">{selectedUser}</span>
          <span className={`chat-header-status ${isOnline ? 'online' : 'offline'}`}>
            {isOnline ? 'En ligne' : 'Hors ligne'}
          </span>
        </div>
      </div>

      <div className="messages-list">
        {grouped.map((item, i) =>
          item.type === 'date' ? (
            <div key={item.key} className="date-divider">
              <span>{item.label}</span>
            </div>
          ) : (
            <div key={i} className={`message-row ${item.from === username ? 'sent' : 'received'}`}>
              {item.from !== username && <Avatar username={item.from} size={28} />}
              <div className={`message-bubble ${item.from === username ? 'bubble-sent' : 'bubble-received'}`}>
                <p>{item.content}</p>
                <span className="message-time">{formatTime(item.timestamp)}</span>
              </div>
            </div>
          )
        )}

        {isTypingForMe && (
          <div className="message-row received">
            <Avatar username={selectedUser} size={28} />
            <div className="message-bubble bubble-received typing-bubble">
              <TypingDots />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="message-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder={`Message à ${selectedUser}...`}
          value={input}
          onChange={handleInputChange}
          autoFocus
        />
        <button type="submit" disabled={!input.trim()}>
          ➤
        </button>
      </form>
    </main>
  );
}

export default ChatPanel;
