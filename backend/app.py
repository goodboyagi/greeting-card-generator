from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Get API keys from environment variables (secure)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')

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
    """Generate greeting card text using AI"""
    if not OPENAI_API_KEY:
        return jsonify({'error': 'OpenAI API key not configured'}), 500
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        style = data.get('style', 'friendly')
        
        # Here you would integrate with OpenAI API
        # For now, return a mock response
        generated_text = f"Generated greeting for: {message} in {style} style"
        
        return jsonify({
            'success': True,
            'generated_text': generated_text
        })
    
    except Exception as e:
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

if __name__ == '__main__':
    # Check if API keys are configured
    if not OPENAI_API_KEY:
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Create a .env file with your API keys for full functionality")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 