from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, template_folder="../frontend/templates")
CORS(app)  

@app.route('/')
def home():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are iReport, a helpful cybercrime assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response['choices'][0]['message']['content'].strip()
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Error: {e}")  
        return jsonify({"reply": "Sorry, I couldn’t process your request right now."}), 500

if __name__ == '__main__':
    app.run(debug=True)
