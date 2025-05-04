from flask import Flask, render_template, request
import os
from mission_builder import build_mission

app = Flask(__name__)

# Adjust these to your install & missions path:
INSTALL_PATH = r"M:\T34vsTiger"
MISSION_ROOT  = r"M:\T34vsTiger\Missions\MyMission"

def get_existing_missions():
    return [
        d for d in os.listdir(MISSION_ROOT)
        if os.path.isdir(os.path.join(MISSION_ROOT, d))
    ]

@app.route("/", methods=["GET", "POST"])
def form():
    message = ""
    missions = get_existing_missions()

    if request.method == "POST":
        data = request.form

        source    = data["source"]                  # e.g. "Murkz2025"
        new_name  = data["new_name"].strip()        # e.g. "WebDev9"
        title     = data["title"].strip()           # menu name
        briefing  = data.get("briefing","").strip()
        orders    = data.get("orders","").strip()
        # collect up to 5 objectives, skip empties
        objectives = [
            data.get(f"obj{i}","").strip()
            for i in range(1, 6)
        ]
        objectives = [o for o in objectives if o]

        campaign    = data["campaign"]               # "ussr" or "germany"
        editor_mode = "editor" in data               # future toggle

        try:
            build_mission(
                install_path  = INSTALL_PATH,
                source_folder = f"MyMission\\{source}",
                new_name      = new_name,
                title         = title,
                briefing      = briefing,
                orders        = orders,
                objectives    = objectives,
                campaign      = campaign,
                editor_mode   = editor_mode
            )
            message = f"✅ Mission '{new_name}' created successfully."
        except Exception as e:
            message = f"❌ Error: {e}"

    return render_template("form.html",
                           missions=missions,
                           message=message)

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
