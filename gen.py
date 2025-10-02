import os
import json
from server_main import format_level, read_file, write_file
import random
import typing
import math

level_datas: list[dict[str, typing.Any]] = []
for i in os.listdir("levels/published/"):
	level_datas.append(json.loads(read_file("levels/published/" + i)))
for i in os.listdir("levels/user/"):
	level_datas.append(json.loads(read_file("levels/user/" + i)))

class Rect:
	def __init__(self, x: int, y: int, width: int, height: int):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
	def colliderect(self, other: "Rect") -> bool:
		return (self.x < other.x + other.width and
				self.x + self.width > other.x and
				self.y < other.y + other.height and
				self.y + self.height > other.y)
	def copy(self):
		return Rect(self.x, self.y, self.width, self.height)

T = typing.TypeVar('T')
R = typing.TypeVar('R')
class Optional(typing.Generic[T]):
	def __init__(self, value: T | None = None):
		self._value = value
	def ifPresent(self, func: typing.Callable[[ T ], typing.Any]):
		if self._value != None:
			func(self._value)
	def getOr(self, replacement: T) -> T:
		if self._value == None:
			return replacement
		else:
			return self._value
	def transform(self, func: typing.Callable[[ T ], R]) -> "Optional[R]":
		if self._value == None:
			return Optional()
		else:
			return Optional(func(self._value))

class LevelObject:
	def __init__(self, data: dict[str, typing.Any]):
		self.data = data
	def getData(self, name: str) -> Optional[float]:
		if name in self.data["data"].keys():
			d = self.data["data"][name]
			try:
				r = int(d)
				return Optional(r)
			except: pass
		return Optional()
	def setData(self, name: str, data: Optional[float]):
		data.ifPresent(lambda x: self.setRawData(name, x))
	def setRawData(self, name: str, data: float):
		self.data["data"][name] = data
	def moveBy(self, x: float, y: float):
		self.setData("x", self.getData("x").transform(lambda v: v + x))
		self.setData("y", self.getData("y").transform(lambda v: v + y))
	def copy(self):
		return LevelObject(dict(self.data))

class Level:
	def __init__(self, name: str, objects: list[LevelObject]):
		self.name = name
		self.objects = objects
	def copy(self):
		return Level(self.name, [o.copy() for o in self.objects])
	def rotate(self):
		for o in self.objects:
			oldX = o.getData("x")
			oldY = o.getData("y")
			oldR = o.getData("rotation")
			oldY.ifPresent(lambda y: o.setData("x", oldX.transform(lambda x: y)))
			oldX.ifPresent(lambda x: o.setData("y", oldY.transform(lambda y: -x)))
			# o.setData("rotation", oldR.transform(lambda r: (180 - r) % 360))
			# that was for flipping whoops
			o.setData("rotation", oldR.transform(lambda r: (r + 90) % 360))
		self.align()
	def getXs(self):
		x: list[float] = []
		for o in self.objects:
			o.getData("x").ifPresent(x.append)
		return x
	def getYs(self):
		y: list[float] = []
		for o in self.objects:
			o.getData("y").ifPresent(y.append)
		return y
	def align(self):
		x = self.getXs()
		y = self.getYs()
		if len(x) == 0 or len(y) == 0: return
		minX = min(x)
		minY = min(y)
		for o in self.objects:
			o.moveBy(-minX, -minY)
	def getRect(self) -> Rect:
		self.align()
		x = self.getXs()
		y = self.getYs()
		if len(x) == 0 or len(y) == 0: return Rect(0, 0, 0, 0)
		maxX = max(x)
		maxY = max(y)
		return Rect(0, 0, math.ceil(maxX), math.ceil(maxY))
	def doesCollide(self, other: "Level", pos: tuple[float, float]):
		thisXs = self.getXs()
		thisYs = self.getYs()
		otherXs = other.getXs()
		otherYs = other.getYs()
		for i in range(len(thisXs)):
			for n in range(len(otherXs)):
				if thisXs[i] == otherXs[n] + pos[0]:
					if thisYs[i] == otherYs[n] + pos[1]:
						return True
		return False
	def blit(self, other: "Level", pos: tuple[float, float]):
		oc = other.copy()
		for o in oc.objects:
			o.moveBy(pos[0], pos[1])
			self.objects.append(o)
	def explode(self):
		for o in [*self.objects]:
			chance = 0.3
			if o.data["type"].split(".")[0] == "death":
				chance = 0.9
			if random.random() < chance:
				self.objects.remove(o)
	def save(self):
		coins: list[bool] = []
		for o in self.objects:
			if o.data["type"] == "special.coin":
				coins.append(False)
		formatted = format_level({
			"name": "Combination",
			"description": self.name,
			"settings": {
				"colorbg": [0, 125, 255],
				"colorstage": [0, 125, 255],
				"gamemode": "cube"
			},
			"objects": [x.data for x in self.objects],
			"completion": {
				"percentage": 0,
				"coins": coins
			},
			"deleted": False
		})
		write_file(f"levels/user/gen_{random.randint(1, 100000)}.json", formatted)

	@staticmethod
	def fromDict(name: str, data: list[dict[str, typing.Any]]):
		return Level(name, [LevelObject(x) for x in data])

levels: list[Level] = [Level.fromDict(x["name"], x["objects"]) for x in level_datas]
combined: Level = Level("Combination of everything", [])

levelsLeft: list[Level] = []
for l in levels:
	levelsLeft.append(l.copy())
	l.rotate()
	levelsLeft.append(l.copy())
	l.rotate()
	levelsLeft.append(l.copy())
	l.rotate()
	levelsLeft.append(l.copy())

random.shuffle(levelsLeft)
levelsLeft = levelsLeft[:15]

positions: list[tuple[int, int]] = []
for l in levelsLeft:
	l.explode()
	pos = (
		random.randint(-10, 10),
		random.randint(-10, 10)
	)
	positions.append(pos)
for i in range(len(levelsLeft)):
	l = levelsLeft[i]
	pos = positions[i]
	if not combined.doesCollide(l, pos):
		combined.blit(l, pos)
combined.align()
combined.save()
