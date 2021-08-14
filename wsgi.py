#!/usr/bin/python3
import os
from app.main import app

if __name__ == "__main__":
	#print(updateStatus(os.environ["ENV_ID"], {"version": 0, "animation": "still", "colors": "#0000ff"}))
	#print(getStatus(os.environ["ENV_ID"]))
	app.run("0.0.0.0", port = 5000)
	# socketio.run(app, "0.0.0.0")
