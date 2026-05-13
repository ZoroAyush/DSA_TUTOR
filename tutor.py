import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Load the secret API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: Could not find the API key. Check your .env file.")
    exit()

# 2. Initialize the client
client = genai.Client(api_key=API_KEY)

# 3. Define the Tutor's Brain (System Instructions)
# This strictly controls how the AI is allowed to respond
tutor_rules = """
You are an expert, highly analytical Data Structures and Algorithms (DSA) tutor.
Your goal is to help the user prepare for rigorous technical interviews, focusing on 
patterns commonly found in resources like the Striver A2Z DSA sheet.

CRITICAL RULES:
1. NEVER give the complete code or the direct answer right away.
2. If the user is stuck, provide a conceptual hint or ask a guiding question.
3. Focus heavily on time/space complexity and edge cases.
4. Encourage the user to dry-run their logic and understand the line-by-line execution of the algorithm.
5. Keep your responses concise and readable.
"""

# 4. Start an interactive Chat Session
print("Starting up your personal DSA Tutor... (Type 'quit' to exit)\n")
print("-" * 40)

try:
    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=tutor_rules,
            temperature=0.3 # Lower temperature makes the AI more logical and precise
        )
    )
except Exception as e:
    print(f"Failed to start chat: {e}")
    exit()

# 5. The Terminal Chat Loop
while True:
    # Get user input
    user_message = input("\nYou: ")
    
    # Check if the user wants to exit
    if user_message.lower() in ['quit', 'exit']:
        print("Tutor: Good luck with your coding! Goodbye.")
        break
        
    # Send the message with automatic retry for traffic spikes
    while True:
        try:
            response = chat.send_message(user_message)
            print(f"\nTutor: {response.text}")
            break # Break the retry loop and wait for the next user input
            
        except Exception as e:
            if "503" in str(e):
                print("\n[Server busy, retrying in 3 seconds...]")
                time.sleep(3)
            else:
                print(f"\n[An error occurred: {e}]")
                break