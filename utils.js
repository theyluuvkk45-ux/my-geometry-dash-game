/**
 * @param {string} hex The hex string, like #XXXXXX.
 * @returns {number[]} The RGB values.
 */
function getRGBFromHex(hex) {
	return hex.substring(1).match(/.{1,2}/g).map((v) => parseInt(v, 16))
}
/**
 * @param {number[]} color The RGB values.
 * @returns {string} The hex string, like #XXXXXX.
 */
function getHexFromRGB(color) {
	return "#" + color.map((v) => v.toString(16).padStart(2, "0")).join("")
}