var view = new View()
view.loadLevel()

/** @type {SceneItem | null | string} */
var editing = null

var floorHeight = 0.25
var tileSize = 30

/**
 * @param {MouseEvent} evt
 */
function on_click(evt) {
	var pos = [
		// @ts-ignore
		Math.floor(evt.clientX / tileSize) + document.querySelector("#viewX").valueAsNumber,
		Math.floor(((window.innerHeight * (1 - floorHeight)) - evt.clientY) / tileSize)// - 1
	]
	if (pos[1] < 0) return
	if (pos[0] < 0) return
	// @ts-ignore
	pos[1] += document.querySelector("#viewY").valueAsNumber
	if (editing != null) deselect()
	// @ts-ignore
	var selectedBlock = document.querySelector(".option-element-selected").dataset.value
	if (selectedBlock == ".eraser") {
		// Remove
		for (var i = 0; i < view.tiles.length; i++) {
			var tile = view.tiles[i]
			if (tile.x == pos[0] && tile.y == pos[1]) {
				tile.destroy()
				view.tiles.splice(i, 1)
				i -= 1;
			}
		}
	} else if (selectedBlock == ".rotate") {
		// Rotate
		for (var i = 0; i < view.tiles.length; i++) {
			var tile = view.tiles[i]
			if (tile.x == pos[0] && tile.y == pos[1]) {
				tile.rotation = (tile.rotation + 90) % 360
				tile.update()
			}
		}
	} else if (selectedBlock == ".edit") {
		// Edit
		var tiles = []
		for (var i = 0; i < view.tiles.length; i++) {
			var tile = view.tiles[i]
			if (Math.round(tile.x) == pos[0] && Math.round(tile.y) == pos[1]) {
				tiles.push(tile)
			}
		}
		editTileList(tiles)
	} else {
		// Add new block
		var type = getObjectFromLocation("tile", selectedBlock.split("."))
		var args = type.default(pos)
		/** @type {Tile} */
		var newTile = type.load(view, type, args)
		view.tiles.push(newTile)
		editTile(newTile)
		newTile.update()
	}
}
// @ts-ignore
document.querySelector("#scene").addEventListener("click", on_click);
/** @param {Tile} tile */
function editTile(tile) {
	if (editing != null) deselect()
	editing = tile
	// UI
	/** @type {HTMLElement} */
	// @ts-ignore
	var parent = document.querySelector(".editing")
	parent.removeAttribute("style")
	parent.innerHTML = tile.getEdit().join("")
	tile.update()
}
/** @param {Tile[]} tiles */
function editTileList(tiles) {
	if (editing != null) deselect()
	if (tiles.length == 0) return
	if (tiles.length == 1) return editTile(tiles[0])
	// UI
	/** @type {HTMLElement} */
	// @ts-ignore
	var parent = document.querySelector(".editing")
	parent.removeAttribute("style")
	parent.innerHTML = `<div style="display: inline-block;">Select tile to edit:</div>`
	for (var i = 0; i < tiles.length; i++) {
		var e = document.createElement("div")
		e.classList.add("option-element")
		e.setAttribute("style", `display: inline-block;`)
		// @ts-ignore
		e.innerHTML = `<div style="background: url(data:image/svg+xml;base64,${btoa(tiles[i].getImage())}); width: 1em; height: 1em; display: inline-block;"></div>`
		parent.appendChild(e)
		// @ts-ignore
		e._TileSource = tiles[i]
		e.setAttribute("onclick", "deselect(); editTile(this._TileSource)")
	}
}
function deselect() {
	if (editing instanceof Tile) {
		var tile = editing
		editing = null
		tile.update()
	}
	if (editing != null) editing = null
	/** @type {HTMLElement} */
	// @ts-ignore
	var parent = document.querySelector(".editing")
	parent.setAttribute("style", "display: none;")
}

var debug = false
function getExport() {
	var r = []
	for (var i = 0; i < view.tiles.length; i++) {
		var tile = view.tiles[i]
		var location = ["error"]
		var r_location = getLocationFromObject("tile", tile)
		if (r_location) location = [...r_location]
		var type = location.join(".")
		r.push({
			type,
			data: tile.save()
		})
	}
	return r
}
function exportLevel() {
	saveLevel().then((e) => {
		var r = getExport()
		var data = btoa(JSON.stringify(r))
		window.open("../game/index.html?level=user/" + e)
	})
}
function saveLevel() {
	return new Promise((resolve) => {
		var coins = []
		for (var i = 0; i < view.tiles.length; i++) {
			var t = view.tiles[i]
			if (t instanceof Coin) {
				coins.push(false)
			}
		}
		var x = new XMLHttpRequest()
		x.open("POST", "/save_user")
		x.addEventListener("loadend", () => resolve(x.responseText))
		x.send(JSON.stringify({
			"name": levelName,
			"level": {
				"name": levelMeta.name,
				"description": levelMeta.description,
				"settings": levelMeta.settings,
				"objects": getExport(),
				"completion": {
					"percentage": 0,
					"coins": coins
				},
				"deleted": false
			}
		}))
	})
}
// async function publishLevel() {
// 	await new Promise((resolve) => {
// 		var coins = []
// 		for (var i = 0; i < view.tiles.length; i++) {
// 			var t = view.tiles[i]
// 			if (t instanceof Coin) {
// 				coins.push(false)
// 			}
// 		}
// 		var x = new XMLHttpRequest()
// 		x.open("POST", "/publish")
// 		x.addEventListener("loadend", () => resolve(x.responseText))
// 		x.send(JSON.stringify({
// 			"name": levelName,
// 			"level": {
// 				"name": levelMeta.name,
// 				"description": levelMeta.description,
// 				"settings": levelMeta.settings,
// 				"objects": getExport(),
// 				"completion": {
// 					"percentage": 0,
// 					"coins": coins
// 				},
// 				"deleted": false
// 			}
// 		}))
// 	})
// 	location.replace("../home/home.html")
// }
function editLevelSettings() {
	editing = "settings"
	/** @type {HTMLElement} */
	// @ts-ignore
	var parent = document.querySelector(".editing")
	parent.removeAttribute("style")
	parent.innerHTML = [
		`Level Name: <input type="text" oninput="levelMeta.name = this.value">`,
		`Level Description:<br><textarea oninput="levelMeta.description = this.value"></textarea>`,
		`Starting Background Color: <input type="color" value="${getHexFromRGB(levelMeta.settings.colorbg)}" oninput="levelMeta.settings.colorbg = getRGBFromHex(this.value)"></div>`,
		`Starting Ground Color: <input type="color" value="${getHexFromRGB(levelMeta.settings.colorground)}" oninput="levelMeta.settings.colorground = getRGBFromHex(this.value)"></div>`,
		`Starting Gamemode: <select oninput="levelMeta.settings.gamemode = this.value">${Object.keys(registries.gamemode).map((v) => `
	<option value="${v}"${levelMeta.settings.gamemode==v ? " selected" : ""}>${v}</option>`)}
</select>`,
		`Is Platformer Level: <input type="checkbox"${levelMeta.settings.platformer ? " checked": ""} oninput="levelMeta.settings.platformer = this.checked">`
	].map((v) => `<div>${v}</div>`).join("")
	// @ts-ignore
	parent.children[0].children[0].value = levelMeta.name
	// @ts-ignore
	parent.children[1].children[1].value = levelMeta.description
}
function updateViewPos() {
	// @ts-ignore
	var x = document.querySelector("#viewX").valueAsNumber
	// @ts-ignore
	var y = document.querySelector("#viewY").valueAsNumber
	document.querySelector('#scene')?.setAttribute('style', `--move-amount-x: ${x}; --move-amount-y: ${y};`)
}

/**
 * @param {string[]} folder
 */
function addOptionElements(folder) {
	var items = getObjectFromLocation("tile", folder)
	var k = Object.keys(items)
	for (var i = 0; i < k.length; i++) {
		if (typeof items[k[i]] == "object") {
			addOptionElements([...folder, k[i]])
		} else {
			var e = document.createElement("span")
			e.classList.add("option-element")
			e.setAttribute("onclick", `this.classList.add("option-element-selected")`)
			e.innerHTML = `<div style="background: url(data:image/svg+xml;base64,${btoa(items[k[i]].getImage())}); background-repeat: no-repeat; background-position: center; width: 1.3em; height: 1.3em; display: inline-block;"></div>`
			e.dataset.value = [...folder, k[i]].join(".")
			document.querySelector("#blocks")?.appendChild(e)
		}
	}
}

(() => {
	document.querySelector("#blocks")?.addEventListener("click", () => {
		document.querySelector('.option-element-selected')?.classList.remove('option-element-selected');
	}, true)
	addOptionElements([])
})();
