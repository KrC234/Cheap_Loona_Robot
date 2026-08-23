# Cheap Robot Loona
### By: Aalan Kalid Ruíz Colín 

## Especificaciones: 
* El robot debe ser capaz de detectar emociones. 
* El robot debe reaccionar a la detección de emociones.
* El robot debe contar con autonomia.

## Desarrollo Resumido 

### Modelo de Visión Artificial 
El reconocimiento se realiza mediante un programa de python que hace uso de las librerías de OpenCV y MediaPipe. 

OpenCV recibe la señal de vídeo y permite dibujar información sobre esta. 
Media Pipe ofrece herramientas de mallado y esqueleto para objetos.

FaceShell es una herramienta que coloca puntos sobre un rostro humano. Se establecen puntos de interés en ojos, cejas, labios y en la parte superior e inferior del rostro. 

La forma de clasificar las emociones es mediante proporciones, 
### Modelo de reconocimiento de Emociones
Para la implementación se hace uso de proporciones. Se obtiene la altura del rostro mediante dos puntos. 

Entonces, en base a la altura del rostro y calculos de distancia entre puntos, se determina que tan abierta o cerrada es una expresión en base a la proporción del rostro. Y mediante umbrales establecidos de manera manual, las emociones se clasifican considerando la abertura de la boca y la contracción de ojos y cejas. (Los umbrales se establecieron de manera manual mediante un estimado obtenido por pruebas).

Para poder validar una emoción, esta debe de cumplir un nivel de estabilidad de frames, establecidos nuevamente mediante un umbral. La estabilidad es importante al momento de mandar paquetes, permitiendo que el robot pueda actuar de una manera controlada. 

### Arquitectura de comunicación

Para el desarrollo se hace uso de 3 placas de desarrollo base
+ Arduino: Manejo de display Ftp 
+ ESP32: Punto de acceso y control de motores.
+ ESP32CAM: Envio de señal de vídeo mediante Stream

```mermaid
flowchart LR
    A[PC] -- WebSockets --> B(ESP32/Access Point)
    B -- Conexión serial --> C[Arduino]
    D[ESP32 CAM] -- Web/Sockets --> A
```
#### Desarrollo 
1. Se establece una red local usando el ESP32 cómo punto de acceso. 
2. El ESP32 y el PC se conectan asignandoles una IP y una submascara de red. 
3. En la PC mediante Python se habilitan puertos web socket.
4. Uno de los puertos recibe la señal del ESP32CAM mediante Stream. 
5. El otro puerto envia datos de tipo caracter al ESP32. 
6. El ESP32 recibe el caracter, acciona y reenvia el caracter al Arduino mediante comunicación serial en modo de escritura.   

