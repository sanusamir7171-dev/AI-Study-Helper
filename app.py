from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
from datetime import datetime
import os

app = Flask(__name__)
client = OpenAI()   # API key env se aayegi

# 🧠 CONVERSATION MEMORY (server-level)
conversation = []

def ai_answer(question):
    global conversation
    q = question.lower()

    image_words = ["draw", "image", "photo", "diagram", "picture", "generate"]

    # 🧍 USER MESSAGE SAVE
    conversation.append({
        "role": "user",
        "type": "text",
        "content": question
    })

    # 🖼️ IMAGE GENERATION
    if any(w in q for w in image_words):
        try:
            img = client.images.generate(
                model="gpt-image-1",
                prompt=question,
                size="512x512"
            )

            img_url = img.data[0].url

            # 🤖 AI IMAGE RESPONSE SAVE
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

    # 📝 TEXT ANSWER (WITH MEMORY)
    try:
        # Only text messages AI ko bhejte hain
        context = [
            {"role": m["role"], "content": m["content"]}
            for m in conversation if m["type"] == "text"
        ]

today = datetime.now().strftime("%d %B %Y")

system_identity = f"""
You are an AI assistant named Sam AI.

IMPORTANT FACTS (never forget):
- You were created by Samir Singh.
- Your creation date is 27 December 2025.
- Today’s real date is {today}.

RULES:
- If asked "who created you", answer: "I was created by Samir Singh."
- If asked "when were you created", answer: "I was created on 27 December 2025."
- If asked today's date, always answer according to {today}.
- Never assume the year is 2024.
- Always use the current year.
"""

res = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "system",
            "content": system_identity
        }
    ] + context
)

        answer = res.output_text

        # 🤖 AI TEXT RESPONSE SAVE
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

    return render_template(
        "index.html",
        messages=conversation
    )

@app.route("/clear")
def clear_chat():
    global conversation
    conversation = []
    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

