#include <Arduino.h>
#include <MCUFRIEND_kbv.h>

MCUFRIEND_kbv tft;

// Variables globales
char emocionDetec = ' ';
char ultimaEmocion =' ';

// --- Definición de Colores ---
#define NEGRO   0x0000
#define AZUL    0x001F
#define ROJO    0xF800
#define VERDE   0x07E0
#define AMARILLO 0xFFE0
#define BLANCO  0xFFFF


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  ultimaEmocion = '0';

  // Inicialización de la pantalla 
  uint16_t ID = tft.readID();
  if (ID == 0xD3D3) ID = 0x9486; 
  tft.begin(ID);
  tft.setRotation(1);

  tft.fillScreen(NEGRO);
}

/*
  Figuras cómo el rectangulo y rectangulo redondeado se dibujan
  desde la esquina superior izquierda hacía abajo

  Se implementan funciones que facilitan su posicionamiento
*/

void centrarElipseHueca(int cx, int cy, int w, int h, uint16_t color){
  int x = cx - (w/2);
  int y = cy - (h/2);

  // calcula el radio optimo para la elipse
  int r = min(w,h) / 2;
  tft.drawRoundRect(x,y,w,h,r,color);
}

void centrarElipseRellena(int cx, int cy, int w, int h, uint16_t color){
  int x = cx - (w/2);
  int y = cy - (h/2);

  int r = min(w,h) / 2;
  tft.fillRoundRect(x,y,w,h,r,color);
}

void centrarRectangulo(int cx, int cy, int w, int h, uint16_t color){
  int x = cx - (w/2);
  int y = cy - (h/2);

  tft.fillRect(x,y,w,h,color);
}

void loop() {
  if(Serial.available() > 0){
    emocionDetec = Serial.read();

    switch(emocionDetec){
      
    }
  }
}
