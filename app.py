from flask import Flask, render_template, request
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI()   # API key env se aayegi

def ai_answer(question):
    q = question.lower()

    image_words = ["draw", "image", "photo", "diagram", "picture"]

    # 🖼️ IMAGE GENERATION
    if any(w in q for w in image_words):
        try:
            img = client.images.generate(
                model="gpt-image-1",
                prompt=question,
                size="512x512"
            )
            return {
                "is_image": True,
                "content": img.data[0].url
            }
        except Exception as e:
            return {
                "is_image": False,
                "content": str(e)
            }

    # 📝 TEXT ANSWER
    try:
        res = client.responses.create(
            model="gpt-4.1-mini",
            input=question
        )
        return {
            "is_image": False,
            "content": res.output_text
        }
    except Exception as e:
        return {
            "is_image": False,
            "content": str(e)
        }

@app.route("/", methods=["GET", "POST"])
def home():
    answer = None
    is_image = False

    if request.method == "POST":
        question = request.form["question"]
        result = ai_answer(question)
        answer = result["content"]
        is_image = result["is_image"]

    return render_template(
        "index.html",
        answer=answer,
        is_image=is_image
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
