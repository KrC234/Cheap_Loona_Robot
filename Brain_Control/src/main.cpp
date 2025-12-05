// --- LIBRERIAS ---
#include <Arduino.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// --- Declaraciones ---

// Comunicación Serial con Arduino 
#define RXD2 16
#define TXD2 17

Servo motorDer;
Servo motorIzq;

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

  // Servos
  motorDer.attach(18);
  motorIzq.attach(19);

  motorDer.write(0);
  motorIzq.write(180);
  // Creación punto de acceso
  WiFi.disconnect(true);
  WiFi.mode(WIFI_AP);

  WiFi.softAP(ssid,password);

  IPAddress localIP = WiFi.softAPIP();
}

void loop() {
  // put your main code here, to run repeatedly:

  // Detecta si ha llegado un paquete
  int packetSize = udp.parsePacket();
  if(packetSize){
    int len = udp.read(packetBuffer, 255);
    
    if(len > 0) packetBuffer[len] = 0;

    char emocion = packetBuffer[0];

    Serial2.write(emocion);
    
    // Casos de emocion para los motores
    switch (emocion)
    {
    case '0':
      /* code */
      break;
    case '1':
      break;
    case '2': 
      break;
    case '3':
      break;
    }
  }
}
