import os
import levelformat

files = os.listdir("levels/published")
for name in files:
	t: levelformat.Level = levelformat.read_level("levels/published/" + name)
	t["completion"]["percentage"] = 0
	t["completion"]["coins"] = [False for _ in t["completion"]["coins"]]
	levelformat.write_level("levels/published/" + name, t)

files = os.listdir("levels/user")
for name in files:
	t: levelformat.Level = levelformat.read_level("levels/user/" + name)
	t["completion"]["percentage"] = 0
	t["completion"]["coins"] = [False for _ in t["completion"]["coins"]]
	levelformat.write_level("levels/user/" + name, t)
