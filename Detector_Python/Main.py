import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from CamaraStream import CamaraStream
from Detector import Detector
from RobotComm import RobotComm

class RobotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Emocional")

        # --- Variables ---
        self.streaming = False
        self.modo_remoto = False

        # --- Instancias ---
        self.cam = CamaraStream("http://192.168.4.2:80/stream")
        self.detector = Detector()
        self.comunicador = RobotComm("192.168.4.1",8080,True)
        self.ultima_emocion_enviada = None
        # --- Widgets ---
        self.video_label = tk.Label(root)
        self.video_label.pack()

        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        self.btn_start = tk.Button(control_frame, text="Iniciar Stream", command=self.iniciar_stream)
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_modo_auto = tk.Button(control_frame, text="Modo Automático", command=self.modo_automatico)
        self.btn_modo_auto.grid(row=0, column=1, padx=5)

        self.btn_modo_remoto = tk.Button(control_frame, text="Modo Remoto", command=self.modo_remoto_on)
        self.btn_modo_remoto.grid(row=0, column=2, padx=5)

        self.emocion_label = tk.Label(root, text="Emoción: Neutral", font=("Arial", 14))
        self.emocion_label.pack(pady=5)

        # Iniciar loop de actualización
        self.update_frame()

    # --- Botones ---
    def iniciar_stream(self):
        self.streaming = True

    def modo_remoto_on(self):
        self.modo_remoto = True

    def modo_automatico(self):
        self.modo_remoto = False

    # --- Loop de actualización ---
    def update_frame(self):
        if self.streaming:
            ret, frame = self.cam.grab_frame()
            if ret:
                emocion, frame = self.detector.detectarEmocion(frame)
                emocion_text = {"0": "Neutral", "1": "Feliz", "2": "Sorprendido", "3": "Enojado"}.get(str(emocion), "Desconocido")
                self.emocion_label.config(text=f"Emoción: {emocion_text}")

                # Convertir frame a ImageTk para mostrar en Tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)

                if emocion != self.ultima_emocion_enviada:
                    print(f"Cambio detectado: {emocion} -> Enviando al robot...")
                
                # --- AQUÍ USAMOS TU CLASE ---
                    self.comunicador.enviarMensaje(emocion)
                
                # Actualizamos la variable de control
                    self.ultima_emocion_enviada = emocion

        # Llamar a sí mismo después de 30 ms
        self.root.after(30, self.update_frame)

# --- Ejecutar GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    gui = RobotGUI(root)
    root.mainloop()
