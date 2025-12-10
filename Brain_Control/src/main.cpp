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

// Motor A
const int ENA = 25;  
const int IN1 = 26;
const int IN2 = 27;

// Motor B
const int ENB = 33;  
const int IN3 = 14;
const int IN4 = 12;

// --- Configuración PWM (LEDC) ---
const int freq = 5000;
const int canalA = 12;
const int canalB = 13;
const int resolucion = 8;

// --- DICCIONARIO ---
const int MOTOR_A = 0;
const int MOTOR_B = 1;
const int ADELANTE = 1;
const int ATRAS = -1;
const int PARAR = 0;

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
char ultimaEmocion = ' ';

void setup() {
  Serial.begin(115200);
  
  // Configuración para arduino
  Serial2.begin(9600,SERIAL_8N1, RXD2, TXD2);

  // Servos
  motorDer.attach(18);
  motorIzq.attach(19);

  motorDer.write(0);
  motorIzq.write(180);

  // Configuración de Motores
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Vincular pines PWM
  ledcAttachPin(ENA, canalA);
  ledcAttachPin(ENB, canalB);

  // Configurar PWM
  ledcSetup(canalA, freq, resolucion);
  ledcSetup(canalB, freq, resolucion);

  // Creación punto de acceso
  WiFi.disconnect(true);
  WiFi.mode(WIFI_AP);

  WiFi.softAP(ssid,password);

  IPAddress localIP = WiFi.softAPIP();

  udp.begin(localPort);

  ultimaEmocion = '0';
}

void moverOrejas(int grados){
  motorDer.write(grados);
  motorIzq.write(180 - grados);
  delay(1000);
}

void moverMotor(int motorId, int direccion, int velocidad) {
  velocidad = constrain(velocidad, 0, 255);
  int pinIN1, pinIN2, canalPWM;

  if (motorId == MOTOR_A) {
    pinIN1 = IN1; pinIN2 = IN2; canalPWM = canalA;
  } else {
    pinIN1 = IN3; pinIN2 = 
    IN4; canalPWM = canalB;
  }

  if (direccion == ADELANTE) {
    digitalWrite(pinIN1, HIGH); digitalWrite(pinIN2, LOW);
    ledcWrite(canalPWM, velocidad);
  } else if (direccion == ATRAS) {
    digitalWrite(pinIN1, LOW); digitalWrite(pinIN2, HIGH);
    ledcWrite(canalPWM, velocidad);
  } else {
    digitalWrite(pinIN1, LOW); digitalWrite(pinIN2, LOW);
    ledcWrite(canalPWM, 0);
  }
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
