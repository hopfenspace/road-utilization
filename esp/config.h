#pragma once

// network key in MSB
#define LORAWAN_NWKEY 0x00, 0x00, 0x00, 0x00 // ...
// app key in MSB
#define LORAWAN_APPKEY 0x00, 0x00, 0x00, 0x00 // ...
// device id in hex
#define LORAWAN_DEVID 0xDEADC0DE

// DR_SF7 - DR_SF12
#define LORAWAN_SPREADING DR_SF12

//#define LOG_LEVEL LOG_OFF
#define LOG_LEVEL LOG_DEBUG

// time between packets in minutes
#define TRANSMIT_INTERVAL 15

#define SPEED_LIMIT 30 // km/h
#define MIN_LENGTH_CAR 200 // cm
#define MIN_LENGTH_TRUCK 700 // cm
