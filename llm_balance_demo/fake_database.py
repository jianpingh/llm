FAKE_USERS = {
    "user_123": {"balance": 305.75, "currency": "USD"},
    "user_456": {"balance": 1000.00, "currency": "EUR"},
}

def get_balance(user_id: str):
    return FAKE_USERS.get(user_id, {"balance": 0, "currency": "USD"})
