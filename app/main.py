#!/usr/bin/python3

import os
# from requests import get, post, put
from datetime import datetime
import requests as rq
import configparser
from werkzeug.utils import secure_filename
from flask import Flask, request, Response, render_template, send_from_directory
from threading import Thread
from time import sleep
from json import dumps
from struct import pack
from pymongo import MongoClient
from . import filters

ledData = {}
version = 0
VALID_CODE = 0x42

# Get DB
client = MongoClient(os.environ["MONGO_URI"])
db = client["pylon"]
collection = db["notifications"]

app = Flask(__name__,
	static_folder = 'static',
	template_folder='templates')

def _getStatus(id):
	global ledData
	ledData = collection.find_one({"id": id})["data"]

	return ledData

def _updateStatus(id, data):
	global version
	global ledData

	# Add version
	ledData["version"] = version

	version += 1

	# ledData["animation"] = data["animation"]
	ledData["animation"] = data["animation"]
	ledData["colors"] = data["colors"]

	# Expand
	if type(data["colors"]) is not list:
		data["colors"] = [ data["colors"] ] * 6

	record = {"timestamp": datetime.now(), "data": data, "id": id }

	if _getStatus(id) is None:
		res = collection.insert_one(record)
	else:
		res = collection.update_one({"id": id}, {"$set": record })

def _disableNotification(timeout):
	print("Disabling notification in %ds" % timeout)
	sleep(timeout)
	current = _getStatus(os.environ["ENV_ID"])
	print(current)
	_updateStatus(os.environ["ENV_ID"], {"animation": "still", "colors": current["colors"]})
	print("Notification disabled")

@app.route("/notify", methods = ["POST"])
def _notify():
	data = request.get_json()

	if data is None or \
		"animation" not in data or \
		"colors" not in data or \
		"timeout" not in data:
		return dumps({"success": False}), 500

	# Update DB data
	res = _updateStatus(os.environ["ENV_ID"], data)

	print("Version: %d" % version)
	print(data)

	# Create the disabling thread
	thread = Thread(target = _disableNotification, args = (data["timeout"], ))
	thread.start()

	return dumps({"success": True})

@app.route("/get", methods = ["GET"])
def _get():
	global ledData

	if ledData is None or "version" not in ledData:
		data = _getStatus(os.environ["ENV_ID"])["data"]

		ledData = data["data"]

		if "version" in ledData:
			version = ledData["version"]

	response = bytes()
	response += pack("BB", VALID_CODE, version & 0xff) # Version

	if "animation" not in ledData or	\
		"colors" not in ledData or		\
		ledData["animation"] not in filters.filters:
		return "\x00Invalid data", 400

	animation = filters.filters[ledData["animation"]].init(ledData["colors"])

	for frameIdx in animation:
		frame = filters.filters[ledData["animation"]].frame(animation)

	# print(animation)

	return response + animation.encode()

@app.route("/getText", methods = ["GET"])
def _getText():
	global ledData

	ledData = _getStatus(os.environ["ENV_ID"])

	print("Data:", ledData)

	return dumps(ledData)
