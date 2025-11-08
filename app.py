"""
Simple Flask LLM Application using OpenAI API
"""
import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv


# Read env
load_dotenv(".env", override=True)
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Curl Commands to localhost:5000/ returns this
@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint that sends user message to OpenAI and returns response
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150
        )

        assistant_message = response.choices[0].message.content

        return jsonify({
            'response': assistant_message,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
