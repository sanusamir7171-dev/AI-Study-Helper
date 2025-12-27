from flask import Flask, render_template, request, jsonify
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
                size="512x512"
            )

            img_url = img.data[0].url

            conversation.append({
                "role": "assistant",
                "content": img_url,
                "is_image": True
            })

            return {
                "type": "image",
                "content": img_url
            }

        except Exception as e:
            return {
                "type": "text",
                "content": f"Image Error: {e}"
            }

    # 🧠 SYSTEM IDENTITY + REAL DATE
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
- Remember the ongoing conversation.
"""

    context = [{"role": "system", "content": system_prompt}]
    context.extend(conversation)

    # 📝 TEXT ANSWER
    try:
        res = client.responses.create(
            model="gpt-4.1-mini",
            input=context
        )

        answer = res.output_text

        conversation.append({
            "role": "assistant",
            "content": answer
        })

        return {
            "type": "text",
            "content": answer
        }

    except Exception as e:
        return {
            "type": "text",
            "content": f"AI Error: {e}"
        }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    result = ai_answer(data["question"])
    return jsonify(result)


@app.route("/clear")
def clear_chat():
    global conversation
    conversation = []
    return ("", 204)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
