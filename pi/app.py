import subprocess
import json
import os

from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SERVICE_NAME = "motionsensor"

@app.route("/")
def main():
	return render_template("main.html")


@app.route("/get_status")
def get_status():
	status_raw = subprocess.Popen("systemctl is-active {}".format(SERVICE_NAME), shell=True, stdout=subprocess.PIPE).stdout
	status = status_raw.read().decode()[:-1] == "active"
	return json.dumps({"status": "ok", "running": status})


@app.route("/get_mode")
def get_mode():
	return json.dumps({"status": "ok", "mode": os.getenv("RUN_MODE")})

@app.route("/get_history")
def get_history():
	with open("history.json") as file:
		try:
			return json.dumps(json.load(file))
		except json.decoder.JSONDecodeError:
			return json.dumps({})


app.run("0.0.0.0", 5000, debug=True)
