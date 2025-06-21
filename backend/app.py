from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS to allow requests from GitHub Pages and other origins
CORS(app, origins=[
    "https://goodboyagi.github.io",
    "https://goodboyagi.com", 
    "https://goodboyagi.com/greeting-card-generator",
    "http://localhost:5000",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "null"  # Allow file:// protocol
], methods=["GET", "POST", "OPTIONS"])

# Get API keys from environment variables (secure)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')

# Configure OpenAI
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

# Simple usage tracking
USAGE_FILE = 'usage_stats.json'

def load_usage_stats():
    """Load usage statistics from file"""
    try:
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {
        'total_requests': 0,
        'successful_requests': 0,
        'failed_requests': 0,
        'last_request': None,
        'requests_by_occasion': {},
        'requests_by_style': {}
    }

def save_usage_stats(stats):
    """Save usage statistics to file"""
    try:
        with open(USAGE_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except:
        pass

def track_request(occasion=None, style=None, success=True):
    """Track API request"""
    stats = load_usage_stats()
    stats['total_requests'] += 1
    stats['last_request'] = datetime.now().isoformat()
    
    if success:
        stats['successful_requests'] += 1
    else:
        stats['failed_requests'] += 1
    
    if occasion:
        stats['requests_by_occasion'][occasion] = stats['requests_by_occasion'].get(occasion, 0) + 1
    
    if style:
        stats['requests_by_style'][style] = stats['requests_by_style'].get(style, 0) + 1
    
    save_usage_stats(stats)

def get_image_suggestion(occasion, style):
    """Generate image suggestion based on occasion and style"""
    image_map = {
        'birthday': {
            'friendly': '🎉',
            'formal': '🎂',
            'funny': '🎭',
            'romantic': '💕'
        },
        'anniversary': {
            'friendly': '🥂',
            'formal': '💍',
            'funny': '🎭',
            'romantic': '💖'
        },
        'wedding': {
            'friendly': '💒',
            'formal': '👰',
            'funny': '🎭',
            'romantic': '💕'
        },
        'graduation': {
            'friendly': '🎓',
            'formal': '🎓',
            'funny': '🎭',
            'romantic': '🌟'
        },
        'thank_you': {
            'friendly': '🙏',
            'formal': '💐',
            'funny': '🎭',
            'romantic': '💝'
        },
        'congratulations': {
            'friendly': '🎉',
            'formal': '🏆',
            'funny': '🎭',
            'romantic': '💫'
        },
        'get_well': {
            'friendly': '🤗',
            'formal': '💊',
            'funny': '🎭',
            'romantic': '💝'
        },
        'sympathy': {
            'friendly': '🤗',
            'formal': '🕊️',
            'funny': '🎭',
            'romantic': '💝'
        },
        'holiday': {
            'friendly': '🎄',
            'formal': '🎁',
            'funny': '🎭',
            'romantic': '💝'
        }
    }
    
    # Get the appropriate image for the occasion and style
    occasion_images = image_map.get(occasion, image_map['birthday'])
    image = occasion_images.get(style, occasion_images['friendly'])
    
    return image

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint for debugging"""
    return jsonify({
        'message': 'API is working!',
        'timestamp': '2025-06-21'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Greeting Card Generator API is running',
        'openai_configured': bool(OPENAI_API_KEY),
        'huggingface_configured': bool(HUGGINGFACE_TOKEN)
    })

@app.route('/api/generate-text', methods=['POST'])
def generate_text():
    """Generate greeting card text using OpenAI API"""
    if not client:
        return jsonify({'error': 'OpenAI API key not configured'}), 500
    
    try:
        data = request.get_json()
        recipient = data.get('recipient', '')
        occasion = data.get('occasion', '')
        style = data.get('style', 'friendly')
        message = data.get('message', '')
        
        # Create a detailed prompt for OpenAI
        prompt = f"""Create a personalized greeting card message for {recipient} for a {occasion} occasion. 

Style: {style}
Additional personal message from sender: {message if message else 'None'}

Please create a warm, personalized greeting card message that is:
- Appropriate for the {occasion} occasion
- Written in a {style} tone
- Personal and heartfelt
- Include the recipient's name naturally
- If there's an additional message from the sender, incorporate it gracefully

Keep the message concise but meaningful (2-3 sentences)."""

        # Call OpenAI API with new format
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative greeting card writer who creates personalized, warm, and appropriate messages for various occasions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        generated_text = response.choices[0].message.content.strip()
        
        # Generate image suggestion based on occasion and style
        image_suggestion = get_image_suggestion(occasion, style)
        
        track_request(occasion, style, True)
        
        return jsonify({
            'success': True,
            'generated_text': generated_text,
            'image_suggestion': image_suggestion
        })
    
    except Exception as e:
        print(f"Error generating text: {str(e)}")
        track_request(occasion, style, False)
        return jsonify({'error': str(e)}), 500

@app.route('/api/styles', methods=['GET'])
def get_styles():
    """Get available card styles"""
    styles = [
        {'id': 'friendly', 'name': 'Friendly', 'description': 'Warm and casual'},
        {'id': 'formal', 'name': 'Formal', 'description': 'Professional and polite'},
        {'id': 'funny', 'name': 'Humorous', 'description': 'Light-hearted and fun'},
        {'id': 'romantic', 'name': 'Romantic', 'description': 'Sweet and loving'}
    ]
    return jsonify(styles)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    stats = load_usage_stats()
    return jsonify(stats)

if __name__ == '__main__':
    # Check if API keys are configured
    if not OPENAI_API_KEY:
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Create a .env file with your API keys for full functionality")
    
    # Get port from environment variable (for production) or use 5001 for local development
    port = int(os.environ.get('PORT', 5001))
    
    # Use debug=False for production
    app.run(debug=False, host='0.0.0.0', port=port) 