var view = new GameView()
view.loadLevel()

/**
 * @param {number} amount
 */
function frame(amount) {
	if (view instanceof GameView) {
		for (var i = 0; i < view.particles.length; i++) {
			view.particles[i].tick(amount)
		}
	}
	view.stage.tick(amount)
	view.player?.tick(amount)
	for (var i = 0; i < view.tiles.length; i++) {
		view.tiles[i].tick(amount)
	}
	view.player?.finishTick(amount)
}
function aFrames() {
	if ((! view.hasWon) && view.deathTime > 0) {
		view.deathTime -= 1
		if (view.deathTime <= 0) {
			view.stage.reset()
			view.player = new Player(view)
			for (; view.tiles.length > 0; ) {
				view.tiles[0].destroy()
				view.tiles.splice(0, 1)
			}
			view.importObjects()
			view.attempt += 1
		}
	}
	var n_frames = 1
	if (view.player) n_frames = Math.ceil(Math.abs(view.player.vy * 4) + 1)
	// view.particles.push(new RectDisplay(new Rect(view.player.x - 1, 0, 0.1, n_frames), "pink"))
	for (var i = 0; i < n_frames; i++) {
		frame(1 / n_frames)
	}
}
async function frameLoop() {
	while (true) {
		aFrames()
		await new Promise((resolve) => requestAnimationFrame(resolve))
	}
}
function setup() {
	setTimeout(frameLoop, 1000)
	view.particles.push(new ProgressBar(view))
}
setup()
