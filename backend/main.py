from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import requests
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/github/{username}")
def get_github_user(username: str):
    response = requests.get(f"https://api.github.com/users/{username}")
    if response.status_code == 404:
        return {"error": "GitHub user not found"}
    return response.json()

def get_ai_analysis(user_data):
    profile_summary = f"""
    GitHub Profile:
    Username: {user_data.get('login')}
    Name: {user_data.get('name')}
    Bio: {user_data.get('bio')}
    Public Repos: {user_data.get('public_repos')}
    Followers: {user_data.get('followers')}
    Following: {user_data.get('following')}
    """

    prompt = f"""
    Analyze this GitHub profile and provide a fun, creative assessment in JSON format.
    Profile: {profile_summary}

    Return ONLY a JSON object with these keys:
    - developer_persona
    - coding_style
    - strongest_skill
    - weak_area
    - funny_roast
    - suggested_role
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

@app.get("/analyze/{username}")
def analyze_user(username: str):
    github_response = requests.get(f"https://api.github.com/users/{username}")
    if github_response.status_code == 404:
        return {"error": "GitHub user not found"}

    user_data = github_response.json()
    analysis = get_ai_analysis(user_data)
    return analysis

@app.get("/card/{username}", response_class=HTMLResponse)
def get_persona_card(username: str):
    # 1. Fetch Data
    github_response = requests.get(f"https://api.github.com/users/{username}")
    if github_response.status_code == 404:
        return "<h1>GitHub user not found</h1>"

    user_data = github_response.json()
    analysis = get_ai_analysis(user_data)

    if "error" in analysis:
        return f"<h1>AI Analysis Error: {analysis['error']}</h1>"

    # 2. Build HTML Card
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{username}'s Dev Persona</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #0d1117;
                --card-bg: rgba(22, 27, 34, 0.8);
                --accent: #58a6ff;
                --text: #c9d1d9;
                --gold: #f2cc60;
            }}
            body {{
                background: var(--bg);
                color: var(--text);
                font-family: 'Inter', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                overflow: hidden;
            }}
            .card {{
                background: var(--card-bg);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 40px;
                width: 400px;
                text-align: center;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                position: relative;
            }}
            .card:hover {{
                transform: scale(1.02) translateY(-10px);
                border-color: var(--accent);
            }}
            .avatar {{
                width: 120px;
                height: 120px;
                border-radius: 50%;
                border: 4px solid var(--accent);
                margin-bottom: 20px;
                box-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
            }}
            h1 {{
                margin: 0;
                font-size: 28px;
                background: linear-gradient(90deg, #fff, var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .username {{
                color: var(--accent);
                font-weight: 300;
                margin-bottom: 20px;
                display: block;
            }}
            .persona-tag {{
                background: rgba(88, 166, 255, 0.1);
                color: var(--accent);
                padding: 6px 16px;
                border-radius: 50px;
                font-size: 14px;
                font-weight: 600;
                display: inline-block;
                margin-bottom: 24px;
                border: 1px solid rgba(88, 166, 255, 0.2);
            }}
            .stats {{
                display: flex;
                justify-content: space-around;
                margin-bottom: 24px;
                border-top: 1px solid rgba(255, 255, 255, 0.05);
                padding-top: 20px;
            }}
            .stat-item span {{
                display: block;
                font-size: 20px;
                font-weight: 800;
                color: #fff;
            }}
            .stat-item label {{
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                opacity: 0.6;
            }}
            .info-grid {{
                text-align: left;
                display: grid;
                gap: 16px;
                font-size: 14px;
            }}
            .info-row b {{
                color: var(--accent);
                display: block;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 4px;
            }}
            .roast {{
                margin-top: 24px;
                padding: 16px;
                background: rgba(242, 204, 96, 0.05);
                border-radius: 12px;
                border-left: 4px solid var(--gold);
                font-style: italic;
                font-size: 13px;
                color: var(--gold);
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <img src="{user_data.get('avatar_url')}" class="avatar" alt="Avatar">
            <h1>{user_data.get('name') or username}</h1>
            <span class="username">@{username}</span>
            <div class="persona-tag">{analysis.get('developer_persona')}</div>

            <div class="stats">
                <div class="stat-item">
                    <span>{user_data.get('public_repos')}</span>
                    <label>Repos</label>
                </div>
                <div class="stat-item">
                    <span>{user_data.get('followers')}</span>
                    <label>Followers</label>
                </div>
            </div>

            <div class="info-grid">
                <div class="info-row">
                    <b>Coding Style</b>
                    {analysis.get('coding_style')}
                </div>
                <div class="info-row">
                    <b>Strongest Skill</b>
                    {analysis.get('strongest_skill')}
                </div>
                <div class="info-row">
                    <b>Suggested Role</b>
                    {analysis.get('suggested_role')}
                </div>
            </div>

            <div class="roast">
                "{analysis.get('funny_roast')}"
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
