from flask import Flask, render_template, request, session, jsonify
from datetime import datetime
import os
import requests

from openai import OpenAI
from anthropic import Anthropic

app = Flask(__name__)

# 🔐 Flask session key (ENV)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

# 🔐 Clients (ENV keys)
openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

claude_client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

HF_API_KEY = os.environ.get("HF_API_KEY")


# ---------------- AI PROVIDERS ---------------- #

def ask_openai(prompt, context):
    try:
        res = openai_client.responses.create(
            model="gpt-4.1-mini",
            input=context + [{"role": "user", "content": prompt}]
        )
        return res.output_text
    except Exception:
        return None


def ask_claude(prompt):
    try:
        msg = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception:
        return None


def ask_huggingface(prompt):
    try:
        url = "https://api-inference.huggingface.co/models/google/flan-t5-base"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": prompt}

        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()[0]["generated_text"]
        return "AI is busy, please try again."
    except Exception:
        return "AI is busy, please try again."


# ---------------- AI LOGIC ---------------- #

def ai_answer(question):
    if "conversation" not in session:
        session["conversation"] = []

    conversation = session["conversation"]

    # 👤 Save user message
    conversation.append({
        "role": "user",
        "type": "text",
        "content": question
    })

    today = datetime.now().strftime("%d %B %Y")

    system_prompt = f"""
You are Sam AI.

IMPORTANT FACTS:
- Created by Samir Singh
- Creation date: 27 December 2025
- Today's real date: {today}

RULES:
- Never say year 2024
- Answer clearly and correctly
"""

    # Build context for OpenAI
    context = [{"role": "system", "content": system_prompt}]
    for msg in conversation:
        if msg["type"] == "text":
            context.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # 🔥 1️⃣ OpenAI
    answer = ask_openai(question, context)

    # 🔁 2️⃣ Claude fallback
    if answer is None:
        answer = ask_claude(system_prompt + "\n\n" + question)

    # 🔁 3️⃣ Hugging Face fallback
    if answer is None:
        answer = ask_huggingface(question)

    conversation.append({
        "role": "assistant",
        "type": "text",
        "content": answer
    })

    session["conversation"] = conversation


# ---------------- ROUTES ---------------- #

@app.route("/", methods=["GET"])
def home():
    return render_template(
        "index.html",
        messages=session.get("conversation", [])
    )


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)
    question = data.get("question") if data else None

    if not question:
        return jsonify({"status": "error"}), 400

    ai_answer(question)
    return jsonify({"status": "ok"})


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"status": "cleared"})


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
