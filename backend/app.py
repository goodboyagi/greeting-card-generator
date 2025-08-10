from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta
import json
import requests
import base64
import re
import secrets
import time

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
    print(f"[INFO] OpenAI client configured with GPT-4o-mini model")

# Always use absolute path for usage stats file
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
USAGE_FILE = os.path.join(BACKEND_DIR, 'usage_stats.json')
print(f"[INFO] Usage stats file: {USAGE_FILE}")

# In-memory stats cache for better persistence
STATS_CACHE = None

# Secure sharing storage (file-based for persistence across server restarts)
SHARED_CARDS_FILE = 'shared_cards.json'
SHARED_CARDS_CACHE = {}  # Cache for performance

# GitHub storage configuration (only for stats, not shared cards)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = 'goodboyagi/greeting-card-generator'
GITHUB_STATS_FILE = 'production_stats.json'

def extract_scene_keywords(recipient, occasion, message, generated_text):
    """
    Extracts key entities and themes from recipient, occasion, message, and especially generated_text.
    Returns a scene description string for DALL-E.
    """
    keywords = set()
    # Add recipient and occasion as possible themes
    if recipient:
        keywords.add(recipient)
    if occasion:
        keywords.add(occasion)
    # Add words from message and generated text
    text = f"{message} {generated_text}".replace("!", ".").replace("?", ".")
    # Simple noun extraction: capitalized words and known magical/fantasy terms
    capitalized = re.findall(r'\b([A-Z][a-zA-Z0-9]+)\b', generated_text)
    for word in capitalized:
        if word.lower() not in ["dear", "congratulations", "congratulation", "congrats", "happy", "best", "wishes", "regards", "sender", "name"]:
            keywords.add(word)
    # Remove generic words
    generic_words = set(["dear", "congratulations", "congratulation", "congrats", "happy", "best", "wishes", "regards", "on", "the", "a", "an", "and", "to", "for", "with", "of", "in", "is", "are", "you", "your", "from", "sender", "name", "won", "keep", "bright", "like", "just", "truly", "now", "have", "has", "this", "that", "it", "as", "be", "by", "at", "or", "but", "not", "so", "if", "out", "all", "we", "us", "they", "them", "he", "she", "his", "her", "their", "our", "ours", "mine", "yours", "theirs", "ourselves", "myself", "yourself", "himself", "herself", "itself", "themselves"])
    keywords = {k for k in keywords if k.lower() not in generic_words}
    # Build scene description
    scene = ", ".join(sorted(keywords))
    return scene

def extract_important_objects(generated_text, occasion, style):
    """
    Uses OpenAI to extract important objects and visual elements from the generated text.
    Returns a list of objects that should be included in the DALL-E image.
    """
    if not client:
        return []
    
    try:
        prompt = f"""Analyze this greeting card message and list the most important visual objects, elements, or themes that should be represented in a greeting card image.

Message: "{generated_text}"
Occasion: {occasion}
Style: {style}

Please list not more than 10 specific visual objects or elements that would make sense for a greeting card image. 
Could be less than ten too, if the message is short.
Focus on:
- Objects mentioned in the message
- Symbols appropriate for the occasion
- Elements that match the style (friendly, formal, funny, romantic)
- Visual elements that would enhance the message

IMPORTANT: Focus on safe, greeting card-appropriate elements:
- Flowers, candles, landscapes, objects, and symbolic elements
- Nature scenes, architectural elements, and abstract designs
- Celebration symbols, achievement markers, and thematic objects

Return only a comma-separated list of objects, no explanations. Example: "flowers, candles, warm lighting" """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at identifying visual elements for images."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        objects_text = response.choices[0].message.content.strip()
        # Clean up the response and split into list
        objects = [obj.strip() for obj in objects_text.split(',') if obj.strip()]
        print(f"[OBJECTS EXTRACTED] {objects}")
        return objects
        
    except Exception as e:
        print(f"Error extracting objects: {str(e)}")
        return []

def load_usage_stats():
    """Load usage statistics from file or environment variables"""
    global STATS_CACHE
    
    # Return cached stats if available
    if STATS_CACHE is not None:
        return STATS_CACHE
    
    try:
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, 'r') as f:
                stats = json.load(f)
                STATS_CACHE = stats
                print(f"[INFO] Loaded stats from file: {stats.get('total_requests', 0)} total requests")
                return stats
    except Exception as e:
        print(f"[ERROR] Failed to load usage stats from file: {e}")
    
    # Try to load from environment variables as backup
    try:
        env_stats = os.getenv('USAGE_STATS')
        if env_stats:
            stats = json.loads(env_stats)
            STATS_CACHE = stats
            print(f"[INFO] Loaded stats from environment: {stats.get('total_requests', 0)} total requests")
            return stats
    except Exception as e:
        print(f"[ERROR] Failed to load stats from environment: {e}")
    
    # Try to load from GitHub as persistent storage
    try:
        if GITHUB_TOKEN:
            stats = load_stats_from_github()
            if stats:
                STATS_CACHE = stats
                print(f"[INFO] Loaded stats from GitHub: {stats.get('total_requests', 0)} total requests")
                return stats
    except Exception as e:
        print(f"[ERROR] Failed to load stats from GitHub: {e}")
    
    # Return default stats
    default_stats = {
        'total_requests': 0,
        'successful_requests': 0,
        'failed_requests': 0,
        'last_request': None,
        'requests_by_occasion': {},
        'requests_by_style': {}
    }
    STATS_CACHE = default_stats
    return default_stats

def save_usage_stats(stats):
    """Save usage statistics to file and environment"""
    global STATS_CACHE
    STATS_CACHE = stats
    
    # Save to file
    try:
        with open(USAGE_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"[INFO] Saved stats to file: {stats.get('total_requests', 0)} total requests")
    except Exception as e:
        print(f"[ERROR] Failed to save usage stats to file: {e}")
    
    # Save to environment variable (for Render persistence)
    try:
        stats_json = json.dumps(stats)
        # Note: This won't persist across Render restarts, but helps with immediate persistence
        os.environ['USAGE_STATS'] = stats_json
    except Exception as e:
        print(f"[ERROR] Failed to save stats to environment: {e}")
    
    # Save to GitHub as persistent storage
    try:
        if GITHUB_TOKEN:
            save_stats_to_github(stats)
    except Exception as e:
        print(f"[ERROR] Failed to save stats to GitHub: {e}")

def track_request(occasion=None, style=None, success=True):
    """Track API request with improved persistence"""
    try:
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
        print(f"[INFO] Tracked request: {occasion} ({style}) - {'success' if success else 'failed'}")
        
    except Exception as e:
        print(f"[ERROR] Failed to track request: {e}")

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

def generate_dalle_image(occasion, style, recipient, generated_text, message):
    """Generate an image using DALL-E based on the greeting card content"""
    try:
        # Create a prompt for DALL-E based on the occasion, style, and content
        image_prompts = {
            'birthday': {
                'friendly': f"Colorful birthday celebration with balloons, cake, and party decorations. Warm, cheerful atmosphere. Clean picture.",
                'formal': f"Elegant birthday cake with candles, sophisticated celebration setting. Professional picture.",
                'funny': f"Whimsical birthday scene with cartoon characters, confetti, and fun elements. Humorous picture.",
                'romantic': f"Soft, romantic birthday scene with flowers, candles, and warm lighting. Loving picture."
            },
            'anniversary': {
                'friendly': f"Celebration of love and partnership with champagne glasses, flowers, and romantic setting. Warm picture.",
                'formal': f"Elegant anniversary celebration with roses, fine dining setting, and sophisticated atmosphere. Formal picture.",
                'funny': f"Playful anniversary scene with cartoon hearts, funny elements, and celebration. Humorous picture.",
                'romantic': f"Romantic anniversary scene with roses, candles, and intimate setting. Loving picture."
            },
            'wedding': {
                'friendly': f"Beautiful wedding celebration with flowers, rings, and happy atmosphere. Warm picture.",
                'formal': f"Elegant wedding scene with white flowers, rings, and sophisticated setting. Formal picture.",
                'funny': f"Playful wedding scene with cartoon elements and celebration. Humorous picture.",
                'romantic': f"Romantic wedding scene with roses, rings, and dreamy atmosphere. Loving picture."
            },
            'graduation': {
                'friendly': f"Graduation celebration with cap, diploma, and achievement symbols. Warm picture.",
                'formal': f"Elegant graduation scene with academic symbols and formal setting. Professional picture.",
                'funny': f"Playful graduation scene with cartoon elements and celebration. Humorous picture.",
                'romantic': f"Romantic graduation scene with flowers and achievement celebration. Loving picture."
            },
            'thank_you': {
                'friendly': f"Gratitude scene with flowers, thank you symbols, and warm atmosphere. Friendly picture.",
                'formal': f"Elegant thank you scene with formal flowers and sophisticated setting. Professional picture.",
                'funny': f"Playful thank you scene with cartoon elements and fun symbols. Humorous picture.",
                'romantic': f"Romantic thank you scene with roses and loving atmosphere. Sweet picture."
            },
            'congratulations': {
                'friendly': f"Victory celebration scene with confetti, trophies, achievement symbols, and warm atmosphere. Friendly picture.",
                'formal': f"Elegant congratulations scene with formal celebration elements, awards, and sophisticated atmosphere. Professional picture.",
                'funny': f"Playful congratulations scene with cartoon celebration elements, fun symbols, and humorous atmosphere. Humorous picture.",
                'romantic': f"Romantic congratulations scene with flowers and loving celebration atmosphere. Sweet picture."
            },
            'get_well': {
                'friendly': f"Healing scene with flowers, get well symbols, and warm atmosphere. Caring picture.",
                'formal': f"Elegant get well scene with formal flowers and healing symbols. Professional picture.",
                'funny': f"Playful get well scene with cartoon healing elements. Humorous picture.",
                'romantic': f"Romantic get well scene with roses and caring atmosphere. Loving picture."
            },
            'sympathy': {
                'friendly': f"Peaceful sympathy scene with white flowers and calming atmosphere. Caring picture.",
                'formal': f"Elegant sympathy scene with formal white flowers and respectful setting. Professional picture.",
                'funny': f"Gentle sympathy scene with soft colors and caring elements. Thoughtful picture.",
                'romantic': f"Romantic sympathy scene with white roses and loving atmosphere. Caring picture."
            },
            'holiday': {
                'friendly': f"Holiday celebration scene with festive decorations and warm atmosphere. Friendly picture.",
                'formal': f"Elegant holiday scene with formal decorations and sophisticated setting. Professional picture.",
                'funny': f"Playful holiday scene with cartoon festive elements. Humorous picture.",
                'romantic': f"Romantic holiday scene with festive flowers and loving atmosphere. Sweet picture."
            }
        }
        
        # Get the appropriate prompt for the occasion and style
        occasion_prompts = image_prompts.get(occasion, None)
        
        if occasion_prompts:
            # Use predefined prompt for known occasions
            prompt = occasion_prompts.get(style, occasion_prompts['friendly'])
        else:
            # Create a generic celebration prompt for custom occasions
            style_celebrations = {
                'friendly': f"Warm celebration scene with flowers, decorations, and joyful atmosphere for {occasion}. Perfect picture.",
                'formal': f"Elegant celebration scene with sophisticated decorations and formal atmosphere for {occasion}. Professional picture.",
                'funny': f"Playful celebration scene with cartoon elements and fun decorations for {occasion}. Humorous picture.",
                'romantic': f"Romantic celebration scene with soft lighting and loving atmosphere for {occasion}. Sweet picture."
            }
            prompt = style_celebrations.get(style, style_celebrations['friendly'])
        
        # Add style-specific instructions with positive focus
        style_instructions = {
            'friendly': "Use warm, bright colors and friendly imagery. Clean, minimalist picture suitable for printing. Focus on objects, nature, flowers, and abstract elements.",
            'formal': "Use elegant, sophisticated colors and formal imagery. Clean, professional picture suitable for printing. Focus on objects, architecture, landscapes, and abstract elements.",
            'funny': "Use playful, cartoon-style imagery with bright colors. Clean, fun picture suitable for printing. Focus on objects, symbols, and abstract elements.",
            'romantic': "Use soft, romantic colors and loving imagery. Clean, elegant picture suitable for printing. Focus on objects, flowers, candles, and abstract elements."
        }
        
        # Extract context from generated text to improve image relevance
        context_keywords = []
        
        # General theme detection based on keywords
        text_lower = generated_text.lower()
        
        # Achievement/Victory themes
        if any(word in text_lower for word in ["win", "won", "victory", "champion", "tournament", "competition", "achievement", "success"]):
            context_keywords.append("victory celebration theme")
        
        # Magical/Fantasy themes
        if any(word in text_lower for word in ["magical", "wizard", "spell", "magic", "fantasy", "enchanted", "mystical", "lumos", "accio", "wizarding", "harry"]):
            context_keywords.append("magical fantasy theme")
        
        # Academic themes
        if any(word in text_lower for word in ["graduation", "degree", "study", "academic", "university", "college", "school"]):
            context_keywords.append("academic achievement theme")
        
        # Love/Romance themes
        if any(word in text_lower for word in ["love", "romantic", "heart", "sweetheart", "darling", "beloved"]):
            context_keywords.append("romantic love theme")
        
        # Health/Recovery themes
        if any(word in text_lower for word in ["heal", "recovery", "well", "health", "strength", "courage"]):
            context_keywords.append("healing wellness theme")
        
        # Celebration themes
        if any(word in text_lower for word in ["party", "celebrate", "celebration", "festive", "joy", "happy"]):
            context_keywords.append("celebration festive theme")
        
        # Professional themes
        if any(word in text_lower for word in ["career", "job", "promotion", "business", "professional", "work"]):
            context_keywords.append("professional career theme")
        
        context_prompt = " " + " ".join(context_keywords) if context_keywords else ""
        
        # Create a clean, professional prompt that focuses on the visual picture
        full_prompt = f"{prompt}{context_prompt} {style_instructions.get(style, '')} Create a clean, professional greeting card background image. The image should be suitable for printing and email sharing. Focus on beautiful visual elements - objects, nature, landscapes, symbols, and abstract elements. IMPORTANT: This is a background image for a greeting card, not a greeting card with text on it."
        
        # Generate image using DALL-E
        '''
        print(f"[DALL-E PROMPT] {full_prompt}")
        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        '''
        
        # Extract important objects from the generated text using OpenAI
        important_objects = extract_important_objects(generated_text, occasion, style)
        
        # Start with the predefined prompt as base
        base_prompt = prompt  # This is from the image_prompts dictionary
        
        # Enhance with AI-extracted objects if available
        if important_objects:
            objects_text = ", ".join(important_objects)
            enhanced_prompt = f"{base_prompt} Additionally featuring: {objects_text}."
        else:
            # Fallback to scene keywords if object extraction fails
            scene_description = extract_scene_keywords(recipient, occasion, message or "", generated_text)
            enhanced_prompt = f"{base_prompt} Enhanced with: {scene_description}."
        
        # Add style-specific instructions
        style_instructions = {
            'friendly': "Use warm, bright colors and friendly imagery.",
            'formal': "Use elegant, sophisticated colors, formal imagery, and a professional picture with photorealistic elements when possible.",
            'funny': "Use playful, cartoon-style imagery with bright colors.",
            'romantic': "Use soft, romantic colors and loving imagery with photorealistic elements when possible."
        }
        
        # Focus on positive instructions since DALL-E doesn't support negative prompts
        quality_instructions = "Create a beautiful, high-quality image with perfect proportions and realistic elements. Focus on objects, nature, landscapes, and symbolic elements. Ensure all visual elements are clear, well-defined, and suitable for a greeting card background."
        
        final_prompt = f"{enhanced_prompt} {style_instructions.get(style, '')} {quality_instructions} Focus on beautiful visual elements only."
        
        print(f"[DALL-E PROMPT] {final_prompt}")
        response = client.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
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
        sender = data.get('sender', '')
        message = data.get('message', '')
        
        # Create a detailed prompt for OpenAI
        prompt = f"""Create a personalized greeting card message for {recipient} for a {occasion} occasion. 

Style: {style}
Sender name: {sender}
{f"Personal message to incorporate: {message}" if message else ""}

Please create a warm, personalized greeting card message that is:
- Appropriate for the {occasion} occasion
- Written in a {style} tone
- Personal and heartfelt
- Include the recipient's name naturally
- If there's a personal message from the sender, incorporate it naturally into the flow
- If inappropriate attributes are in the occasion or the message, remove them (items like violence, hate, nudity, bias, etc.)

Keep the message concise but meaningful (2-3 sentences). Start with 'Dear [recipient name],' and then begin the message content on a new line. 

CRITICAL: You must NOT include ANY closing phrases, signatures, or ending lines. Do NOT write:
- "With love"
- "Warmly" 
- "Best regards"
- "Sincerely"
- "With warmest regards"
- "Cheers"
- "Yours truly"
- Any other closing phrase

End your message with the last sentence of your greeting. The system will add the signature separately."""

        # Call OpenAI API with new format
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
        generated_image_url = generate_dalle_image(occasion, style, recipient, generated_text, message)
        
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
    try:
        stats = load_usage_stats()
        return jsonify(stats)
    except Exception as e:
        print(f"[ERROR] Failed to get stats: {e}")
        return jsonify({'error': 'Failed to load stats'}), 500

@app.route('/api/debug/shared-cards', methods=['GET'])
def debug_shared_cards():
    """Debug endpoint to check shared cards status (development only)"""
    try:
        # Only allow in development
        if os.environ.get('PORT', '5001') != '5001':
            return jsonify({'error': 'Debug endpoint only available in development'}), 403
        
        with open(SHARED_CARDS_FILE, 'r') as f:
            all_cards = json.load(f)
        
        # Count active and expired cards
        current_time = time.time()
        active_cards = {k: v for k, v in all_cards.items() if current_time < v['expires_at']}
        expired_cards = {k: v for k, v in all_cards.items() if current_time >= v['expires_at']}
        
        return jsonify({
            'total_cards': len(all_cards),
            'active_cards': len(active_cards),
            'expired_cards': len(expired_cards),
            'cache_size': len(SHARED_CARDS_CACHE),
            'file_path': os.path.abspath(SHARED_CARDS_FILE)
        })
    except FileNotFoundError:
        return jsonify({'error': 'Shared cards file not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to read shared cards: {e}'}), 500

@app.route('/api/share', methods=['POST'])
def share_card():
    """Create a secure shareable link for a greeting card"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['recipient', 'occasion', 'generated_text', 'image_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Store the card data
        card_data = {
            'recipient': data['recipient'],
            'occasion': data['occasion'],
            'generated_text': data['generated_text'],
            'image_url': data['image_url'],
            'style': data.get('style', 'friendly'),
            'sender': data.get('sender', 'A Friend'),
            'message': data.get('message', ''),
            'created_at': datetime.now().isoformat()
        }
        
        card_id = store_shared_card(card_data)
        
        if not card_id:
            return jsonify({'error': 'Failed to create shareable link - storage error'}), 500
        
        # Generate the shareable URL based on environment
        # Check if we're running locally vs production by looking at the request
        if request.headers.get('Host', '').startswith('localhost') or request.headers.get('Host', '').startswith('127.0.0.1'):
            # Local development
            share_url = f"http://{request.headers.get('Host', 'localhost:5001')}/share/{card_id}"
        else:
            # Production
            share_url = f"https://goodboyagi.com/greeting-card-generator/share/{card_id}"
        
        return jsonify({
            'success': True,
            'share_id': card_id,
            'share_url': share_url,
            'expires_in_hours': 48
        })
        
    except Exception as e:
        print(f"[ERROR] Share card error: {e}")
        return jsonify({'error': 'Failed to create shareable link'}), 500

@app.route('/share/<card_id>')
def view_shared_card(card_id):
    """View a shared greeting card"""
    # Clean up expired cards first
    cleanup_expired_cards()
    
    # Get the card data
    card_data = get_shared_card(card_id)
    
    if not card_data:
        # Card doesn't exist or has expired
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Greeting Card Not Found</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { max-width: 600px; margin: 0 auto; }
                .btn { display: inline-block; padding: 15px 30px; background: white; color: #667eea; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 20px 10px; }
                .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎭 Greeting Card Not Found</h1>
                <p>This greeting card has either expired or doesn't exist.</p>
                <p>Greeting cards expire after 48 hours for security.</p>
                <a href="https://goodboyagi.com/greeting-card-generator/" class="btn">✨ Create Your Own Greeting Card</a>
            </div>
        </body>
        </html>
        ''')
    
    # Render the shared card
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Greeting Card for {{ card.recipient }}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta property="og:title" content="Greeting Card for {{ card.recipient }}">
        <meta property="og:description" content="A personalized greeting card for {{ card.occasion }}">
        <meta property="og:image" content="{{ card.image_url }}">
        <meta property="og:url" content="{{ request.url }}">
        <meta property="og:type" content="website">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="Greeting Card for {{ card.recipient }}">
        <meta name="twitter:description" content="A personalized greeting card for {{ card.occasion }}">
        <meta name="twitter:image" content="{{ card.image_url }}">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white;
                min-height: 100vh;
            }
            .container { 
                max-width: 600px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1); 
                border-radius: 20px; 
                padding: 30px; 
                backdrop-filter: blur(10px);
            }
            .card-image { 
                width: 100%; 
                max-width: 512px; 
                height: auto; 
                border-radius: 15px; 
                margin: 20px 0; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .card-text { 
                background: rgba(255,255,255,0.9); 
                color: #333; 
                padding: 25px; 
                border-radius: 15px; 
                margin: 20px 0; 
                font-size: 18px; 
                line-height: 1.6;
                text-align: justify;
            }

            .btn { 
                display: inline-block; 
                padding: 15px 30px; 
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
                color: white; 
                text-decoration: none; 
                border-radius: 25px; 
                font-weight: bold; 
                margin: 20px 10px; 
                transition: all 0.3s ease;
            }
            .btn:hover { 
                transform: translateY(-2px); 
                box-shadow: 0 5px 15px rgba(0,0,0,0.3); 
            }
            .viral-section { 
                text-align: center; 
                margin: 30px 0; 
                padding: 20px; 
                background: rgba(255,255,255,0.1); 
                border-radius: 15px;
            }
            .branding { 
                text-align: center; 
                margin: 20px 0; 
                font-size: 14px; 
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎭 Greeting Card for {{ card.recipient }}</h1>
            
            <div style="text-align: left; margin: 20px 0; font-size: 18px; opacity: 0.9;">
                <p><strong>From:</strong> {{ card.sender }}</p>
            </div>
            
            <img src="{{ card.image_url }}" alt="Greeting card for {{ card.recipient }}" class="card-image">
            
            <div class="card-text">
                {{ card.generated_text }}
            </div>
            
            <div class="card-text" style="margin-top: 15px; text-align: left; font-style: italic;">
                <p style="margin: 0;">With warmest regards,<br>{{ card.sender }}</p>
            </div>
            
            <div class="viral-section">
                <h3>✨ Love this greeting card?</h3>
                <p>Create your own personalized greeting card for your loved ones!</p>
                <a href="https://goodboyagi.com/greeting-card-generator/" class="btn">🎨 Create Your Own Greeting Card</a>
            </div>
            
            <div class="branding">
                <p>🎭 Made with Good Boy AGI</p>
                <p>Share the joy of personalized greeting cards!</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html_template, card=card_data, request=request)

def load_stats_from_github():
    """Load stats from GitHub file"""
    if not GITHUB_TOKEN:
        return None
    
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_STATS_FILE}"
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            stats_data = base64.b64decode(content['content']).decode('utf-8')
            return json.loads(stats_data)
        elif response.status_code == 404:
            # File doesn't exist, return None to create default stats
            return None
        else:
            print(f"[ERROR] GitHub API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to load from GitHub: {e}")
        return None

def save_stats_to_github(stats):
    """Save stats to GitHub file"""
    if not GITHUB_TOKEN:
        return False
    
    try:
        # First, get the current file to get the SHA
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_STATS_FILE}"
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get current file SHA
        response = requests.get(url, headers=headers)
        sha = None
        if response.status_code == 200:
            sha = response.json()['sha']
        
        # Prepare the update
        stats_json = json.dumps(stats, indent=2)
        content = base64.b64encode(stats_json.encode('utf-8')).decode('utf-8')
        
        data = {
            'message': f'Update usage stats - {stats.get("total_requests", 0)} total requests',
            'content': content
        }
        
        if sha:
            data['sha'] = sha
        
        # Update the file
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            print(f"[INFO] Saved stats to GitHub: {stats.get('total_requests', 0)} total requests")
            return True
        else:
            print(f"[ERROR] Failed to save to GitHub: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to save to GitHub: {e}")
        return False

# Secure sharing functions
def generate_secure_card_id():
    """Generate a secure, unguessable card ID"""
    return secrets.token_urlsafe(16)

def store_shared_card(card_data):
    """Store a card temporarily with 48-hour expiration"""
    card_id = generate_secure_card_id()
    expires_at = time.time() + (48 * 60 * 60)  # 48 hours from now
    
    # Store in file
    try:
        if not os.path.exists(SHARED_CARDS_FILE):
            with open(SHARED_CARDS_FILE, 'w') as f:
                json.dump({}, f, indent=2)
        
        with open(SHARED_CARDS_FILE, 'r') as f:
            all_cards = json.load(f)
        
        all_cards[card_id] = {
            'data': card_data,
            'expires_at': expires_at,
            'created_at': time.time()
        }
        
        with open(SHARED_CARDS_FILE, 'w') as f:
            json.dump(all_cards, f, indent=2)
        
        print(f"[INFO] Stored shared card {card_id} in file, expires at {datetime.fromtimestamp(expires_at)}")
        # Also cache it locally
        SHARED_CARDS_CACHE[card_id] = all_cards[card_id]
        return card_id
    except Exception as e:
        print(f"[ERROR] Failed to store shared card {card_id} in file: {e}")
        return None

def get_shared_card(card_id):
    """Retrieve a shared card if it exists and hasn't expired"""
    # Check cache first
    if card_id in SHARED_CARDS_CACHE:
        card_info = SHARED_CARDS_CACHE[card_id]
        if time.time() < card_info['expires_at']:
            return card_info['data']
        else:
            del SHARED_CARDS_CACHE[card_id]
            print(f"[INFO] Expired shared card {card_id} removed from cache")
            return None

    # If not in cache, load from file
    try:
        with open(SHARED_CARDS_FILE, 'r') as f:
            all_cards = json.load(f)
            
            # Find the card by ID
            if card_id in all_cards:
                card_info = all_cards[card_id]
                # Check if expired
                if time.time() < card_info['expires_at']:
                    SHARED_CARDS_CACHE[card_id] = card_info # Cache it
                    return card_info['data']
                else:
                    # Remove expired card from file
                    del all_cards[card_id]
                    # Save updated file
                    with open(SHARED_CARDS_FILE, 'w') as f_write:
                        json.dump(all_cards, f_write, indent=2)
                    print(f"[INFO] Removed expired shared card {card_id} from file")
                    return None
            return None # Card not found
    except FileNotFoundError:
        print(f"[INFO] Shared cards file not found in file system.")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to load shared card {card_id} from file: {e}")
        return None

def cleanup_expired_cards():
    """Remove expired cards from storage"""
    try:
        with open(SHARED_CARDS_FILE, 'r') as f:
            all_cards = json.load(f)
            
            # Find expired cards
            expired_ids = [
                c_id for c_id, card_info in all_cards.items()
                if time.time() > card_info['expires_at']
            ]
            
            for card_id in expired_ids:
                del all_cards[card_id]
                # Also remove from cache
                if card_id in SHARED_CARDS_CACHE:
                    del SHARED_CARDS_CACHE[card_id]
            
            if expired_ids:
                print(f"[INFO] Cleaned up {len(expired_ids)} expired shared cards from file")
                
                # Save updated file
                with open(SHARED_CARDS_FILE, 'w') as f_write:
                    json.dump(all_cards, f_write, indent=2)
            else:
                print(f"[INFO] No expired shared cards to clean up in file.")
    except FileNotFoundError:
        print(f"[INFO] Shared cards file not found in file system for cleanup.")
    except Exception as e:
        print(f"[ERROR] Failed to cleanup expired shared cards from file: {e}")

def load_shared_cards_cache():
    """Load shared cards from file into cache on startup"""
    try:
        if os.path.exists(SHARED_CARDS_FILE):
            with open(SHARED_CARDS_FILE, 'r') as f:
                all_cards = json.load(f)
                
            # Load non-expired cards into cache
            current_time = time.time()
            for card_id, card_info in all_cards.items():
                if current_time < card_info['expires_at']:
                    SHARED_CARDS_CACHE[card_id] = card_info
            
            print(f"[INFO] Loaded {len(SHARED_CARDS_CACHE)} shared cards into cache from file")
        else:
            print(f"[INFO] No shared cards file found, starting with empty cache")
    except Exception as e:
        print(f"[ERROR] Failed to load shared cards cache from file: {e}")

if __name__ == '__main__':
    # Check if API keys are configured
    if not OPENAI_API_KEY:
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Create a .env file with your API keys for full functionality")
    
    # Load shared cards cache from file
    load_shared_cards_cache()
    
    # Get port from environment variable (for production) or use 5001 for local development
    port = int(os.environ.get('PORT', 5001))
    
    # Use debug=False for production
    app.run(debug=True, host='0.0.0.0', port=port) 