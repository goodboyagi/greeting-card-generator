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

def generate_dalle_image(occasion, style, recipient, generated_text):
    """Generate an image using DALL-E based on the greeting card content"""
    try:
        # Create a prompt for DALL-E based on the occasion, style, and content
        image_prompts = {
            'birthday': {
                'friendly': f"Colorful birthday celebration with balloons, cake, and party decorations. Warm, cheerful atmosphere. Perfect for a greeting card for {recipient}.",
                'formal': f"Elegant birthday cake with candles, sophisticated celebration setting. Professional greeting card style for {recipient}.",
                'funny': f"Whimsical birthday scene with cartoon characters, confetti, and fun elements. Humorous greeting card for {recipient}.",
                'romantic': f"Soft, romantic birthday scene with flowers, candles, and warm lighting. Loving greeting card for {recipient}."
            },
            'anniversary': {
                'friendly': f"Celebration of love and partnership with champagne glasses, flowers, and romantic setting. Warm greeting card for {recipient}.",
                'formal': f"Elegant anniversary celebration with roses, fine dining setting, and sophisticated atmosphere. Formal greeting card for {recipient}.",
                'funny': f"Playful anniversary scene with cartoon hearts, funny elements, and celebration. Humorous greeting card for {recipient}.",
                'romantic': f"Romantic anniversary scene with roses, candles, and intimate setting. Loving greeting card for {recipient}."
            },
            'wedding': {
                'friendly': f"Beautiful wedding celebration with flowers, rings, and happy atmosphere. Warm greeting card for {recipient}.",
                'formal': f"Elegant wedding scene with white flowers, rings, and sophisticated setting. Formal greeting card for {recipient}.",
                'funny': f"Playful wedding scene with cartoon elements and celebration. Humorous greeting card for {recipient}.",
                'romantic': f"Romantic wedding scene with roses, rings, and dreamy atmosphere. Loving greeting card for {recipient}."
            },
            'graduation': {
                'friendly': f"Graduation celebration with cap, diploma, and achievement symbols. Warm greeting card for {recipient}.",
                'formal': f"Elegant graduation scene with academic symbols and formal setting. Professional greeting card for {recipient}.",
                'funny': f"Playful graduation scene with cartoon elements and celebration. Humorous greeting card for {recipient}.",
                'romantic': f"Romantic graduation scene with flowers and achievement celebration. Loving greeting card for {recipient}."
            },
            'thank_you': {
                'friendly': f"Gratitude scene with flowers, thank you symbols, and warm atmosphere. Friendly greeting card for {recipient}.",
                'formal': f"Elegant thank you scene with formal flowers and sophisticated setting. Professional greeting card for {recipient}.",
                'funny': f"Playful thank you scene with cartoon elements and fun symbols. Humorous greeting card for {recipient}.",
                'romantic': f"Romantic thank you scene with roses and loving atmosphere. Sweet greeting card for {recipient}."
            },
            'congratulations': {
                'friendly': f"Celebration scene with confetti, achievement symbols, and warm atmosphere. Friendly greeting card for {recipient}.",
                'formal': f"Elegant congratulations scene with formal celebration elements. Professional greeting card for {recipient}.",
                'funny': f"Playful congratulations scene with cartoon celebration elements. Humorous greeting card for {recipient}.",
                'romantic': f"Romantic congratulations scene with flowers and loving celebration. Sweet greeting card for {recipient}."
            },
            'get_well': {
                'friendly': f"Healing scene with flowers, get well symbols, and warm atmosphere. Caring greeting card for {recipient}.",
                'formal': f"Elegant get well scene with formal flowers and healing symbols. Professional greeting card for {recipient}.",
                'funny': f"Playful get well scene with cartoon healing elements. Humorous greeting card for {recipient}.",
                'romantic': f"Romantic get well scene with roses and caring atmosphere. Loving greeting card for {recipient}."
            },
            'sympathy': {
                'friendly': f"Peaceful sympathy scene with white flowers and calming atmosphere. Caring greeting card for {recipient}.",
                'formal': f"Elegant sympathy scene with formal white flowers and respectful setting. Professional greeting card for {recipient}.",
                'funny': f"Gentle sympathy scene with soft colors and caring elements. Thoughtful greeting card for {recipient}.",
                'romantic': f"Romantic sympathy scene with white roses and loving atmosphere. Caring greeting card for {recipient}."
            },
            'holiday': {
                'friendly': f"Holiday celebration scene with festive decorations and warm atmosphere. Friendly greeting card for {recipient}.",
                'formal': f"Elegant holiday scene with formal decorations and sophisticated setting. Professional greeting card for {recipient}.",
                'funny': f"Playful holiday scene with cartoon festive elements. Humorous greeting card for {recipient}.",
                'romantic': f"Romantic holiday scene with festive flowers and loving atmosphere. Sweet greeting card for {recipient}."
            }
        }
        
        # Get the appropriate prompt for the occasion and style
        occasion_prompts = image_prompts.get(occasion, image_prompts['birthday'])
        prompt = occasion_prompts.get(style, occasion_prompts['friendly'])
        
        # Add style-specific instructions
        style_instructions = {
            'friendly': "Use warm, bright colors and friendly imagery.",
            'formal': "Use elegant, sophisticated colors and formal imagery.",
            'funny': "Use playful, cartoon-style imagery with bright colors.",
            'romantic': "Use soft, romantic colors and loving imagery."
        }
        
        full_prompt = f"{prompt} {style_instructions.get(style, '')} Create a beautiful greeting card image that matches the message: '{generated_text[:100]}...'"
        
        # Generate image using DALL-E
        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Return the image URL
        return response.data[0].url
        
    except Exception as e:
        print(f"Error generating DALL-E image: {str(e)}")
        return None

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
        
        # Generate DALL-E image
        generated_image_url = generate_dalle_image(occasion, style, recipient, generated_text)
        
        track_request(occasion, style, True)
        
        return jsonify({
            'success': True,
            'generated_text': generated_text,
            'image_suggestion': image_suggestion,
            'generated_image_url': generated_image_url
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