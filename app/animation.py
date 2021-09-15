#!/usr/bin/python3
from struct import pack

OPCODE_FRAME_START = 0
OPCODE_FRAME_END   = 1
OPCODE_SLEEP       = 2
OPCODE_LED         = 3

class Animation:
	def __init__(self, initColors, frames, perFrameWait, perAnimationWait):
		self.initColors = initColors

		self.framesNum = frames

		self.perFrameWait = perFrameWait

		self.perAnimationWait = perAnimationWait

		self.frames = []

		self.currentFrame = None

	def currentFrameNum(self):
		return len(self.frames)

	def createFrame(self):
		if len(self.frames) >= self.framesNum:
			raise Exception("Too many frames created!")

		# Either init with the init data or duplicate the previous frame
		if self.currentFrame is None:
			self.currentFrame = Frame(self.initColors)
		else:
			self.currentFrame = Frame(self.currentFrame)

		self.frames.append(self.currentFrame)

		return self.currentFrame

	def encode(self):
		data = bytes()

		for frame in self.frames:
			data += frame.encode()

			sleepTime = self.perFrameWait

			while sleepTime > 255:
				data += pack("BB", OPCODE_SLEEP, 255)
				sleepTime -= 255

			data += pack("BB", OPCODE_SLEEP, sleepTime)

		endSleep = self.perAnimationWait

		while endSleep > 255:
			data += pack("BB", OPCODE_SLEEP, 255)
			endSleep -= 255

		if endSleep > 0:
			data += pack("BB", OPCODE_SLEEP, endSleep)

		return data

	def __iter__(self):
		return self

	def __next__(self):
		if self.currentFrameNum() == self.framesNum:
			raise StopIteration()
		return self.currentFrameNum()

	def __repr__(self):
		data = []

		data.append("__ANIMATION__")

		for frame, frameIdx in zip(self.frames, range(len(self.frames))):
			data += [ "\t #%d " % frameIdx + obj for obj in frame.__repr__() ]

		return data

	def __str__(self):
		return "\n".join(self.__repr__())

class Frame:
	def __init__(self, frameData):
		self.leds = []

		self.iterIdx = 0

		if type(frameData) is list:
			for led in frameData:
				if "brightness" not in led:
					led["brightness"] = 0

				self.leds.append(LED(led["red"], led["green"], led["blue"], led["brightness"]))
		elif frameData.__class__ is Frame:
			for led in frameData.leds:
				self.leds.append(LED(led.red, led.green, led.blue, led.brightness))

	def setBrightness(self, value):
		for led in self.leds:
			led.brightness = value

	def addBrightness(self, value):
		for led in self.leds:
			led.brightness += value

	def addColors(self, red, green, blue):
		for led in self.leds:
			led.red = (led.red + red + 0x100) & 0xff
			led.green = (led.green + green + 0x100) & 0xff
			led.blue = (led.blue + blue + 0x100) & 0xff

	def addColors_limited(self, red, green, blue):
		for led in self.leds:
			if led.red + red < 0:
				led.red = 0
			elif led.red + red > 0xff:
				led.red = 0xff
			else:
				led.red += red

			if led.green + green < 0:
				led.green = 0
			elif led.green + green > 0xff:
				led.green = 0xff
			else:
				led.green += green

			if led.blue + blue < 0:
				led.blue = 0
			elif led.blue + blue > 0xff:
				led.blue = 0xff
			else:
				led.blue += blue

	def encode(self):
		data = bytes()
		data += pack("B", OPCODE_FRAME_START)

		for led in self.leds:
			data += led.encode()

		# Add one more "fake LED" to fix late-lit last LED
		for idx in range(2):
			data += self.leds[-1].encode()

		data += pack("B", OPCODE_FRAME_END)

		return data

	def __iter__(self):
		self.iterIdx = 0

		return self

	def __next__(self):
		if self.iterIdx == len(self.leds):
			raise StopIteration()

		led = self.leds[self.iterIdx]
		self.iterIdx += 1

		return led

	def __repr__(self):
		data = []

		data.append("__FRAME__")

		data += [ "\t" + led.__repr__() for led in self.leds ]

		return data

	def __str__(self):
		return "\n".join(self.__repr__())

class LED:
	def __init__(self, red, green, blue, brightness):
		self.red = abs(red)
		self.green = abs(green)
		self.blue = abs(blue)
		self.brightness = brightness

	def add(self, red, green, blue):
		if self.red + red < 0:
			self.red = 0
		elif self.red  + red > 255:
			self.red = 255
		else:
			self.red += red

		if self.green + green < 0:
			self.green = 0
		elif self.green  + green > 255:
			self.green = 255
		else:
			self.green += green

		if self.blue + blue < 0:
			self.blue = 0
		elif self.blue  + blue > 255:
			self.blue = 255
		else:
			self.blue += blue

	def encode(self):
		return pack("BBBBB", OPCODE_LED, abs(self.red), abs(self.green), abs(self.blue), abs(self.brightness))

	def __repr__(self):
		return "RED: %-3d GREEN: %-3d BLUE: %-3d BRIGHTNESS: %-3d" % (self.red, self.green, self.blue, self.brightness)

	def __str__(self):
		return self.__repr__(self)
