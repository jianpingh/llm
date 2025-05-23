import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from function_schema import get_user_balance_function
from fake_database import get_balance

# Load environment variables from .env
load_dotenv()

# Create OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")  # optional if using proxy or Azure
)

def chat_with_gpt(user_prompt, user_id):
    """
    Handles a user prompt using GPT-4-turbo and function calling for balance checking.
    """
    try:
        # Inject user_id into prompt so GPT can understand context
        messages = [
            {
                "role": "user",
                "content": f"My user ID is {user_id}. {user_prompt}"
            }
        ]

        # Step 1: Ask GPT to determine whether to call a function
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            functions=[get_user_balance_function],
            function_call="auto"
        )

        message = response.choices[0].message

        # Step 2: If GPT called a function, handle it
        if message.function_call:
            function_name = message.function_call.name
            arguments = json.loads(message.function_call.arguments)

            if function_name == "get_user_balance":
                # Simulate balance lookup
                result = get_balance(arguments["user_id"])
                function_response = json.dumps(result)

                # Step 3: Pass function result back to GPT for final response
                followup = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        *messages,
                        {
                            "role": "assistant",
                            "function_call": {
                                "name": function_name,
                                "arguments": json.dumps(arguments)
                            }
                        },
                        {
                            "role": "function",
                            "name": function_name,
                            "content": function_response
                        }
                    ]
                )

                final_msg = followup.choices[0].message
                if final_msg.content:
                    return final_msg.content
                else:
                    return f"✅ Function `{function_name}` executed successfully. (But no response message was returned.)"

        # If GPT didn't call any function, return normal response
        return message.content or "No function call was made and no reply was returned."

    except Exception as e:
        print("❌ GPT handler error:", e)
        return "Sorry, something went wrong while processing your request."
