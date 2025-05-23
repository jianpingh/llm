import os
import json
import openai
from dotenv import load_dotenv
from function_schema import get_user_balance_function
from fake_database import get_balance

# Load .env variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.base_url = os.getenv("OPENAI_API_BASE")  # Optional; set if using a proxy or Azure

def chat_with_gpt(user_prompt, user_id):
    """
    Handle the conversation with GPT, including function calling if needed.
    """
    # User message
    messages = [
        {"role": "user", "content": user_prompt}
    ]

    # First GPT call: decide whether to call a function
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",  # or "gpt-3.5-turbo-0613"
        messages=messages,
        functions=[get_user_balance_function],
        function_call="auto"
    )

    message = response["choices"][0]["message"]

    # If function_call is requested
    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        arguments = json.loads(message["function_call"]["arguments"])

        # Handle get_user_balance
        if function_name == "get_user_balance":
            result = get_balance(arguments["user_id"])  # You can pass user_id from session instead
            function_response = json.dumps(result)

            # Second GPT call: send function result to GPT and get final message
            followup = openai.ChatCompletion.create(
                model="gpt-4-0613",
                messages=[
                    *messages,
                    message,
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response
                    }
                ]
            )
            return followup["choices"][0]["message"]["content"]

    # No function call needed, just return the model response
    return message["content"]
