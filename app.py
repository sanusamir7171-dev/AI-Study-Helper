from flask import Flask, render_template, request, redirect, url_for, session
from openai import OpenAI
from datetime import datetime
import os

app = Flask(__name__)

# 🔐 IMPORTANT:
# Flask secret key .env / Environment variable se aayegi
# GitHub me kabhi hardcode mat karna
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# 🔐 IMPORTANT:
# OpenAI API key bhi ENV se hi aayegi
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


def ai_answer(question):
    # 🧠 SESSION BASED conversation (har user ke liye alag)
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

    # 🧠 SYSTEM PROMPT (identity + real date)
    today = datetime.now().strftime("%d %B %Y")

    system_prompt = f"""
You are Sam AI.

IMPORTANT FACTS:
- You were created by Samir Singh.
- you creator wife name is Priyanshu Singh.
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


@app.route("/", methods=["GET", "POST"])
def home():
    if "conversation" not in session:
        session["conversation"] = []

    if request.method == "POST":
        ai_answer(request.form["question"])
        return redirect(url_for("home"))

    return render_template(
        "index.html",
        messages=session["conversation"]
    )


@app.route("/clear")
def clear_chat():
    session.pop("conversation", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


