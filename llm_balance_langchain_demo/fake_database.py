FAKE_USERS = {
    "user_123": {"balance": 305.75, "currency": "USD"},
    "user_456": {"balance": 1000.00, "currency": "EUR"},
}

def get_balance(user_id):
    return FAKE_USERS.get(user_id, {"balance": 0, "currency": "USD"})

def get_transaction_history(user_id, limit=5):
    return {
        "user_id": user_id,
        "transactions": [
            {"type": "withdraw", "amount": 50, "date": "2024-05-01"},
            {"type": "deposit", "amount": 100, "date": "2024-04-28"}
        ][:limit]
    }

def transfer_funds(from_user, to_user, amount):
    return {
        "status": "success",
        "from": from_user,
        "to": to_user,
        "amount": amount
    }

def search_orders(user_id, keyword):
    return {
        "user_id": user_id,
        "matched_orders": [
            {"id": "ORD001", "item": "keyboard"},
            {"id": "ORD002", "item": "usb cable"}
        ] if "key" in keyword.lower() else []
    }
