function int16_LE(bytes, idx) {
	bytes = bytes.slice(idx || 0);
	return bytes[0] << 0 | bytes[1] << 8;
}

function Decoder(bytes, port) {
	var decoded = {};

	decoded.count_car = int16_LE(bytes, 0);
	decoded.count_truck = int16_LE(bytes, 2);
	decoded.battery = int16_LE(bytes, 4) / 4095 * 2 * 3.3 * 1.1;

	return decoded;
}
