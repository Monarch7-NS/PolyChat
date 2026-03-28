import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import ChatPanel from './components/ChatPanel';
import ProfileModal from './components/ProfileModal';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const WS_URL = API_URL.replace(/^http/, 'ws');

function App() {
  const [username, setUsername] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState(new Set());
  const [selectedUser, setSelectedUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [typingUsers, setTypingUsers] = useState(new Set());
  const [searchResults, setSearchResults] = useState([]);
  const [profileUser, setProfileUser] = useState(null);

  const ws = useRef(null);
  const selectedUserRef = useRef(null);
  const currentUserRef = useRef('');
  const typingTimers = useRef({});

  const searchUsers = useCallback(async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    try {
      const res = await axios.get(`${API_URL}/api/users/search`, {
        params: { query: query.trim() },
      });
      // Filter out self and people already in conversations list
      const filtered = (res.data.users || []).filter(
        (u) => u !== currentUserRef.current && !conversations.find((c) => c.other_user === u)
      );
      setSearchResults(filtered);
    } catch (_) {}
  }, [conversations]);

  const fetchConversations = useCallback(async (user) => {
    try {
      const res = await axios.get(`${API_URL}/api/conversations/${user}`);
      setConversations(res.data.conversations || []);
    } catch (_) {}
  }, []);

  const fetchOnlineUsers = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/users/online`);
      setOnlineUsers(new Set(res.data.users || []));
    } catch (_) {}
  }, []);

  const markAsRead = useCallback(async (fromUser, toUser) => {
    try {
      await axios.put(`${API_URL}/api/conversations/read`, null, {
        params: { from_user: fromUser, to_user: toUser },
      });
    } catch (_) {}
  }, []);

  const handleWsMessage = useCallback(
    (event) => {
      try {
        const data = JSON.parse(event.data);
        switch (data.type) {
          case 'new_message':
            if (data.from === selectedUserRef.current) {
              setMessages((prev) => [...prev, data]);
              markAsRead(data.from, currentUserRef.current);
            } else {
              setConversations((prev) => {
                const exists = prev.find((c) => c.other_user === data.from);
                const updated = exists
                  ? prev
                      .map((c) =>
                        c.other_user === data.from
                          ? { ...c, unread_count: c.unread_count + 1, last_message: data.content, updated_at: data.timestamp }
                          : c
                      )
                      .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
                  : [{ other_user: data.from, last_message: data.content, updated_at: data.timestamp, unread_count: 1 }, ...prev];
                return updated;
              });
            }
            break;
          case 'typing':
            setTypingUsers((prev) => new Set([...prev, data.from]));
            clearTimeout(typingTimers.current[data.from]);
            typingTimers.current[data.from] = setTimeout(() => {
              setTypingUsers((prev) => {
                const next = new Set(prev);
                next.delete(data.from);
                return next;
              });
            }, 3000);
            break;
          case 'stop_typing':
            setTypingUsers((prev) => {
              const next = new Set(prev);
              next.delete(data.from);
              return next;
            });
            break;
          default:
            break;
        }
      } catch (_) {}
    },
    [markAsRead]
  );

  const handleWsMessageRef = useRef(handleWsMessage);
  useEffect(() => {
    handleWsMessageRef.current = handleWsMessage;
  }, [handleWsMessage]);

  useEffect(() => {
    if (!isLoggedIn) return;
    currentUserRef.current = username;

    ws.current = new WebSocket(`${WS_URL}/ws/${username}`);
    ws.current.onmessage = (e) => handleWsMessageRef.current(e);
    ws.current.onerror = () => {};

    fetchConversations(username);
    fetchOnlineUsers();
    const interval = setInterval(fetchOnlineUsers, 10000);

    return () => {
      clearInterval(interval);
      ws.current?.close();
    };
  }, [isLoggedIn, username, fetchConversations, fetchOnlineUsers]);

  const selectUser = useCallback(
    async (otherUser) => {
      selectedUserRef.current = otherUser;
      setSelectedUser(otherUser);
      setSearchResults([]);
      try {
        const res = await axios.get(`${API_URL}/api/messages/conversation`, {
          params: { user1: currentUserRef.current, user2: otherUser },
        });
        setMessages(res.data.messages || []);
      } catch (_) {}
      await markAsRead(otherUser, currentUserRef.current);
      setConversations((prev) =>
        prev.map((c) => (c.other_user === otherUser ? { ...c, unread_count: 0 } : c))
      );
    },
    [markAsRead]
  );

  const handleLogin = async (inputUsername) => {
    const trimmed = inputUsername.trim();
    if (!trimmed) return;
    try {
      await axios.post(`${API_URL}/api/users/login`, { username: trimmed });
      setUsername(trimmed);
      setIsLoggedIn(true);
    } catch (_) {
      alert('Erreur de connexion');
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API_URL}/api/users/logout`, { username });
    } catch (_) {}
    ws.current?.close();
    selectedUserRef.current = null;
    setIsLoggedIn(false);
    setUsername('');
    setConversations([]);
    setSelectedUser(null);
    setMessages([]);
    setOnlineUsers(new Set());
    setTypingUsers(new Set());
  };

  const handleSendMessage = async (content) => {
    if (!content.trim() || !selectedUser) return;
    const now = new Date().toISOString();
    try {
      await axios.post(`${API_URL}/api/messages/send`, {
        from_user: username,
        to_user: selectedUser,
        content: content.trim(),
      });
      setMessages((prev) => [
        ...prev,
        { from: username, to: selectedUser, content: content.trim(), timestamp: now, read: false },
      ]);
      setConversations((prev) => {
        const updated = { other_user: selectedUser, last_message: content.trim(), updated_at: now, unread_count: 0 };
        return [updated, ...prev.filter((c) => c.other_user !== selectedUser)];
      });
    } catch (_) {}
  };

  const sendTyping = useCallback((type) => {
    if (ws.current?.readyState === WebSocket.OPEN && selectedUserRef.current) {
      ws.current.send(JSON.stringify({ type, to: selectedUserRef.current }));
    }
  }, []);

  if (!isLoggedIn) return <Login onLogin={handleLogin} />;

  return (
    <div className="app">
      <Sidebar
        username={username}
        conversations={conversations}
        onlineUsers={onlineUsers}
        selectedUser={selectedUser}
        onSelectUser={selectUser}
        onLogout={handleLogout}
        searchResults={searchResults}
        onSearch={searchUsers}
      />
      <ChatPanel
        username={username}
        selectedUser={selectedUser}
        messages={messages}
        typingUsers={typingUsers}
        onSendMessage={handleSendMessage}
        onTyping={sendTyping}
        isOnline={onlineUsers.has(selectedUser)}
        onShowProfile={(u) => setProfileUser(u)}
      />
      {profileUser && (
        <ProfileModal username={profileUser} onClose={() => setProfileUser(null)} />
      )}
    </div>
  );
}

export default App;
