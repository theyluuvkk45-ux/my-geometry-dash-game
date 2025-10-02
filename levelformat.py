import json
import typing

class LevelSettings(typing.TypedDict):
	colorbg: list[int]
	colorground: list[int]
	gamemode: typing.Literal["cube", "ship", "ball", "wave"]
	platformer: bool

class LevelObjectData(typing.TypedDict):
	x: int
	y: int
	rotation: int
	groups: list[str]

class LevelObject(typing.TypedDict):
	type: str
	data: LevelObjectData

class LevelCompletion(typing.TypedDict):
	percentage: int
	coins: list[bool]

class Level(typing.TypedDict):
	name: str
	description: str
	settings: LevelSettings
	objects: list[LevelObject]
	completion: LevelCompletion
	deleted: bool

def format_level(t: "Level"):
	def format_o(o: "LevelObject"):
		keys: list[str] = [*o["data"].keys()]
		data = [f"""\"{k}\": {json.dumps(o["data"][k])}""" for k in keys]
		return f"""{{"type": "{o["type"]}", "data": {{{', '.join(data)}}}}}"""
	objects = ',\n'.join([
		format_o(o)
		for o in t["objects"]
	]).replace("\n", "\n\t\t")
	result = f"""{{
	"name": {json.dumps(t["name"])},
	"description": {json.dumps(t["description"])},
	"settings": {{
		"colorbg": {json.dumps(t["settings"]["colorbg"])},
		"colorground": {json.dumps(t["settings"]["colorground"])},
		"gamemode": {json.dumps(t["settings"]["gamemode"])},
		"platformer": {json.dumps(t["settings"]["platformer"])}
	}},
	"objects": [
		{objects}
	],
	"completion": {{
		"percentage": {json.dumps(t["completion"]["percentage"])},
		"coins": {json.dumps(t["completion"]["coins"])}
	}},
	"deleted": {json.dumps(t["deleted"])}
}}"""
	return result

def read_file(filename: str) -> bytes:
	f = open(filename, "rb")
	t = f.read()
	f.close()
	return t

def write_file(filename: str, content: str):
	f = open(filename, "w")
	f.write(content)
	f.close()

def read_level(filename: str) -> "Level":
	return json.loads(read_file(filename))

def write_level(filename: str, content: "Level"):
	try:
		write_file(filename, format_level(content))
	except Exception as e:
		print("ERROR WRITING FILE: " + filename)
		print(e)
