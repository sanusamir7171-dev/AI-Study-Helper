from flask import Flask, render_template, request, session, jsonify
from openai import OpenAI
from datetime import datetime
import os

app = Flask(__name__)

# 🔐 Secret key (ENV)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

# 🔐 OpenAI client (ENV)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# 🧠 AI LOGIC
def ai_answer(question):
    if "conversation" not in session:
        session["conversation"] = []

    conversation = session["conversation"]

    # USER MESSAGE
    conversation.append({
        "role": "user",
        "type": "text",
        "content": question
    })

    q = question.lower()
    image_words = ["draw", "image", "photo", "diagram", "picture", "generate"]

    # 🖼️ IMAGE GENERATION
    if any(word in q for word in image_words):
        try:
            img = client.images.generate(
                model="gpt-image-1",
                prompt=question,
                size="1024x1024"
            )

            conversation.append({
                "role": "assistant",
                "type": "image",
                "content": img.data[0].url
            })

            session["conversation"] = conversation
            return

        except Exception as e:
            conversation.append({
                "role": "assistant",
                "type": "text",
                "content": f"Image Error: {e}"
            })
            session["conversation"] = conversation
            return

    # 🧠 SYSTEM PROMPT
    today = datetime.now().strftime("%d %B %Y")

    system_prompt = f"""
You are Sam AI.
Created by Samir Singh.
Creation date: 27 December 2025.
Today's date: {today}.
"""

    context = [{"role": "system", "content": system_prompt}]

    for msg in conversation:
        if msg["type"] == "text":
            context.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # 📝 TEXT RESPONSE
    try:
        res = client.responses.create(
            model="gpt-4.1-mini",
            input=context
        )

        conversation.append({
            "role": "assistant",
            "type": "text",
            "content": res.output_text
        })

    except Exception as e:
        conversation.append({
            "role": "assistant",
            "type": "text",
            "content": f"AI Error: {e}"
        })

    session["conversation"] = conversation


# 🏠 HOME (NO POST HERE)
@app.route("/", methods=["GET"])
def home():
    return render_template(
        "index.html",
        messages=session.get("conversation", [])
    )


# 💬 ASK (AJAX ONLY)
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)
    question = data.get("question") if data else None

    if question:
        ai_answer(question)
        return jsonify({"status": "ok"})

    return jsonify({"status": "error"}), 400


# 🧹 CLEAR CHAT (AJAX SAFE)
@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
