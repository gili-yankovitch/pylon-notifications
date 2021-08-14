#!/usr/bin/python3:
from app.animation import Animation

def init(colors):
	animation = Animation(colors, 1, 100, 30000)

	initFrame = animation.createFrame()

	initFrame.setBrightness(16)

	return animation

def frame(animation):
	return animation
