import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from function_schema import *
from fake_database import *

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

def chat_with_agent(user_prompt, user_id):
    messages = [{
        "role": "user",
        "content": f"My user ID is {user_id}. {user_prompt}"
    }]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        functions=all_functions,
        function_call="auto"
    )

    message = response.choices[0].message

    if message.function_call:
        name = message.function_call.name
        args = json.loads(message.function_call.arguments)

        if name == "get_user_balance":
            result = get_balance(args["user_id"])
        elif name == "get_transaction_history":
            result = get_transaction_history(args["user_id"], args.get("limit", 5))
        elif name == "transfer_funds":
            result = transfer_funds(args["from_user"], args["to_user"], args["amount"])
        elif name == "search_orders":
            result = search_orders(args["user_id"], args["keyword"])
        else:
            result = {"error": "Unknown function"}

        followup = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                *messages,
                {
                    "role": "assistant",
                    "function_call": {
                        "name": name,
                        "arguments": json.dumps(args)
                    }
                },
                {
                    "role": "function",
                    "name": name,
                    "content": json.dumps(result)
                }
            ]
        )

        final_msg = followup.choices[0].message
        return final_msg.content or f"Function `{name}` executed."

    return message.content or "No action taken."
