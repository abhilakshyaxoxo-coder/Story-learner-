import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Hardcoded for a throwaway 24-hour key. Swap back to os.environ.get("GROQ_API_KEY")
# and set it externally if you ever reuse this with a real, longer-lived key.
GROQ_API_KEY = "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"
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not set. Set it as an environment variable before running."
    )

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)  # harmless to keep even when frontend + backend share an origin

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.4,
    max_tokens=250,
)

prompt = ChatPromptTemplate.from_template(
    """You are a master film storyteller
Topic: {top}
Genre: {flow}

Task: Convert the given topic into a complete, engaging film story.
Structure it like this:
1. Title - Give a catchy film title
2. Logline - 1 line summary
3. Act 1: Setup - Introduce hero and world
4. Act 2: Conflict - Main problem and struggles
5. Act 3: Resolution - Climax and ending with a twist/message

Make it cinematic, emotional and keep it strictly in {flow} genre. Keep it under 300 words."""
)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True) or {}
    top = (data.get("topic") or "").strip()
    flow = (data.get("genre") or "").strip()

    if not top or not flow:
        return jsonify({"error": "Both 'topic' and 'genre' are required."}), 400

    try:
        f_prompt = prompt.format_messages(top=top, flow=flow)
        response = llm.invoke(f_prompt)
        return jsonify({"story": response.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT for you
    app.run(host="0.0.0.0", port=port)
    
