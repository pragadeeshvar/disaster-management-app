from flask import Flask, render_template_string, request, redirect, url_for, flash
import json, os, datetime, re

app = Flask(__name__)
app.secret_key = "disaster-secret"

DATA_FILE = "disaster_reports.json"

PHONE_REGEX = re.compile(r'^[\d\+\-\s]{5,20}$')

# Sample emergency contacts
EMERGENCY_CONTACTS = [
    {"role": "Fire Department", "phone": "+91-101"},
    {"role": "Ambulance", "phone": "+91-102"},
    {"role": "Police", "phone": "+91-100"},
    {"role": "Disaster Management Office", "phone": "+91-1800-123-456"},
    {"role": "Local Hospital", "phone": "+91-11-12345678"},
]

# Sample resources and instructions
RESOURCES = [
    "Nearest shelter locations",
    "First aid kits",
    "Drinking water (bottled)",
    "Non-perishable food supplies",
    "Portable radio and spare batteries",
    "Flashlights",
    "Blankets and warm clothing",
    "Emergency contact list printed",
]

EVACUATION_INSTRUCTIONS = [
    "Follow official evacuation orders from local authorities.",
    "If indoors during an earthquake: Drop, Cover, and Hold On.",
    "If there is a flood risk: move to higher ground and avoid floodwater.",
    "If there is a fire: evacuate immediately and stay low to avoid smoke.",
    "Carry essential documents, medicines, and a flashlight.",
    "Keep family/friends informed about your location if possible.",
]

def load_reports():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_reports(reports):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)

def timestamp_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def validate_phone(phone):
    return bool(PHONE_REGEX.match(phone.strip())) if phone else False

@app.route("/")
def index():
    reports = load_reports()
    return render_template_string(TEMPLATE_INDEX, reports=reports)

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        data = request.form
        reporter_name = data.get("reporter_name", "").strip()
        reporter_phone = data.get("reporter_phone", "").strip()
        if reporter_phone and not validate_phone(reporter_phone):
            flash("Invalid phone format.")
            return redirect(url_for("report"))
        report = {
            "id": len(load_reports()) + 1,
            "timestamp": timestamp_now(),
            "type": data.get("type"),
            "location": data.get("location"),
            "severity": data.get("severity"),
            "affected_estimate": data.get("affected_estimate"),
            "notes": data.get("notes"),
            "reporter_name": reporter_name or None,
            "reporter_phone": reporter_phone or None,
        }
        reports = load_reports()
        reports.append(report)
        save_reports(reports)
        flash("Report submitted successfully!")
        return redirect(url_for("index"))
    return render_template_string(TEMPLATE_REPORT)

@app.route("/contacts")
def contacts():
    return render_template_string(TEMPLATE_CONTACTS, contacts=EMERGENCY_CONTACTS)

@app.route("/resources")
def resources():
    return render_template_string(TEMPLATE_RESOURCES, resources=RESOURCES, instructions=EVACUATION_INSTRUCTIONS)

TEMPLATE_INDEX = """
<!doctype html>
<title>Disaster Management App</title>
<style>
body { font-family: Arial; background: #eef3f9; color:#222; }
.container { max-width: 900px; margin: auto; background:white; padding:20px; border-radius:12px; box-shadow:0 0 10px #aaa; }
a { text-decoration:none; color:#007bff; }
table { width:100%; border-collapse:collapse; margin-top:10px; }
th, td { border:1px solid #ccc; padding:8px; text-align:center; }
h1 { text-align:center; color:#003366; }
nav a { margin:10px; }
.flash { color:green; text-align:center; }
</style>
<div class="container">
<h1>🌏 Disaster Management System</h1>
<nav>
<a href="{{ url_for('index') }}">Home</a> |
<a href="{{ url_for('report') }}">Report Disaster</a> |
<a href="{{ url_for('contacts') }}">Emergency Contacts</a> |
<a href="{{ url_for('resources') }}">Resources</a>
</nav>
{% with messages = get_flashed_messages() %}
  {% if messages %}
  <div class="flash">{{ messages[0] }}</div>
  {% endif %}
{% endwith %}
<h2>Saved Reports</h2>
{% if reports %}
<table>
<tr><th>ID</th><th>Type</th><th>Location</th><th>Severity</th><th>Reporter</th><th>Phone</th><th>Time</th></tr>
{% for r in reports %}
<tr>
<td>{{r.id}}</td>
<td>{{r.type}}</td>
<td>{{r.location}}</td>
<td>{{r.severity}}</td>
<td>{{r.reporter_name or 'N/A'}}</td>
<td>{{r.reporter_phone or 'N/A'}}</td>
<td>{{r.timestamp}}</td>
</tr>
{% endfor %}
</table>
{% else %}
<p>No reports yet. <a href="{{ url_for('report') }}">Report one now</a>.</p>
{% endif %}
</div>
"""

TEMPLATE_REPORT = """
<!doctype html>
<title>Report Disaster</title>
<style>
body { font-family: Arial; background:#eef3f9; }
.container { max-width:600px; margin:auto; background:white; padding:20px; border-radius:12px; box-shadow:0 0 10px #aaa; }
input, select, textarea { width:100%; padding:8px; margin:6px 0; border:1px solid #ccc; border-radius:6px; }
button { background:#007bff; color:white; padding:10px; border:none; border-radius:6px; cursor:pointer; }
button:hover { background:#0056b3; }
a { text-decoration:none; color:#007bff; }
</style>
<div class="container">
<h2>🚨 Report a Disaster</h2>
<form method="POST">
<label>Your Name:</label>
<input type="text" name="reporter_name" placeholder="Optional">
<label>Your Phone:</label>
<input type="text" name="reporter_phone" placeholder="+91-">
<label>Disaster Type:</label>
<select name="type">
<option>Earthquake</option>
<option>Flood</option>
<option>Storm</option>
<option>Fire</option>
<option>Landslide</option>
<option>Tsunami</option>
<option>Other</option>
</select>
<label>Location:</label>
<input type="text" name="location" required>
<label>Severity (1–5):</label>
<input type="number" name="severity" min="1" max="5" value="3">
<label>Affected People (est.):</label>
<input type="number" name="affected_estimate" min="0">
<label>Additional Notes:</label>
<textarea name="notes" rows="4"></textarea>
<button type="submit">Submit Report</button>
</form>
<p><a href="{{ url_for('index') }}">← Back</a></p>
</div>
"""

TEMPLATE_CONTACTS = """
<!doctype html>
<title>Emergency Contacts</title>
<style>
body { font-family: Arial; background:#eef3f9; }
.container { max-width:600px; margin:auto; background:white; padding:20px; border-radius:12px; box-shadow:0 0 10px #aaa; }
table { width:100%; border-collapse:collapse; }
th, td { border:1px solid #ccc; padding:8px; text-align:center; }
</style>
<div class="container">
<h2>☎️ Emergency Contacts</h2>
<table>
<tr><th>Role</th><th>Phone</th></tr>
{% for c in contacts %}
<tr><td>{{c.role}}</td><td>{{c.phone}}</td></tr>
{% endfor %}
</table>
<p><a href="{{ url_for('index') }}">← Back</a></p>
</div>
"""

TEMPLATE_RESOURCES = """
<!doctype html>
<title>Resources & Evacuation</title>
<style>
body { font-family: Arial; background:#eef3f9; }
.container { max-width:800px; margin:auto; background:white; padding:20px; border-radius:12px; box-shadow:0 0 10px #aaa; }
ul { line-height:1.8; }
</style>
<div class="container">
<h2>📦 Key Resources</h2>
<ul>
{% for r in resources %}
<li>{{r}}</li>
{% endfor %}
</ul>
<h2>🚶‍♀️ Evacuation Instructions</h2>
<ol>
{% for i in instructions %}
<li>{{i}}</li>
{% endfor %}
</ol>
<p><a href="{{ url_for('index') }}">← Back</a></p>
</div>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
