import json
import sys
import base64
from server_main import HttpResponse, get, post

class URLQuery:
	def __init__(self, q):
		self.orig = q
		self.fields = {}
		for f in q.split("&"):
			s = f.split("=")
			if len(s) >= 2:
				self.fields[s[0]] = s[1]
	def get(self, key):
		if key in self.fields:
			return self.fields[key]
		else:
			return ''

class MyServer:
	def read_packet(self) -> bytes:
		headers = b""
		newChar = b""
		while newChar != b".":
			headers += newChar
			newChar = sys.stdin.buffer.read(1)
		length = int(headers)
		content = b""
		for i in range(length):
			content += sys.stdin.buffer.read(1)
		return content
	def handle_request(self):
		method = self.read_packet()
		path = self.read_packet().decode("UTF-8")
		body = self.read_packet().decode("UTF-8")
		res: HttpResponse = {
			"status": 404,
			"headers": {},
			"content": b""
		}
		if method == b"GET":
			res = self.do_GET(path)
		if method == b"POST":
			res = self.do_POST(path, body)
		s: list[bytes | str] = [
			str(res["status"]).encode("UTF-8"),
			",".join([f"{a}:{b}" for a, b in res["headers"].items()]).encode("UTF-8"),
			res["content"]
		]
		for data in s:
			self.send_packet(data)
			# time.sleep(0.3)
	def send_packet(self, info: bytes | str):
		try: info = info.decode("UTF-8") # type: ignore
		except: pass
		if isinstance(info, str):
			sys.stdout.buffer.write(str(len(info)).encode("UTF-8"))
			sys.stdout.buffer.write(b".")
			sys.stdout.buffer.write(info.encode("UTF-8"))
		elif isinstance(info, bytes):
			e = base64.b64encode(info)
			sys.stdout.buffer.write(str(len(e) + 1).encode("UTF-8"))
			sys.stdout.buffer.write(b".$")
			sys.stdout.buffer.write(e)
		sys.stdout.buffer.flush()
		# try: print("Printed[", str(len(info)), '.', info.decode("UTF-8"), "]", sep="", file=sys.stderr)
		# except UnicodeDecodeError: print("Printed[", str(len(info)), '.', info, "]", sep="", file=sys.stderr)
	def do_GET(self, path) -> HttpResponse:
		res = get(path)
		c: str | bytes = res["content"]
		if isinstance(c, str): c = c.encode("utf-8")
		return {
			"status": res["status"],
			"headers": res["headers"],
			"content": c
		}
	def do_POST(self, path: str, body: str) -> HttpResponse:
		res = post(path, body.encode("UTF-8"))
		c: str | bytes = res["content"]
		if isinstance(c, str): c = c.encode("utf-8")
		return {
			"status": res["status"],
			"headers": res["headers"],
			"content": c
		}

if __name__ == "__main__":
	running = True
	webServer = MyServer()
	print(f"Fake server (geometry dash) started", file=sys.stderr)
	# sys.stdout.flush()
	while running:
		try:
			webServer.handle_request()
		except KeyboardInterrupt:
			running = False
	print("Server stopped", file=sys.stderr)
