import os
import time
from flask import Flask, request, render_template_string
from google import genai

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-3.8-flash"

def gift_detective(user_input):
    prompt = f"""
You are Gift Detective, a specialized AI gift recommendation agent.

User information:
{user_input}

Analyze it and provide:
1. RECIPIENT PROFILE — interests, personality, relationship, occasion, budget, likes, dislikes.
2. GIFT DETECTIVE — identify what type of gift suits them and explain why.
3. TOP 5 GIFT IDEAS — gift name, why it matches, approximate price/budget category, personalization idea.
4. SPECIAL TOUCH — one creative way to make the gift memorable.
5. MISSING INFORMATION — ask useful questions if important details are missing.

Rules:
- Avoid generic recommendations when enough information is available.
- Respect the budget, relationship and occasion.
- Do not repeatedly suggest the same type of gift.
- Keep recommendations realistic and practical.
- Do not claim a particular product is definitely available.
"""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < 2:
                    time.sleep(5)
                    continue
                return "⚠️ Gemini is temporarily experiencing high demand.\n\nPlease wait a little and try again."
            raise

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Gift Detective</title>
<style>
body {font-family:Arial,sans-serif;background:#fff5f8;margin:0;padding:40px;}
.container {max-width:800px;margin:auto;background:white;padding:30px;border-radius:15px;}
h1 {text-align:center;color:#d14d72;}
textarea {width:100%;height:170px;padding:15px;box-sizing:border-box;border-radius:10px;border:1px solid #ccc;font-size:16px;}
button {display:block;margin:20px auto;padding:12px 25px;border:none;border-radius:8px;background:#d14d72;color:white;font-size:16px;cursor:pointer;}
.result {margin-top:25px;padding:20px;background:#fff8fa;border-radius:10px;white-space:pre-wrap;line-height:1.6;}
</style>
</head>
<body>
<div class="container">
<h1>🎁 Gift Detective</h1>
<p>Tell us about the person and the occasion. Our AI Gift Detective will find personalized gift ideas.</p>
<form method="POST">
<textarea name="person" placeholder="Example: My best friend is 20, loves painting and photography, and my budget is ₹1500." required></textarea>
<button type="submit">🔎 Find Gift Ideas</button>
</form>
{% if result %}<div class="result">{{ result }}</div>{% endif %}
{% if error %}<div class="result">{{ error }}</div>{% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    error = ""
    if request.method == "POST":
        user_input = request.form.get("person")
        try:
            result = gift_detective(user_input)
        except Exception as e:
            error = f"Something went wrong: {e}"
    return render_template_string(HTML, result=result, error=error)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
