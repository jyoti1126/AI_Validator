from __future__ import annotations

import json
import os
import re
import traceback
import database
from pathlib import Path

from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure Gemini
_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=_GEMINI_KEY) if _GEMINI_KEY else None
_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# ---------------------------------------------------------------------------

# Structured JSON Schema for Gemini
# ---------------------------------------------------------------------------

class OverviewData(BaseModel):
    summary: str
    problem: str
    target_customers: str
    value_proposition: str

class MarketData(BaseModel):
    market_overview: str
    target_market: str
    customer_demand: str
    market_opportunity: str
    assumptions: list[str]

class CompetitionItem(BaseModel):
    name: str
    description: str
    similarity: str
    differentiation_opportunity: str

class RiskItem(BaseModel):
    title: str
    description: str
    mitigation: str

class BusinessData(BaseModel):
    business_model: str
    revenue_streams: list[str]
    customer_acquisition: str
    resources_needed: list[str]
    business_assumptions: list[str]

class MVPData(BaseModel):
    description: str
    features: list[str]
    avoid_initially: list[str]
    first_users: str
    launch_approach: str

class ValidationOverview(BaseModel):
    score: int
    evidence_level: str
    summary: str

class QuickInsight(BaseModel):
    category: str
    insight_text: str

class ValidationExperimentStep(BaseModel):
    id: str
    title: str
    description: str

class DashboardAnalysis(BaseModel):
    startup_name: str
    industry: str = ""
    validation_overview: ValidationOverview
    quick_insights: list[QuickInsight]
    overview: OverviewData
    market: MarketData
    competition: list[CompetitionItem]
    risks: list[RiskItem]
    business: BusinessData
    mvp: MVPData
    validation_experiment: list[ValidationExperimentStep]


# ---------------------------------------------------------------------------
# Static file routes
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return send_file(BASE_DIR / "index.html")


@app.route("/<path:filename>", methods=["GET", "HEAD"])
def serve_file(filename: str):
    file_path = BASE_DIR / filename
    if file_path.is_file():
        return send_file(file_path)
    return "Not Found", 404



import database

# ---------------------------------------------------------------------------
# SQLite APIs - Startups
# ---------------------------------------------------------------------------

@app.post("/api/startups")
def create_startup():
    data = request.get_json(silent=True) or {}
    idea = data.get("idea")
    if not isinstance(idea, str) or not idea.strip():
        return jsonify({"success": False, "message": "Startup idea is required."}), 400

    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO startups (name, idea, problem, target_customers, business_model, budget, time_available, skills)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("name", "New Startup Idea"),
        idea.strip(),
        data.get("problem", ""),
        data.get("targetCustomers", ""),
        data.get("businessModel", ""),
        data.get("budget", ""),
        data.get("timeAvailable", ""),
        json.dumps(data.get("skills", []))
    ))
    startup_id = cursor.lastrowid
    
    cursor.execute('SELECT * FROM startups WHERE id = ?', (startup_id,))
    startup = dict(cursor.fetchone())
    if startup.get("skills"):
        startup["skills"] = json.loads(startup["skills"])
        
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "startup": startup}), 201

@app.get("/api/startups")
def get_startups():
    conn = database.get_db_connection()
    startups = conn.execute('SELECT id, name, category, validation_score as validation, progress, idea FROM startups ORDER BY created_at DESC').fetchall()
    conn.close()
    
    result = []
    for s in startups:
        s_dict = dict(s)
        # To maintain compatibility with frontend `startups.js` expectations
        result.append(s_dict)
        
    return jsonify({"success": True, "startups": result}), 200

@app.get("/api/startups/<int:startup_id>")
def get_startup(startup_id):
    conn = database.get_db_connection()
    startup = conn.execute('SELECT * FROM startups WHERE id = ?', (startup_id,)).fetchone()
    conn.close()
    
    if not startup:
        return jsonify({"success": False, "message": "Startup not found."}), 404
        
    s_dict = dict(startup)
    if s_dict.get("skills"):
        s_dict["skills"] = json.loads(s_dict["skills"])
        
    # Map db fields to frontend expected fields
    s_dict["targetCustomers"] = s_dict.pop("target_customers", "")
    s_dict["businessModel"] = s_dict.pop("business_model", "")
    s_dict["timeAvailable"] = s_dict.pop("time_available", "")
    
    return jsonify({"success": True, "startup": s_dict}), 200

@app.put("/api/startups/<int:startup_id>")
def update_startup(startup_id):
    data = request.get_json(silent=True) or {}
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # We only update fields provided
    fields = []
    values = []
    
    mapping = {
        "name": "name",
        "idea": "idea",
        "problem": "problem",
        "targetCustomers": "target_customers",
        "businessModel": "business_model",
        "budget": "budget",
        "timeAvailable": "time_available",
        "skills": "skills",
        "validation": "validation_score",
        "progress": "progress",
        "category": "category"
    }
    
    for req_key, db_key in mapping.items():
        if req_key in data:
            fields.append(f"{db_key} = ?")
            if req_key == "skills":
                values.append(json.dumps(data[req_key]))
            else:
                values.append(data[req_key])
                
    if not fields:
        conn.close()
        return jsonify({"success": True, "message": "No fields to update."}), 200
        
    values.append(startup_id)
    
    cursor.execute(f'''
        UPDATE startups SET {", ".join(fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', values)
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Startup updated successfully."}), 200

@app.delete("/api/startups/<int:startup_id>")
def delete_startup(startup_id):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM startups WHERE id = ?', (startup_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Startup deleted successfully."}), 200

# ---------------------------------------------------------------------------
# SQLite APIs - Analysis
# ---------------------------------------------------------------------------

@app.get("/api/startups/<int:startup_id>/analysis")
def get_analysis(startup_id):
    conn = database.get_db_connection()
    analysis = conn.execute('SELECT * FROM analyses WHERE startup_id = ?', (startup_id,)).fetchone()
    conn.close()
    
    if not analysis:
        return jsonify({"success": False, "message": "Analysis not found."}), 404
        
    try:
        data = {
            "startup_name": analysis["startup_name"],
            "industry": analysis["industry"] or "",
            "validation_overview": json.loads(analysis["validation_overview"] or "{}"),
            "overview": json.loads(analysis["overview"] or "{}"),
            "market": json.loads(analysis["market_analysis"] or "{}"),
            "competition": json.loads(analysis["competition"]),
            "risks": json.loads(analysis["risks"]),
            "business": json.loads(analysis["business"]),
            "mvp": json.loads(analysis["mvp"]),
            "quick_insights": json.loads(analysis["quick_insights"]),
            "validation_experiment": json.loads(analysis["validation_experiment"])
        }
        return jsonify({"success": True, "analysis": data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error parsing analysis: {e}"}), 500

# ---------------------------------------------------------------------------
# SQLite APIs - Tasks
# ---------------------------------------------------------------------------

@app.get("/api/startups/<int:startup_id>/tasks")
def get_tasks(startup_id):
    print(f"[Validation] Loading tasks for startup ID: {startup_id}")
    conn = database.get_db_connection()
    tasks = conn.execute('SELECT id, task_name as title, description, completed FROM mvp_tasks WHERE startup_id = ?', (startup_id,)).fetchall()
    conn.close()
    
    result = [dict(t) for t in tasks]
    # For frontend compatibility, completed should be boolean
    for t in result:
        t["completed"] = bool(t["completed"])
        
    print(f"[Validation] Tasks received: {len(result)}")
    return jsonify({"success": True, "tasks": result}), 200

@app.put("/api/tasks/<task_id>")
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    completed = 1 if data.get("completed") else 0
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Update task
    cursor.execute('UPDATE mvp_tasks SET completed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (completed, task_id))
    
    # Recalculate progress for the startup
    startup_id_row = cursor.execute('SELECT startup_id FROM mvp_tasks WHERE id = ?', (task_id,)).fetchone()
    if startup_id_row:
        startup_id = startup_id_row["startup_id"]
        total = cursor.execute('SELECT COUNT(*) FROM mvp_tasks WHERE startup_id = ?', (startup_id,)).fetchone()[0]
        completed_count = cursor.execute('SELECT COUNT(*) FROM mvp_tasks WHERE startup_id = ? AND completed = 1', (startup_id,)).fetchone()[0]
        
        progress = int((completed_count / total) * 100) if total > 0 else 0
        
        cursor.execute('UPDATE startups SET progress = ? WHERE id = ?', (progress, startup_id))
    else:
        progress = 0
        
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "progress": progress}), 200


# ---------------------------------------------------------------------------
# Gemini AI Dashboard Generation
# ---------------------------------------------------------------------------

DASHBOARD_PROMPT_TEMPLATE = """You are an AI startup analyst helping a beginner founder understand their startup.

Gemini must analyze ONLY the startup submitted by the current user.
The analysis must be specific to:
- startup idea
- problem
- customers
- business model
- budget
- founder skills
- validation information

Do not generate generic startup advice.
Use simple English, short sentences, bullet points, and practical suggestions.
Avoid unnecessarily complicated business terminology, huge paragraphs, and generic AI-sounding explanations.
If information is uncertain or cannot be verified, clearly identify it as an assumption or estimate instead of presenting it as a confirmed fact.

Startup information:

Startup Idea:
{idea}

Problem:
{problem}

Target Customers:
{targetCustomers}

Business Model:
{businessModel}

Budget:
{budget}

Time Available:
{timeAvailable}

Founder Skills:
{skills}

Validation Result:
{validationStatus}

Generate the following:

SHORT NAME (startup_name)
A short, readable startup/business name (1-3 words).

INDUSTRY (industry)
A 1-2 word category for the startup (e.g. "EdTech", "Health", "E-commerce"). If you cannot determine, leave empty. Never use "Food & Beverage" as a default category. Only use it if the startup is explicitly related to food.

VALIDATION OVERVIEW (validation_overview)
Provide a high-level summary of the startup:
- score: An integer from 0 to 100 indicating validation strength.
- evidence_level: "Strong Evidence", "Moderate Evidence", etc.
- summary: A 2-3 sentence summary covering potential, problem, market opportunity, competition, business model, and key risk.

QUICK INSIGHTS (quick_insights)
Provide 4-6 short, useful insights specific to this startup.
Each insight should have:
- category: (e.g. "Market", "Customer", "Competition", "Business", "Risk", "MVP")
- insight_text: A very short, punchy takeaway (e.g. "Huge teen demand", "High setup costs", "Fierce local competition").

1. OVERVIEW SECTION (overview)
Analyze:
- What the startup does (summary)
- What problem it solves (problem)
- Who it is for (target_customers)
- Why the idea could be useful (value_proposition)

2. MARKET ANALYSIS SECTION (market)
Analyze:
- Market overview (market_overview)
- Target market (target_market)
- Customer demand (customer_demand)
- Market opportunity (market_opportunity)
- Important assumptions (assumptions)

3. COMPETITION SECTION (competition)
For each competitor/alternative provide:
- Name (name)
- What they offer (description)
- How they are similar (similarity)
- Possible differentiation opportunity (differentiation_opportunity)

4. RISKS SECTION (risks)
For each risk provide:
- Title (title)
- Simple explanation (description)
- Possible mitigation (mitigation)

5. BUSINESS SECTION (business)
Analyze:
- Business model (business_model)
- Possible revenue streams (revenue_streams)
- Customer acquisition approach (customer_acquisition)
- Main resources required (resources_needed)
- Important business assumptions (business_assumptions)

6. MVP SECTION (mvp)
Generate an MVP specifically for THIS startup. Include:
- MVP description (description)
- 5-8 essential features (features)
- What should NOT be built initially (avoid_initially)
- Suggested first users (first_users)
- Basic launch approach (launch_approach)

7. VALIDATION EXPERIMENT (validation_experiment)
Provide 6-8 practical, realistic, and short validation steps for the founder to test this specific startup idea in the real world.
Each step should include:
- id: A unique step identifier (e.g. "step-1", "step-2")
- title: Short title (e.g. "Talk to potential customers")
- description: Short, simple explanation of what to do (e.g. "Interview 10-15 students who regularly buy used textbooks.")
"""

def _build_dashboard_prompt(data: dict) -> str:
    skills_str = ", ".join(data.get("skills") or []) or "Not specified"
    validation = data.get("validationResult") or data.get("validationStatus") or "Validated"
    return DASHBOARD_PROMPT_TEMPLATE.format(
        idea=data.get("idea") or "Not provided",
        problem=data.get("problem") or "Not provided",
        targetCustomers=data.get("targetCustomers") or "Not provided",
        businessModel=data.get("businessModel") or "Not provided",
        budget=data.get("budget") or "Not provided",
        timeAvailable=data.get("timeAvailable") or "Not provided",
        skills=skills_str,
        validationStatus=validation,
    )

def _handle_gemini_error(exc: Exception, context: str) -> tuple[dict, int]:
    print(f"[{context} ERROR] {type(exc).__name__}: {exc}")
    traceback.print_exc()
    
    if isinstance(exc, APIError):
        if exc.code == 429:
            return {"success": False, "message": "Analysis limit reached. Please wait and try again.", "error_code": "QUOTA_EXCEEDED"}, 429
        elif exc.code == 404:
            return {"success": False, "message": "AI Model not found or unavailable.", "error_code": "MODEL_UNAVAILABLE"}, 502
        elif exc.code == 403 or exc.code == 400:
            return {"success": False, "message": "Invalid API key or authentication error.", "error_code": "AUTHENTICATION_ERROR"}, 401
        elif exc.code == 503:
            return {"success": False, "message": "The AI service is currently overloaded. Please wait a minute and try again.", "error_code": "SERVICE_UNAVAILABLE"}, 503
            
    return {"success": False, "message": "An unexpected error occurred while analyzing your startup.", "error_code": f"SERVER_ERROR_{type(exc).__name__}"}, 502

@app.get("/api/gemini-test")
def test_gemini():
    if not client:
        return jsonify({"success": False, "message": "Gemini API key is missing."}), 503
        
    try:
        response = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents="Respond with exactly 'Gemini API is working.'",
        )
        return jsonify({"success": True, "message": response.text.strip()}), 200
    except Exception as exc:
        error_resp, status_code = _handle_gemini_error(exc, "Test")
        return jsonify(error_resp), status_code

@app.post("/api/generate-dashboard")
def generate_dashboard():
    import uuid
    request_id = str(uuid.uuid4())[:8]
    print(f"[Dashboard] Request ID: {request_id}")
    print("[Dashboard] Request received")
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"success": False, "message": "Dashboard analysis failed.", "error_code": "MISSING_REQUEST_DATA"}), 400

    startup_id = data.get("id")
    if not startup_id:
        return jsonify({"success": False, "message": "Startup ID is required.", "error_code": "MISSING_STARTUP_ID"}), 400
        
    # Standardize if frontend sends "startup-X" or just integer X
    if isinstance(startup_id, str) and startup_id.startswith("startup-"):
        startup_id = int(startup_id.replace("startup-", ""))

    if not data.get("idea", "").strip():
        return jsonify({"success": False, "message": "Dashboard analysis failed.", "error_code": "MISSING_STARTUP_IDEA"}), 400

    if not client:
        return jsonify({"success": False, "message": "Dashboard analysis failed.", "error_code": "MISSING_API_KEY"}), 503

    prompt = _build_dashboard_prompt(data)

    print("[Dashboard] Gemini request started")
    try:
        response = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DashboardAnalysis,
                temperature=0.7,
            ),
        )
        print("[Dashboard] Gemini response received")
        
        try:
            parsed = json.loads(response.text)
            
            # Verify validation_experiment is present and not empty
            experiments = parsed.get("validation_experiment", [])
            if not experiments or len(experiments) == 0:
                print("[Dashboard] Error: validation_experiment is empty.")
                return jsonify({"success": False, "message": "The AI failed to generate validation steps. Please try again.", "error_code": "INVALID_JSON_RESPONSE"}), 502
                
            print("[Dashboard] JSON validation successful")
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"[Dashboard] Gemini error type: {type(exc).__name__}")
            print(f"[Dashboard] Gemini error: {exc}")
            return jsonify({"success": False, "message": "Received invalid response from AI. Please try again.", "error_code": "INVALID_JSON_RESPONSE"}), 502

    except Exception as exc:
        print(f"[Dashboard] Gemini error type: {type(exc).__name__}")
        print(f"[Dashboard] Gemini error: {exc}")
        error_resp, status_code = _handle_gemini_error(exc, "Generate Dashboard")
        return jsonify(error_resp), status_code

    # Save to database
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Save or update the analysis
        cursor.execute('''
            INSERT INTO analyses (startup_id, startup_name, industry, validation_overview, overview, market_analysis, competition, risks, business, mvp, quick_insights, validation_experiment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(startup_id) DO UPDATE SET
                startup_name=excluded.startup_name,
                industry=excluded.industry,
                validation_overview=excluded.validation_overview,
                overview=excluded.overview,
                market_analysis=excluded.market_analysis,
                competition=excluded.competition,
                risks=excluded.risks,
                business=excluded.business,
                mvp=excluded.mvp,
                quick_insights=excluded.quick_insights,
                validation_experiment=excluded.validation_experiment,
                updated_at=CURRENT_TIMESTAMP
        ''', (
            startup_id,
            parsed.get("startup_name", ""),
            parsed.get("industry", ""),
            json.dumps(parsed.get("validation_overview", {})),
            json.dumps(parsed.get("overview", {})),
            json.dumps(parsed.get("market", {})),
            json.dumps(parsed.get("competition", [])),
            json.dumps(parsed.get("risks", [])),
            json.dumps(parsed.get("business", {})),
            json.dumps(parsed.get("mvp", {})),
            json.dumps(parsed.get("quick_insights", [])),
            json.dumps(parsed.get("validation_experiment", []))
        ))
        
        # 2. Save tasks
        experiments = parsed.get("validation_experiment", [])

            
        # Delete old tasks for this startup to replace with new ones
        cursor.execute('DELETE FROM mvp_tasks WHERE startup_id = ?', (startup_id,))
        
        tasks_saved = 0
        for idx, task in enumerate(experiments):
            # Create a robust unique ID: startup_id-step-N
            task_id = f"{startup_id}-{task.get('id', f'step-{idx}')}"
            cursor.execute('''
                INSERT INTO mvp_tasks (id, startup_id, task_name, description, completed)
                VALUES (?, ?, ?, ?, 0)
            ''', (
                task_id,
                startup_id,
                task.get("title", ""),
                task.get("description", "")
            ))
            tasks_saved += 1
            
        # 3. Update startup validation score and name/category
        score = parsed.get("validation_overview", {}).get("score", 0)
        cursor.execute('''
            UPDATE startups 
            SET validation_score = ?, name = ?, category = ?, progress = 0 
            WHERE id = ?
        ''', (score, parsed.get("startup_name", "New Startup Idea"), parsed.get("industry", ""), startup_id))
        
        conn.commit()
    except Exception as db_exc:
        conn.rollback()
        print(f"[Dashboard] Database save error: {db_exc}")
        return jsonify({"success": False, "message": "Failed to save analysis to database.", "error_code": "DATABASE_ERROR"}), 500
    finally:
        conn.close()
    
    print("[Dashboard] Analysis saved to database")
    print("[Dashboard] Analysis sent to frontend")

    return jsonify({
        "success": True,
        "analysis": parsed
    }), 200
    

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import database
    database.init_db()
    app.run(host="0.0.0.0", port=8000, debug=True)
