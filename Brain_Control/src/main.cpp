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

// Variables de detección 
char emocionDetec = ' ';
char ultimaEmocion = '0';

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

void moverOrejas(int grados){
  motorDer.write(grados);
  motorIzq.write(180 - grados);
  delay(1000);
}

void loop() {
  // put your main code here, to run repeatedly:

  // Detecta si ha llegado un paquete
  int packetSize = udp.parsePacket();
  if(packetSize){
    int len = udp.read(packetBuffer, 255);
    
    if(len > 0) packetBuffer[len] = 0;

    emocionDetec = packetBuffer[0];

    if(emocionDetec != ultimaEmocion){
      Serial2.write(emocionDetec);
      switch (emocionDetec)
      {
      case '0':
        /* code */
        moverOrejas(90);
        break;
      
      case '1':
        moverOrejas(153);
        break;

      case '2':
        moverOrejas(45);
        break;

      case '3':
        moverOrejas(15);
        break;
      }

      ultimaEmocion = emocionDetec;
    }
  }
}
