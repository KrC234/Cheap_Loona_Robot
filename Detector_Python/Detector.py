import mediapipe as mp
import math as m
import cv2

# Definiciones clave
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

# --- umbrales ---
UMBRAL_BOCA_ABIERTA_SORPRESA = 0.1  # Boca muy abierta
UMBRAL_BOCA_ABIERTA_FELIZ = 0.070   # Boca un poco abierta (sonrisa)
UMBRAL_BOCA_ANCHO_FELIZ = 0.250     # Sonrisa ancha
UMBRAL_CEJA_LEVANTADA = 0.055       # Cejas arriba (Sorpresa)
UMBRAL_CEJA_FRUNCIDA = 0.110        # Cejas abajo (Enojo)

class Detector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

        self.emocion_confirmada = '0'
        self.posible_nueva_emocion = '0'
        self.contador_estabilidad = 0
        self.META_ESTABILIDAD = 5

    @staticmethod
    def calcularDistancia(p1, p2):
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        return m.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def estabilizarEmocion(self, nueva_emocion):
        # Si la emoción detectada es igual a la posible nueva emoción, aumentamos contador
        if nueva_emocion == self.posible_nueva_emocion:
            self.contador_estabilidad += 1
        else:
            # Si cambia, reseteamos el contador y cambiamos la "posible"
            self.posible_nueva_emocion = nueva_emocion
            self.contador_estabilidad = 0
        
        # Si el contador llega a la meta, confirmamos el cambio de emoción
        if self.contador_estabilidad >= self.META_ESTABILIDAD:
            if self.emocion_confirmada != self.posible_nueva_emocion:
                self.emocion_confirmada = self.posible_nueva_emocion
                
        return self.emocion_confirmada

    def detectarEmocion(self, frame):
        # MediaPipe necesita RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        
        # Opcional: Si quieres dibujar sobre la imagen original
        # frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR) 

        # Por defecto asumimos '0' (Neutral) si no se detecta nada
        emocion_detectada_ahora = '0'

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # Dibujamos la malla facial
            self.mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.drawing_spec)
        
            # --- CÁLCULOS (Solo si hay cara) ---
            landmarks = face_landmarks.landmark

            dist_cara_alto = self.calcularDistancia(landmarks[P_FRENTE_TOP], landmarks[P_BARBILLA_BOT])
            
            # Evitamos división por cero si la cara está muy lejos o error de lectura
            if dist_cara_alto == 0: 
                dist_cara_alto = 1 

            dist_boca_apertura = self.calcularDistancia(landmarks[P_LABIO_SUP_INT], landmarks[P_LABIO_INF_INT])
            dist_boca_ancho = self.calcularDistancia(landmarks[P_COMISURA_IZQ], landmarks[P_COMISURA_DER])

            dist_ceja_izq = self.calcularDistancia(landmarks[P_CEJA_IZQ_MID], landmarks[P_OJO_IZQ_TOP])
            dist_ceja_der = self.calcularDistancia(landmarks[P_CEJA_DER_MID], landmarks[P_OJO_DER_TOP])

            dist_cejas_promedio = (dist_ceja_izq + dist_ceja_der) / 2

            # Calculo de proporciones (Ratios)
            ratio_boca_apertura = dist_boca_apertura / dist_cara_alto
            ratio_boca_ancho = dist_boca_ancho / dist_cara_alto
            ratio_cejas_altura = dist_cejas_promedio / dist_cara_alto

            # Clasificamos la emoción actual
            emocion_detectada_ahora = self.clasificarEmocion(ratio_boca_apertura, ratio_boca_ancho, ratio_cejas_altura)

        # Retornamos la emoción estabilizada y el frame dibujado
        return self.estabilizarEmocion(emocion_detectada_ahora), frame
    
    def clasificarEmocion(self, ratio_boca_apertura, ratio_boca_ancho, ratio_cejas_altura):
        # CASO: SORPRESA ('2')
        if (ratio_boca_apertura > UMBRAL_BOCA_ABIERTA_SORPRESA and 
            ratio_cejas_altura > UMBRAL_CEJA_LEVANTADA):
            return '2'

        # CASO: ENOJADO ('3') (Cejas muy bajas/fruncidas)
        # Nota: Asegúrate que tus umbrales estén calibrados, a veces 'menor que' funciona mejor aquí.
        elif (ratio_cejas_altura < UMBRAL_CEJA_FRUNCIDA and 
              ratio_boca_apertura < UMBRAL_BOCA_ABIERTA_FELIZ):
            return '3'
                
        # CASO: FELIZ ('1') (Boca ancha + un poco abierta)
        elif (ratio_boca_ancho > UMBRAL_BOCA_ANCHO_FELIZ):
            return '1'
        
        # CASO: NEUTRAL ('0') - Si no es ninguna de las anteriores
        else:
            return '0'