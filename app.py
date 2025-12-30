from flask import Flask, render_template, request, session, jsonify
from datetime import datetime
import google.generativeai as genai
import os

app = Flask(__name__)

# 🔐 Flask secret
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

# 🔐 Gemini API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 🔹 Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")


# 🧠 AI LOGIC
def ai_answer(question):
    if "conversation" not in session:
        session["conversation"] = []

    conversation = session["conversation"]

    # USER MESSAGE SAVE
    conversation.append({
        "role": "user",
        "type": "text",
        "content": question
    })

    # 🧠 SYSTEM PROMPT
    today = datetime.now().strftime("%d %B %Y")

    system_prompt = f"""
You are Sam AI.
Created by Samir Singh.
Creation date: 27 December 2025.
Today's date: {today}.

Rules:
- Be helpful
- Answer clearly
"""

    # 🧩 Build full prompt from conversation
    full_prompt = system_prompt + "\n\n"

    for msg in conversation:
        if msg["type"] == "text":
            role = "User" if msg["role"] == "user" else "Assistant"
            full_prompt += f"{role}: {msg['content']}\n"

    # 📝 Gemini response
    try:
        response = model.generate_content(full_prompt)

        conversation.append({
            "role": "assistant",
            "type": "text",
            "content": response.text
        })

    except Exception as e:
        conversation.append({
            "role": "assistant",
            "type": "text",
            "content": f"AI Error: {e}"
        })

    session["conversation"] = conversation


# 🏠 HOME
@app.route("/", methods=["GET"])
def home():
    return render_template(
        "index.html",
        messages=session.get("conversation", [])
    )


# 💬 ASK (AJAX)
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)
    question = data.get("question") if data else None

    if question:
        ai_answer(question)
        return jsonify({"status": "ok"})

    return jsonify({"status": "error"}), 400


# 🧹 CLEAR CHAT
@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
