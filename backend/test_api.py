#!/usr/bin/env python3
"""
Simple test script to verify OpenAI API key is working
"""

import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

def test_openai_api():
    """Test if OpenAI API key is working"""
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    if api_key == "your_actual_openai_api_key_here":
        print("❌ Please replace the placeholder API key with your actual key in .env file")
        return False
    
    try:
        # Configure OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple request
        print("🧪 Testing OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello from Good Boy AGI!' in a friendly way"}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI API is working!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenAI API: {e}")
        return False

if __name__ == "__main__":
    test_openai_api() 