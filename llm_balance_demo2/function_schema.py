get_user_balance = {
    "name": "get_user_balance",
    "description": "Get the user's current account balance.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"}
        },
        "required": ["user_id"]
    }
}

get_transaction_history = {
    "name": "get_transaction_history",
    "description": "View recent transaction history.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "limit": {"type": "integer"}
        },
        "required": ["user_id"]
    }
}

transfer_funds = {
    "name": "transfer_funds",
    "description": "Transfer funds from one user to another.",
    "parameters": {
        "type": "object",
        "properties": {
            "from_user": {"type": "string"},
            "to_user": {"type": "string"},
            "amount": {"type": "number"}
        },
        "required": ["from_user", "to_user", "amount"]
    }
}

search_orders = {
    "name": "search_orders",
    "description": "Search user orders by keyword.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "keyword": {"type": "string"}
        },
        "required": ["user_id", "keyword"]
    }
}

all_functions = [
    get_user_balance,
    get_transaction_history,
    transfer_funds,
    search_orders
]
