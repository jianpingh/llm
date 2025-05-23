from langchain.tools import tool
from fake_database import get_balance, transfer_funds as do_transfer, get_transaction_history, search_orders

@tool
def get_user_balance(user_id: str) -> str:
    """Get a user's balance."""
    data = get_balance(user_id)
    return f"Balance for {user_id}: {data['balance']} {data['currency']}"

@tool
def transfer_funds(from_user: str, to_user: str, amount: float) -> str:
    """Transfer funds between users."""
    result = do_transfer(from_user, to_user, amount)
    return f"Transferred {amount} from {from_user} to {to_user}."

@tool
def get_transaction_history(user_id: str, limit: int = 5) -> str:
    """Retrieve recent transactions for a user."""
    txs = get_transaction_history(user_id, limit)
    return f"Recent transactions for {user_id}: {txs['transactions']}"

@tool
def search_orders(user_id: str, keyword: str) -> str:
    """Search orders by keyword."""
    result = search_orders(user_id, keyword)
    return f"Search results: {result['matched_orders']}"
