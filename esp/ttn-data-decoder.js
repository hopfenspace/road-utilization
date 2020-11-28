function int16_LE(bytes, idx) {
	bytes = bytes.slice(idx || 0);
	return bytes[0] << 0 | bytes[1] << 8;
}

function Decoder(bytes, port) {
	var decoded = {};

	decoded.battery = int16_LE(bytes, 0) / 4095 * 2 * 3.3 * 1.1;
	decoded.vehicles = {};
	for(var i = 0; i < 9; i++)
	{
		var cycles = (i + 1).toString();
		decoded.vehicles[cycles] = int16_LE(bytes, 2 + i * 2);
	}

	return decoded;
}
