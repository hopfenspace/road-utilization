#include <Arduino.h>
#include <WiFi.h>
#include <Wire.h>
#include <stdint.h>

#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>
#include <SSD1306.h>
#include <soc/efuse_reg.h>

#include "./config.h"
#include "./log.hpp"

#define OLED_I2C_ADDR 0x3C
#define OLED_RESET 16
#define OLED_SDA 4
#define OLED_SCL 15

#define VBAT_PIN 35
//#define ULTRASONIC_ADDRESS 0xE0
// see https://github.com/tsayles/Photon-I2C-RangeFinder/blob/master/firmware/weather-ranger.ino#L70
#define ULTRASONIC_ADDRESS 0x70

#define TRANSMIT_FIRST (TRANSMIT_INTERVAL * 60 * 1000)

// calculate the amount of samples for a car of `length` traveling with `speed`
// length / (speed / 3.6 * 100 / 9.090909)
//                               ^ we sample every 110ms (9.090909Hz)
//                         ^ times 100 converts m/s to cm/s
//                   ^ division by 3.6 converts km/h to m/s
//           ^ in km/h
// ^ in cm
// the shorted form is length / (speed / 0.36)
#define MIN_SAMPLES_CAR ((uint16_t)(MIN_LENGTH_CAR / (SPEED_LIMIT / 3.6 * 100 / 9.090909)))
#define MIN_SAMPLES_TRUCK ((uint16_t)(MIN_LENGTH_TRUCK / (SPEED_LIMIT / 3.6 * 100 / 9.090909)))

typedef struct __attribute__((packed))
{
	uint16_t battery;
	uint16_t vehicleCounts[9];
} vehicle_statistics_packet_t;

SSD1306 display (OLED_I2C_ADDR, OLED_SDA, OLED_SCL);
Print *logger;

static u1_t NWKSKEY[16] = { LORAWAN_NWKEY }; 
static u1_t APPSKEY[16] = { LORAWAN_APPKEY };
static u4_t DEVADDR = LORAWAN_DEVID;

// unused in ABP mode
void os_getArtEui (u1_t* buf) { }
void os_getDevEui (u1_t* buf) { }
void os_getDevKey (u1_t* buf) { }

/*
// Pin mapping
// see https://github.com/cyberman54/ESP32-Paxcounter/blob/master/src/hal/heltecv2.h
// and https://github.com/cyberman54/ESP32-Paxcounter/blob/master/src/lorawan.cpp#L44
#define LORA_IRQ DIO0
#define LORA_IO1 DIO1
#define LORA_IO2 DIO2
#define LORA_SCK GPIO_NUM_5
#define LORA_MISO MISO
#define LORA_MOSI MOSI
#define LORA_RST RST_LoRa
#define LORA_CS SS
// see https://resource.heltec.cn/download/WiFi_LoRa_32/WIFI_LoRa_32_V2.pdf
#define LORA_IRQ 26 // DIO0
#define LORA_IO1 33
#define LORA_IO2 32
#define LORA_SCK 5
#define LORA_MISO 19
#define LORA_MOSI 27
#define LORA_RST 14
#define LORA_CS 18
*/
// Pin mapping
// see https://github.com/cyberman54/ESP32-Paxcounter/blob/master/src/hal/ttgov21new.h
// and https://github.com/cyberman54/ESP32-Paxcounter/blob/master/src/lorawan.cpp#L44
#define LORA_SCK  (5)
#define LORA_CS   (18)
#define LORA_MISO (19)
#define LORA_MOSI (27)
#define LORA_RST  (23)
#define LORA_IRQ  (26)
#define LORA_IO1  (33)
#define LORA_IO2  (32)
const lmic_pinmap lmic_pins = {
	.nss = LORA_CS,
	.rxtx = LMIC_UNUSED_PIN,
	.rst = LORA_RST,
	.dio = {LORA_IRQ, LORA_IO1, LORA_IO2},
	//.rxtx_rx_active = LMIC_UNUSED_PIN,
	//.rssi_cal = 10,
	//.spi_freq = 8000000, // 8MHz
};

void onEvent (ev_t ev)
{
	if (ev == EV_TXCOMPLETE)
	{
		LOG(INFO, "Data transmission complete");
	}
}

void transmitPacket(vehicle_statistics_packet_t *packet)
{
	LOG(INFO, "Starting transmission...");
	LMIC_setTxData2(1, (uint8_t *)packet, sizeof(vehicle_statistics_packet_t), 0);
}

void startSensorReading()
{
	Wire.beginTransmission(ULTRASONIC_ADDRESS);
	Wire.write(0x51); // trigger sensor reading
	Wire.endTransmission();
}
uint16_t readDistance()
{
	Wire.requestFrom((uint16_t)ULTRASONIC_ADDRESS, (uint8_t)2, (bool)true);
	if(Wire.available() != 2)
		return 0xffff;

	// read distance in cm as a big endian 16bit value
	uint16_t ret = Wire.read() << 8;
	ret |= Wire.read();
	return ret;
}

void setup()
{
#ifdef LOG_LEVEL
	Serial.begin(115200);
	logger = &Serial;
	delay(1500);
#endif

	LOG(INFO, "Initializing...");

	LOG(DEBUG, "Initializing display...");
	display.init();
	display.displayOff();

	LOG(DEBUG, "Turning off WiFi...");
	WiFi.mode(WIFI_OFF);

	LOG(DEBUG, "Initializing ultrasonic sensor...");
	Wire.begin(21, 22, 100000);
	startSensorReading();

	LOG(DEBUG, "Initializing LMIC...");
	os_init();
	LMIC_reset();

	// Set up the channels used by the Things Network
	LMIC_setupChannel(0, 868100000, DR_RANGE_MAP(DR_SF12, DR_SF7),  BAND_CENTI);      // g-band
	LMIC_setupChannel(1, 868300000, DR_RANGE_MAP(DR_SF12, DR_SF7B), BAND_CENTI);      // g-band
	LMIC_setupChannel(2, 868500000, DR_RANGE_MAP(DR_SF12, DR_SF7),  BAND_CENTI);      // g-band
	LMIC_setupChannel(3, 867100000, DR_RANGE_MAP(DR_SF12, DR_SF7),  BAND_CENTI);      // g-band
	LMIC_setupChannel(4, 867300000, DR_RANGE_MAP(DR_SF12, DR_SF7),  BAND_CENTI);      // g-band
	LMIC_setupChannel(5, 867500000, DR_RANGE_MAP(DR_SF12, DR_SF7),  BAND_CENTI);      // g-band
	LMIC_setupChannel(6, 867700000, DR_RANGE_MAP(DR_SF12, DR_SF7),  BAND_CENTI);      // g-band
	LMIC_setupChannel(7, 867900000, DR_RANGE_MAP(DR_SF12, DR_SF7),  BAND_CENTI);      // g-band
	LMIC_setupChannel(8, 868800000, DR_RANGE_MAP(DR_FSK,  DR_FSK),  BAND_MILLI);      // g2-band

	LMIC_setSession(0x1, DEVADDR, NWKSKEY, APPSKEY); // Set static session parameters.
	LMIC_setLinkCheckMode(0); // Disable link check validation
	LMIC.dn2Dr = DR_SF9; // TTN uses SF9 for its RX2 window.

	// Set data rate and transmit power for uplink (note: txpow seems to be ignored by the library)
	LMIC_setDrTxpow(LORAWAN_SPREADING, 14);

	LOG(INFO, "Initialization done");
	LOG(INFO, "MIN_SAMPLES_CAR == ", MIN_SAMPLES_CAR, ", MIN_SAMPLES_TRUCK == ", MIN_SAMPLES_TRUCK);

	delay(110);
}

void loop()
{
	os_runloop_once();

	static vehicle_statistics_packet_t packet;

	static uint32_t nextTransmit = TRANSMIT_FIRST;
	uint32_t now = millis();
	if(now >= nextTransmit && (now <= TRANSMIT_FIRST || nextTransmit >= TRANSMIT_FIRST))
	{
		packet.battery = analogRead(VBAT_PIN);
		transmitPacket(&packet);

		for(int i = 0; i < 9; i++)
			packet.vehicleCounts[i] = 0;
		nextTransmit = now + TRANSMIT_FIRST;
	}

	static int16_t recentMaxReading = 0;
	static uint16_t carDetectionCount = 0;

	int16_t distance = readDistance();
	startSensorReading(); // start a new reading to be read next time
	if(distance != 0xffff)
	{
		LOG(DEBUG, "Distance reading: ", distance, ", recentMax: ", recentMaxReading);
		if(recentMaxReading - distance > 50)
		{
			carDetectionCount++;
		}
		else if(carDetectionCount != 0)
		{
			LOG(INFO, "Detected vehicle blocking for ", carDetectionCount, " cycles");
			carDetectionCount--;
			if(carDetectionCount < 8)
				packet.vehicleCounts[carDetectionCount]++;
			else
				packet.vehicleCounts[8]++;
			carDetectionCount = 0;
		}

		if(abs(recentMaxReading - distance) < 10)
			recentMaxReading = distance;
		else if(distance < recentMaxReading && recentMaxReading > 10)
			recentMaxReading -= 10;
		else if(distance > recentMaxReading)
			recentMaxReading += 10;
	}
	else
	{
		LOG(ERROR, "Failed reading data from sensor!");
	}

	// try to somewhat accurately run a measurement every 110ms
	uint32_t end = millis();
	if(now + 110 > end)
		delay(110 - (end - now));
}
