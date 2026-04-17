import pytest
from fastapi.testclient import TestClient
import mongomock
from unittest.mock import MagicMock
from app.main import app
import app.database

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_mock_db():
    # Remplacer les clients globaux par des mocks pour les tests
    mock_client = mongomock.MongoClient()
    app.database.db = mock_client.polychat_test
    
    # Simuler le client Redis
    mock_redis = MagicMock()
    app.database.redis_client = mock_redis
    
    # Nettoyer les collections entre chaque test (optionnel avec un db neuf, mais bonne pratique)
    app.database.db.messages.delete_many({})
    app.database.db.conversations.delete_many({})
    
    yield

def test_send_message_and_retrieve_conversation():
    # 1. Envoi de plusieurs messages
    res1 = client.post("/api/messages/send", json={
        "from_user": "alice",
        "to_user": "bob",
        "content": "Bonjour Bob!"
    })
    assert res1.status_code == 201
    
    res2 = client.post("/api/messages/send", json={
        "from_user": "bob",
        "to_user": "alice",
        "content": "Salut Alice!"
    })
    assert res2.status_code == 201
    
    # 2. Récupérer la conversation
    convo_res = client.get("/api/messages/conversation?user1=alice&user2=bob")
    assert convo_res.status_code == 200
    messages = convo_res.json()["messages"]
    
    assert len(messages) == 2
    assert messages[0]["content"] == "Bonjour Bob!"
    assert messages[1]["content"] == "Salut Alice!"

def test_get_user_conversations():
    # Insert de deux conversations avec des personnes différentes
    client.post("/api/messages/send", json={"from_user": "alice", "to_user": "bob", "content": "A"})
    client.post("/api/messages/send", json={"from_user": "charlie", "to_user": "alice", "content": "B"})
    
    res = client.get("/api/conversations/alice")
    assert res.status_code == 200
    convos = res.json()["conversations"]
    assert len(convos) == 2
    
    others = [c["other_user"] for c in convos]
    assert "bob" in others
    assert "charlie" in others

def test_stats_top_sender_receiver():
    # alice envoie 2 messages, charlie 1 message
    # bob reçoit 3 messages
    client.post("/api/messages/send", json={"from_user": "alice", "to_user": "bob", "content": "1"})
    client.post("/api/messages/send", json={"from_user": "alice", "to_user": "bob", "content": "2"})
    client.post("/api/messages/send", json={"from_user": "charlie", "to_user": "bob", "content": "3"})
    
    res_sender = client.get("/api/stats/top-sender")
    assert res_sender.status_code == 200
    assert res_sender.json()["username"] == "alice"
    assert res_sender.json()["message_count"] == 2
    
    res_receiver = client.get("/api/stats/top-receiver")
    assert res_receiver.status_code == 200
    assert res_receiver.json()["username"] == "bob"
    assert res_receiver.json()["message_count"] == 3

def test_stats_user_activity():
    client.post("/api/messages/send", json={"from_user": "alice", "to_user": "bob", "content": "1"})
    
    res = client.get("/api/stats/user-activity/alice")
    assert res.status_code == 200
    data = res.json()
    assert data["messages_sent"] == 1
    assert data["messages_received"] == 0
    assert data["top_contact"] == "bob"
