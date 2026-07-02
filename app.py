from flask import Flask, render_template, request, jsonify

from utils.rag_engine import ask_question

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    try:

        data = request.get_json()

        question = data.get("question", "")

        result = ask_question(question)

        return jsonify({
            "answer": result["answer"],
            "sources": result["sources"]
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "answer": "⚠️ AI service is temporarily unavailable. Please try again later.",
            "sources": []
        }), 500


if __name__ == "__main__":
    app.run(debug=True)