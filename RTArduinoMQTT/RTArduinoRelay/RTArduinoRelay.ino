
////////////////////////////////////////////////////////////////////////////
//
//  This file is part of RTMQTT
//
//  Copyright (c) 2015-2016, richards-tech, LLC
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy of
//  this software and associated documentation files (the "Software"), to deal in
//  the Software without restriction, including without limitation the rights to use,
//  copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
//  Software, and to permit persons to whom the Software is furnished to do so,
//  subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
//  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
//  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
//  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
//  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
//  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <jsmn.h>

//  This is the mac address to use. Make sure it is unique on your network!

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};

//  This is the IP address of the MQTT broker - change it to whatever is correct

IPAddress server(192, 168, 10, 10);

//  This is used to identify this set of devices. It is an 8 digit decimal number as a string and must be unique in the system
//
//  Must not start with 0.

#define DEVICEID "12345678"

//  This is the topic used to publish updates - must be unique and always end with "status"

#define STATUS_TOPIC "arduino/status"

//  This is the topic on which to listen for control messages - must be unique and always end with "control"

#define CONTROL_TOPIC "arduino/control"

EthernetClient ethClient;
PubSubClient client(ethClient);

//  The JSON parser

jsmn_parser jsmnParser;
jsmntok_t jsmnTokens[32];

//
//  JSON control messages expected to look like this:
//
// {"setDeviceLevel": [{"deviceID": 123456782,"newLevel": 0}]}
//
// except with the appropriate 9 digit deviceID and level value (0-255)
//
//  Decoded JSON vars

int typeSeq[8] = {JSMN_OBJECT, JSMN_STRING, JSMN_ARRAY, JSMN_OBJECT, JSMN_STRING, JSMN_PRIMITIVE, JSMN_STRING, JSMN_PRIMITIVE};

bool devicePresent;
bool levelPresent;

int device;
int level;

long lastReconnectAttempt = 0;
long lastStatusUpdate = 0;

//  Outgoing status message
//
//  The final message looks like this example:
//
//  {"updateList":"currentLevel":255,"deviceID":123456781,"name":"Relay1"}]}

#define STATUS_STRING_LEVEL         "{\"updateList\":[{\"currentLevel\":"
#define STATUS_STRING_DEVICEID      ",\"deviceID\":"
#define STATUS_STRING_NAME          ",\"name\":\"Relay"
#define STATUS_STRING_END           "\"}]}"

char statusMessage[90];

//  Relay setup

#define RELAY_COUNT         4

int relayPins[RELAY_COUNT] = {2, 3, 5, 6};

//  This can be used to set the default relay state - this is all off

int relayInitialLevels[RELAY_COUNT] = {0, 0, 0, 0};

int relayLevels[RELAY_COUNT];

//  Utility routine to check strings in JSON message

int jsoneq(const char *json, jsmntok_t *tok, const char *s) {
    if (tok->type == JSMN_STRING && (int) strlen(s) == tok->end - tok->start &&
            strncmp(json + tok->start, s, tok->end - tok->start) == 0) {
        return 1;
    }
    return 0;
}

//  JSMN callback

void callback(char* topic, byte* payload, unsigned int length) {
    int count;
    int pos;

    jsmn_init(&jsmnParser);
    if ((count = jsmn_parse(&jsmnParser, (char *)payload, length, jsmnTokens, sizeof(jsmnTokens) / sizeof(jsmntok_t))) < 0) {
        Serial.print("Failed to parse control msg - ");
        Serial.println(count);
        return;
    }   

    if (count != 8) {
        Serial.println("Wrong JSON control format");
        return;
    }

    for (int i = 0; i < 8; i++) {
        if (jsmnTokens[i].type != typeSeq[i]) {
            Serial.println("Incorrect token type");
            return;
        }
    }

    devicePresent = levelPresent = false;

    if (!jsoneq((char *)payload, &jsmnTokens[1], "setDeviceLevel"))
        return;
 
    if (!jsoneq((char *)payload, &jsmnTokens[4], "deviceID"))
        return;
        
    if (!jsoneq((char *)payload, &jsmnTokens[6], "newLevel"))
        return;

    int relayNumber = ((char *)payload)[jsmnTokens[5].end - 1] - '0';

    if ((relayNumber < 0) || (relayNumber >= RELAY_COUNT))
        return;

    relayLevels[relayNumber] = ((char *)payload)[jsmnTokens[7].start] - '0';
    digitalWrite(relayPins[relayNumber], (relayLevels[relayNumber] > 0) ? LOW : HIGH);
}

boolean reconnect() {
    if (client.connect("arduinoClient")) {
        client.subscribe(CONTROL_TOPIC);
    }
    return client.connected();
}

void addInteger(int val)
{
    int length;
    
    if (val >= 10)
        addInteger(val / 10);
    length = strlen(statusMessage);
    statusMessage[length] = '0' + val % 10;        
    statusMessage[length + 1] = 0;
}

void setup()
{
    Serial.begin(115200);
    
    client.setServer(server, 1883);
    client.setCallback(callback);

    Ethernet.begin(mac);
    delay(1500);
    Serial.println(Ethernet.localIP());
    lastReconnectAttempt = 0;

    // preset relays

    for (int i = 0; i < RELAY_COUNT; i++) {
        pinMode(relayPins[i], OUTPUT);
        relayLevels[i] = relayInitialLevels[i];
        digitalWrite(relayPins[i], (relayLevels[i] > 0) ? LOW : HIGH);
    }
}


void loop()
{
    Ethernet.maintain();
  
    long now = millis();

    if (!client.connected()) {
        if (now - lastReconnectAttempt > 2000) {
            lastReconnectAttempt = now;
            // Attempt to reconnect
            if (reconnect()) {
                lastReconnectAttempt = 0;
                Serial.println("Connected");
            }
        }
    } else {
        if ((now - lastStatusUpdate) > 2000) {
            for (int i = 0; i < RELAY_COUNT; i++) {
                strcpy(statusMessage, STATUS_STRING_LEVEL);
                addInteger((relayLevels[i] > 0) ? 255 : 0);
                strcat(statusMessage, STATUS_STRING_DEVICEID);
                strcat(statusMessage, DEVICEID);
                addInteger(i);
                strcat(statusMessage, STATUS_STRING_NAME);
                addInteger(i);
                strcat(statusMessage, STATUS_STRING_END);
                client.publish(STATUS_TOPIC, statusMessage);
            }
            lastStatusUpdate = now;
        }
        client.loop();
    }
}
