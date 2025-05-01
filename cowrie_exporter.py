from flask import Flask, Response
from prometheus_client import Counter, generate_latest
import json
import os
import time
from threading import Thread

app = Flask(__name__)

LOGIN_ATTEMPTS = Counter(
    "cowrie_ssh_login_attempts_total",
    "SSH login attempts recorded by Cowrie",
    ["username", "success"]
)

LOG_FILE = "/cowrie/log/cowrie.json"

def tail_log():
    """ Continuously tail cowrie.json and update Prometheus counters """
    with open(LOG_FILE, "r") as f:
        f.seek(0, os.SEEK_END)  # Go to end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            try:
                event = json.loads(line)
                if event.get("eventid") == "cowrie.login.failed":
                    LOGIN_ATTEMPTS.labels(username=event["username"], success="false").inc()
                elif event.get("eventid") == "cowrie.login.success":
                    LOGIN_ATTEMPTS.labels(username=event["username"], success="true").inc()
            except json.JSONDecodeError:
                continue

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

if __name__ == "__main__":
    t = Thread(target=tail_log)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=9100)
