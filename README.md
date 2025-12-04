# Cheap Robot Loona
### By: Aalan Kalid Ruíz Colín 

## Especifiaciones: 
* El robot debe ser capaz de detectar emociones. 
* El robot debe de reaccionar a las emociones detectadas.
* El robot debe contar con autonomia.

## Funcionamiento

Se establece una comunicación entre 3 microcontroladores:
+ Arduino 
+ ESP32 (NODE MCU 32S)
+ ESP32CAM

El ESP32 funciona cómo controlador principal, se le otorgan credenciales necesarias para poder generar un punto de acceso, este punto de acceso se comunica con un PC, el cual se encarga del procesamiento en bruto, el PC recibe una señal de video mediante puertos, por parte del ESP32 CAM. 
Una vez obtenida la imagen, se procesa para obtener una detección de emociones, la emoción detectada se manda mediante socket de regreso al ESP32 principal, quien coordina los motores, además de comunicar el arduino en Serie, quien despliega la imagen en el display. 

