from flask import Flask, render_template, request
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI()   # API key env se aayegi

def ai_answer(question):
    q = question.lower()

    # 🖼️ IMAGE REQUEST CHECK
    image_keywords = ["draw", "image", "photo", "diagram", "picture", "generate image"]

    if any(word in q for word in image_keywords):
        try:
            img = client.images.generate(
                model="gpt-image-1",
                prompt=question,
                size="512x512"
            )
            return {"type": "image", "data": img.data[0].url}
        except Exception as e:
            return {"type": "text", "data": str(e)}

    # 🔤 NORMAL TEXT AI
    try:
        res = client.responses.create(
            model="gpt-4.1-mini",
            input=question
        )
        return {"type": "text", "data": res.output_text}
    except Exception as e:
        return {"type": "text", "data": str(e)}

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        question = request.form["question"]
        result = ai_answer(question)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
