#!/usr/bin/python3:
from app.animation import Animation

def init(colors):
	animation = Animation(colors, 1, 255, 30000)

	initFrame = animation.createFrame()

	initFrame.setBrightness(0)

	return animation

def frame(animation):
	return animation
