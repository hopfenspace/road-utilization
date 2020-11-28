var streetTypes = {
	"living_street": 1,
	"residential": 2,
	"tertiary": 3,
	"secondary": 5,
	"primary": 7,
};

var mainMap = L.map('mainmap', {
	minZoom: 10,
	maxZoom: 20,
	maxBounds: [
		[51, 8],
		[46, 15.5],
	],
}).setView([48.5300, 11.5056], 15);

L.tileLayer('https://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png ', {
	subdomains: 'abc',
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, '
		+ '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
}).addTo(mainMap);

function render(streets, traffic)
{
	var usages = Object.values(traffic).map(x => x.count_truck * 3 + x.count_car);
	var maxUsage = usages.reduce((a, b) => Math.max(a, b));

	for(var name in streets)
	{
		var street = streets[name];
		var usage = traffic[name] || {count_car: 0, count_truck: 0};
		usage = (usage.count_truck * 3 + usage.count_car) / maxUsage;

		var color;
		if(usage < 0.3)
			color = "green";
		else if(usage < 0.6)
			color = "orange";
		else
			color = "red";

		var width = 20;
		if(streetTypes.hasOwnProperty(street.type))
			width = streetTypes[street.type];

		var latLongs = street.coordinates.map(x => [x.lat, x.long]);
		L.polyline(latLongs, {
				color: color,
				fillOpacity: 0.7
			})
			.addTo(mainMap);
	}
}

Promise.all([
	fetch('streets.json')
		.then(res => res.json()),
	fetch('data.json', {cache: "no-cache"})
		.then(res => res.json()),
])
	.then(([streets, traffic]) => render(streets.result, traffic.result));