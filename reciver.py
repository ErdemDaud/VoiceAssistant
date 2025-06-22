from flask import Flask, request, jsonify
import ollama
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# System prompt
INITIAL_PROMPT = {
    'role': 'system',
    'content': (
        "Do not use Turkish language."
        "Think like you are in conversation and the user is speaking to you."
        "Do not use special characters like '/,%,+,$,*' etc."
        "Your answer should be as concise as possible. Long lines can be boring in a conversation, but if users want long content, provide it."
        "Use examples when needed. Respond like a smart, friendly person."
        "Always use Turkish measurement units like Celsius, meters, centimeters, calories, etc."
    )
}

conversation_history = [INITIAL_PROMPT]
MODEL_NAME = "llama3.1"  # Your Ollama model name

@app.route('/receive', methods=['POST'])
def receive():
    global conversation_history

    # ✅ Accepting form data instead of JSON
    user_text = request.form.get('message', '').strip()
    print(f"📥 User: {user_text}")

    if not user_text:
        return jsonify({'response': "No input received."})

    conversation_history.append({'role': 'user', 'content': user_text})

    if len(conversation_history) > 51:
        conversation_history = [INITIAL_PROMPT] + conversation_history[-20:]

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=conversation_history
        )
        response_text = response['message']['content'].strip()
        print(f"🦙 LLaMA says: {response_text}")

        conversation_history.append({'role': 'assistant', 'content': response_text})
        return jsonify({'response': response_text})

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'response': "LLaMA failed to respond."})

@app.route('/reset', methods=['POST'])
def reset_memory():
    global conversation_history
    conversation_history = [INITIAL_PROMPT]
    print("🧠 Memory reset!")
    return jsonify({'status': 'Memory cleared.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
