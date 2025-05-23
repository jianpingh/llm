get_user_balance_function = {
    "name": "get_user_balance",
    "description": "Get the current account balance of a user",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "The unique identifier of the user"
            }
        },
        "required": ["user_id"]
    }
}
