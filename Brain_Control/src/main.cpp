// --- LIBRERIAS ---
#include <Arduino.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// --- Declaraciones ---

// Comunicación Serial con Arduino 
#define RXD2 16
#define TXD2 17

// Punto de Acceso
const char *ssid = "ProyectoRobotica";
const char *password = "123456789";

// Comunicación por socket
WiFiUDP udp;
unsigned int localPort = 8080;

// Bus de paquetes 
char packetBuffer[255];

void setup() {
  Serial.begin(115200);
  
  // Configuración para arduino
  Serial2.begin(9600,SERIAL_8N1, RXD2, TXD2);

  // Creación punto de acceso
  WiFi.disconnect(true);
  WiFi.mode(WIFI_AP);

  WiFi.softAP(ssid,password);

  IPAddress localIP = WiFi.softAPIP();
}

void loop() {
  // put your main code here, to run repeatedly:
}
