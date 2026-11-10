import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Proxy is running online!"}), 200

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        # System instructions & Chat log formatting
        system_instruction = ""
        contents = []
        
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'system':
                system_instruction += content + "\n"
            elif role == 'user':
                contents.append({"role": "user", "parts": [content]})
            elif role == 'assistant':
                contents.append({"role": "model", "parts": [content]})
                
        # Load Gemini 1.5 Flash (1M Context Support)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction if system_instruction else None
        )
        
        # Generate Response
        response = model.generate_content(contents)
        reply_text = response.text if response.text else ""
        
        # Format response into OpenAI format (Required for Janitor AI)
        openai_formatted_response = {
            "id": "chatcmpl-gemini-proxy",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gemini-1.5-flash",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply_text
                    },
                    "finish_reason": "stop"
                }
            ]
        }
        return jsonify(openai_formatted_response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
      
