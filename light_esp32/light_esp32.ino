e#include <WiFi.h>
#include <ESPmDNS.h>
#include <WebServer.h>

const char* ssid = "Crimson College 2.4G";  
const char* password = "cct@2222"; 

const int ledPin = 4;  // GPIO 4 corresponds to D4
WebServer server(80);

void handleRoot() {
  server.send(200, "text/plain", "ESP32 is online");
}

void handleLedOn() {
  digitalWrite(ledPin, HIGH);
  server.send(200, "text/plain", "LED is ON");
}

void handleLedOff() {
  digitalWrite(ledPin, LOW);
  server.send(200, "text/plain", "LED is OFF");
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to Wi-Fi");

  if (!MDNS.begin("h")) {  // Use the hostname "h"
    Serial.println("Error starting mDNS");
    return;
  }
  Serial.println("mDNS started");

  pinMode(ledPin, OUTPUT);

  server.on("/", handleRoot);
  server.on("/led/on", handleLedOn);
  server.on("/led/off", handleLedOff);

  server.begin();
}


void loop() {
  server.handleClient();
}
