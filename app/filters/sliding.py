#!/usr/bin/python3
from app.animation import Animation

LEDS_PER_FRAME = 6

def init(colors):
	animation = Animation(colors, len(colors) / LEDS_PER_FRAME, 750, 50)

	initFrame = animation.createFrame()

	initFrame.setBrightness(16)

	return animation

def frame(animation):
	nextFrame = animation.createFrame()

	nextFrame.leds = nextFrame.leds[LEDS_PER_FRAME:] + nextFrame.leds[:LEDS_PER_FRAME]

	return animation
