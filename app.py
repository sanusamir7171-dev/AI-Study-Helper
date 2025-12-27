from flask import Flask, render_template, request
from openai import OpenAI
import os

app = Flask(__name__)

# ✅ API key environment se aayegi
client = OpenAI()   # yahan key nahi likhte

def ai_answer(question):
    q = question.lower().strip()

    # Rule-based answers
    if "matrix" in q:
        return "Matrix multiplication explanation..."

    # 🔥 Real AI fallback
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"Explain simply with examples:\n{question}"
        )
        return response.output_text

    except Exception as e:
        return f"AI Error: {e}"

@app.route("/", methods=["GET", "POST"])
def home():
    answer = ""
    if request.method == "POST":
        question = request.form["question"]
        answer = ai_answer(question)
    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
