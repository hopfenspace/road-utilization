var streetTypes = {
	"living_street": -1,
	"residential": -2,
	"tertiary": 3,
	"secondary": 5,
	"primary": 7,
};

var mainMap = L.map('mainmap', {
	minZoom: 10,
	maxZoom: 18,
	maxBounds: [
		[51, 8],
		[46, 15.5],
	],
}).setView([48.7640, 11.4290], 15);

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
		if(usage < 0.5)
			color = "rgb(" + (usage * 2 * 255) + ", 150, 0)";
		else
			color = "rgb(255, " + ((1 - usage * 2) * 150) + ", 0)";

		var width = 3;
		if(streetTypes.hasOwnProperty(street.road_type))
			width = streetTypes[street.road_type];

		if(width < 0)
		{
			color = "grey";
			width = -width;
		}

		L.polyline(street.coordinates, {
				color: color,
				weight: width,
				fillOpacity: 0.7
			})
			.addTo(mainMap);
	}
}

var streetPath = "/api/getRoads";
var dataPath = "/api/getRoadUtilization";

if(document.location.hostname === "localhost")
{
	streetPath = "streets.json";
	dataPath = "data.json";
}

Promise.all([
	fetch(streetPath)
		.then(res => res.json()),
	fetch(dataPath, {cache: "no-cache"})
		.then(res => res.json()),
])
	.then(([streets, traffic]) => render(streets.result, traffic.result));