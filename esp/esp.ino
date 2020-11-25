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
#define ULTRASONIC_ADDRESS 0xE0

#define TRANSMIT_FIRST (TRANSMIT_INTERVAL * 60 * 1000)

// calculate the amount of samples for a car of `length` traveling with `speed`
// length / (speed / 3.6 * 100 / 10)
//                               ^ we sample at 10Hz
//                         ^ times 100 converts m/s to cm/s
//                   ^ division by 3.6 converts km/h to m/s
//           ^ in km/h
// ^ in cm
// the shorted form is length / (speed / 0.36)
#define MIN_SAMPLES_CAR ((uint16_t)(MIN_LENGTH_CAR / (SPEED_LIMIT / 0.36)))
#define MIN_SAMPLES_TRUCK ((uint16_t)(MIN_LENGTH_TRUCK / (SPEED_LIMIT / 0.36)))

typedef struct __attribute__((packed))
{
	uint16_t carCount;
	uint16_t truckCount;
	uint16_t battery;
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

// Pin mapping
// see https://github.com/cyberman54/ESP32-Paxcounter/blob/master/src/lorawan.cpp#L44
// and https://github.com/cyberman54/ESP32-Paxcounter/blob/master/src/lorawan.cpp#L44
#define LORA_IRQ DIO0
#define LORA_IO1 DIO1
#define LORA_IO2 DIO2
#define LORA_SCK GPIO_NUM_5
#define LORA_MISO MISO
#define LORA_MOSI MOSI
#define LORA_RST RST_LoRa
#define LORA_CS SS
/*
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

void transmitPacket(uint16_t carCount, uint16_t truckCount)
{
	vehicle_statistics_packet_t packet;

	packet.carCount = carCount;
	packet.truckCount = truckCount;
	packet.battery = analogRead(VBAT_PIN);

	LOG(INFO, "Starting transmission...");
	LMIC_setTxData2(1, (uint8_t *)&packet, sizeof(vehicle_statistics_packet_t), 0);
}

uint16_t readDistance()
{
	Wire.requestFrom((uint16_t)ULTRASONIC_ADDRESS, (uint8_t)2, (bool)true);
	if(Wire.available() != 2)
		return 0xffff;

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

	// LMIC init
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
}

void loop()
{
	os_runloop_once();

	static uint16_t carCount = 0;
	static uint16_t truckCount = 0;

	static uint32_t nextTransmit = TRANSMIT_FIRST;
	uint32_t now = millis();
	if(now > nextTransmit && (now < TRANSMIT_FIRST || nextTransmit > TRANSMIT_FIRST))
	{
		transmitPacket(carCount, truckCount);
		carCount = 0;
		truckCount = 0;
	}

	static uint16_t recentMaxReading = 0;
	static bool carDetectionCount = 0;

	uint16_t distance = readDistance();
	if(distance != 0xffff)
	{
		LOG(DEBUG, "Distance reading: ", distance);
		if(recentMaxReading - distance > 50)
		{
			carDetectionCount++;
		}
		else if(carDetectionCount != 0)
		{
			LOG(INFO, "Detected vehicle blocking for ", carDetectionCount, " cycles");
			if(carDetectionCount > MIN_SAMPLES_TRUCK)
				truckCount++;
			else if(carDetectionCount > MIN_SAMPLES_CAR)
				carCount++;
			carDetectionCount = 0;
		}

		recentMaxReading -= 100;
		if(distance > recentMaxReading)
		{
			LOG(DEBUG, "New max reading: ", distance);
			recentMaxReading = distance;
		}
	}
	else
	{
		LOG(ERROR, "Failed reading data from sensor!");
	}

	delay(95);
}
