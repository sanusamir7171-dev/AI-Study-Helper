from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
from datetime import datetime
import os

app = Flask(__name__)
client = OpenAI()   # API key ENV se aayegi

# 🧠 Conversation memory (server side)
conversation = []

def ai_answer(question):
    global conversation

    # USER MESSAGE SAVE
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

            img_url = img.data[0].url

            conversation.append({
                "role": "assistant",
                "type": "image",
                "content": img_url
            })
            return

        except Exception as e:
            conversation.append({
                "role": "assistant",
                "type": "text",
                "content": f"Image Error: {e}"
            })
            return

    # 🧠 SYSTEM IDENTITY + DATE (REAL TIME)
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

    # TEXT CONTEXT ONLY
    context = [{"role": "system", "content": system_prompt}]

    for msg in conversation:
        if msg["type"] == "text":
            context.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # 📝 TEXT ANSWER
    try:
        res = client.responses.create(
            model="gpt-4.1-mini",
            input=context
        )

        answer = res.output_text

        conversation.append({
            "role": "assistant",
            "type": "text",
            "content": answer
        })

    except Exception as e:
        conversation.append({
            "role": "assistant",
            "type": "text",
            "content": f"AI Error: {e}"
        })


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        question = request.form["question"]
        ai_answer(question)
        return redirect(url_for("home"))

    return render_template("index.html", messages=conversation)


@app.route("/clear")
def clear_chat():
    global conversation
    conversation = []
    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


