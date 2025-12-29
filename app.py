from flask import Flask, render_template, request, session, jsonify
from openai import OpenAI
from datetime import datetime
import os

app = Flask(__name__)

# 🔐 Secret key (ENV se)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# 🔐 OpenAI client (API key ENV se)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


# 🧠 AI LOGIC
def ai_answer(question):

    # SESSION BASED conversation (per user)
    if "conversation" not in session:
        session["conversation"] = []

    conversation = session["conversation"]

    # 👤 USER MESSAGE SAVE
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

    # 🧠 SYSTEM PROMPT + REAL DATE
    today = datetime.now().strftime("%d %B %Y")

    system_prompt = f"""
You are Sam AI.

IMPORTANT FACTS:
- You were created by Samir Singh.
- Your creation date is 27 December 2025.
- Today's real date is {today}.

RULES:
- Never say the year is 2024.
- Always answer with the correct current date.
- Remember the ongoing conversation context.
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


# 🏠 HOME PAGE (ONLY GET)
@app.route("/", methods=["GET"])
def home():
    return render_template(
        "index.html",
        messages=session.get("conversation", [])
    )


# 💬 ASK API (AJAX)
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question")

    if question:
        ai_answer(question)

    return jsonify({"status": "ok"})


# 🧹 CLEAR CHAT
@app.route("/clear")
def clear_chat():
    session.clear()
    return redirect(url_for("home"))



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


