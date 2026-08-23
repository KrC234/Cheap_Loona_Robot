import cv2
import mediapipe as mp
import numpy as np
import math
import serial
import socket 
import urllib.request

'''
    El ESP32 genera un punto de acceso, por lo que se conecta mediante Socket
'''
# --- CONFIGURACION POR SOCKET ---
UDP_IP = "192.168.4.1"
UDP_PORT = 8080

USAR_WIFI = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- CONFIGURACIÓN MEDIAPIPE ---
'''
    Generar face_mesh de MediaPipe
    Se establecen proporciones en relación de la cara para determinar la emoción
'''
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True, 
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# --- ÍNDICES DE PUNTOS CLAVE (Landmarks) ---
P_FRENTE_TOP = 10
P_BARBILLA_BOT = 152
P_LABIO_SUP_INT = 13
P_LABIO_INF_INT = 14
P_COMISURA_IZQ = 61
P_COMISURA_DER = 291
P_CEJA_IZQ_MID = 105
P_CEJA_DER_MID = 334
P_OJO_IZQ_TOP = 159
P_OJO_IZQ_BOT = 145
P_OJO_DER_TOP = 386
P_OJO_DER_BOT = 374

# --- UMBRALES DE CALIBRACIÓN ---
UMBRAL_BOCA_ABIERTA_SORPRESA = 0.1 # Boca muy abierta
UMBRAL_BOCA_ABIERTA_FELIZ = 0.070   # Boca un poco abierta (sonrisa)
UMBRAL_BOCA_ANCHO_FELIZ = 0.250     # Sonrisa ancha
UMBRAL_CEJA_LEVANTADA = 0.055       # Cejas arriba (Sorpresa)
UMBRAL_CEJA_FRUNCIDA = 0.110        # Cejas abajo (Enojo)

# --- VARIABLES PARA EL FILTRO DE ESTABILIDAD ---
emocion_confirmada = '0' # '0' es Neutral
posible_nueva_emocion = '0'
contador_estabilidad = 0
META_ESTABILIDAD = 5  # Número de frames seguidos para confirmar (ajustar velocidad vs estabilidad)

# Diccionario para mostrar texto en pantalla
diccionario_emociones = {
    '0': "Neutral",
    '1': "Feliz",
    '2': "Sorprendido",
    '3': "Enojado"
}


# --- FUNCIÓN AUXILIAR: Calcular distancia Euclidiana ---
def calcular_distancia(p1, p2):
    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# --- FUNCIÓN PRINCIPAL DE ENVÍO POR SOCKET ---
def procesar_y_enviar_emocion(nueva_emocion_detectada):
    global emocion_confirmada, posible_nueva_emocion, contador_estabilidad
    
    # Establizar emoción
    if nueva_emocion_detectada == posible_nueva_emocion:
        contador_estabilidad += 1
    else:
        posible_nueva_emocion = nueva_emocion_detectada
        contador_estabilidad = 0
        
    # Emoción Detectada
    if contador_estabilidad >= META_ESTABILIDAD:
        # Validar Cambio de Emoción
        if emocion_confirmada != posible_nueva_emocion:
            emocion_confirmada = posible_nueva_emocion

            # Mandar Mensaje al ESP32
            if USAR_WIFI:
                try:
                    mensaje = emocion_confirmada

                    sock.sendto(mensaje.encode('utf-8'), (UDP_IP,UDP_PORT))
                except Exception as e:
                    print(f"Error de red: {e}")

            else:
                print('Emocion detectada sin red')

# --- BUCLE PRINCIPAL ---
url = "http://192.168.4.2:80/stream"
cap = cv2.VideoCapture(url) 
if not cap.isOpened():
    print("No se pudo obtener la imagen")
    exit()

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # Espejo y conversión de color
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    
    # Procesamiento de MediaPipe
    results = face_mesh.process(image_rgb)
    image.flags.writeable = True
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    emocion_actual_frame = '0' # Por defecto Neutral

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Dibujar la malla facial (opcional, puedes comentarlo)
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=drawing_spec)

            # --- CALCULAR DISTANCIAS CLAVE ---
            landmarks = face_landmarks.landmark
            
            # Referencia Vertical (Altura de la cara para normalizar)
            dist_cara_alto = calcular_distancia(landmarks[P_FRENTE_TOP], landmarks[P_BARBILLA_BOT])
            
            # Evitar división por cero si no detecta bien la cara
            if dist_cara_alto < 0.01: continue 

            # Distancias de rasgos
            dist_boca_apertura = calcular_distancia(landmarks[P_LABIO_SUP_INT], landmarks[P_LABIO_INF_INT])
            dist_boca_ancho = calcular_distancia(landmarks[P_COMISURA_IZQ], landmarks[P_COMISURA_DER])
            
            # Promedio de altura de cejas respecto a los ojos
            dist_ceja_izq = calcular_distancia(landmarks[P_CEJA_IZQ_MID], landmarks[P_OJO_IZQ_TOP])
            dist_ceja_der = calcular_distancia(landmarks[P_CEJA_DER_MID], landmarks[P_OJO_DER_TOP])
            dist_cejas_promedio = (dist_ceja_izq + dist_ceja_der) / 2

            # --- CALCULAR PROPORCIONES (Normalización) ---
            ratio_boca_apertura = dist_boca_apertura / dist_cara_alto
            ratio_boca_ancho = dist_boca_ancho / dist_cara_alto
            ratio_cejas_altura = dist_cejas_promedio / dist_cara_alto

            # --- Calibración de Umbrales ---
            #print(f"BocaAbierta: {ratio_boca_apertura:.3f} | BocaAncho: {ratio_boca_ancho:.3f} | Cejas: {ratio_cejas_altura:.3f}")

            # --- IDENTIFICACIÓN DE LAS EMOCIONES ---
            
            # CASO: SORPRESA (Boca muy abierta + Cejas levantadas)
            if (ratio_boca_apertura > UMBRAL_BOCA_ABIERTA_SORPRESA and 
                ratio_cejas_altura > UMBRAL_CEJA_LEVANTADA):
                emocion_actual_frame = '2'

            # CASO: ENOJADO (Cejas muy bajas/fruncidas)
            elif (ratio_cejas_altura < UMBRAL_CEJA_FRUNCIDA and 
                  ratio_boca_apertura < UMBRAL_BOCA_ABIERTA_FELIZ):
                emocion_actual_frame = '3'
                
            # CASO: FELIZ (Boca ancha + un poco abierta)
            elif (ratio_boca_ancho > UMBRAL_BOCA_ANCHO_FELIZ ):
                emocion_actual_frame = '1'

            # --- ENVIO DE EMOCIÓN ---
            procesar_y_enviar_emocion(emocion_actual_frame)

    # Mostrar la emoción confirmada en pantalla
    txt_mostrar = diccionario_emociones.get(emocion_confirmada, "Desconocido")
    
    # Cambiar color del texto según la emoción
    color_texto = (255, 255, 255) # Blanco neutro
    if emocion_confirmada == '1': color_texto = (0, 255, 0) # Verde feliz
    elif emocion_confirmada == '2': color_texto = (0, 255, 255) # Amarillo sorpresa
    elif emocion_confirmada == '3': color_texto = (0, 0, 255) # Rojo enojo

    cv2.putText(image, f"Emocion Robot: {txt_mostrar}", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, color_texto, 2, cv2.LINE_AA)
    
    # Barra de estabilidad (visualización del filtro)
    ancho_barra = int((contador_estabilidad / META_ESTABILIDAD) * 200)
    cv2.rectangle(image, (50, 70), (50 + ancho_barra, 80), color_texto, -1)

    cv2.imshow('Detector de Emociones Geometrico', image)
    if cv2.waitKey(5) & 0xFF == 27: # Salir con ESC
        break

cap.release()
if sock:
    sock.close()
cv2.destroyAllWindows()