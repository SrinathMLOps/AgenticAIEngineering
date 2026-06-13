"""
Quick API Key Test Script
Run this to verify your Anthropic API key is valid
"""
import os
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

print("\n" + "="*60)
print("🔑 API Key Test")
print("="*60 + "\n")

# Check if key exists
if not api_key:
    print("❌ ERROR: No API key found in .env file")
    print("   Make sure your .env file has:")
    print("   ANTHROPIC_API_KEY=sk-ant-...")
    exit(1)

# Check key format
if not api_key.startswith("sk-ant-"):
    print(f"⚠️  WARNING: Key doesn't start with 'sk-ant-'")
    print(f"   Your key starts with: {api_key[:10]}...")

# Show key info (partially hidden for security)
print(f"✓ API key found")
print(f"  First 20 chars: {api_key[:20]}...")
print(f"  Last 10 chars:  ...{api_key[-10:]}")
print(f"  Total length:   {len(api_key)} characters")
print()

# Expected length (typical Anthropic keys are ~100-110 characters)
if len(api_key) < 90:
    print("⚠️  WARNING: Key seems SHORT (typical keys are 100+ chars)")
    print("   Your key might be incomplete!")
elif len(api_key) > 120:
    print("⚠️  WARNING: Key seems LONG (might have extra characters)")
else:
    print("✓ Key length looks reasonable")

print("\n" + "-"*60)
print("Testing API connection...")
print("-"*60 + "\n")

try:
    # Try to make a simple API call
    client = anthropic.Anthropic(api_key=api_key)
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=50,
        messages=[
            {"role": "user", "content": "Say 'Hello, API key works!'"}
        ]
    )
    
    print("✅ SUCCESS! Your API key is VALID!")
    print(f"\nClaude says: {response.content[0].text}")
    print(f"\nTokens used: {response.usage.input_tokens} input, {response.usage.output_tokens} output")
    print("\n" + "="*60)
    print("🎉 You're ready to run the agent!")
    print("="*60)
    print("\nRun: python main.py")
    print("Or:  python dashboard.py")
    
except anthropic.AuthenticationError as e:
    print("❌ AUTHENTICATION ERROR")
    print(f"   {e}")
    print("\n📝 What to do:")
    print("   1. Go to https://console.anthropic.com/settings/keys")
    print("   2. Create a NEW API key")
    print("   3. Click 'Copy' button (don't select manually)")
    print("   4. Paste it in your .env file on ONE line")
    print("   5. Run this test again: python test_api_key.py")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nCheck your internet connection and try again.")

print()
