import socket as sck

class RobotComm:
    def __init__(self, UDP_IP, UDP_PORT, USAR_WIFI):
        self.UDP_IP = UDP_IP
        self.UDP_PORT = UDP_PORT
        self.USAR_WIFI = USAR_WIFI
    
        self.sock = sck.socket(sck.AF_INET,sck.SOCK_DGRAM)

    def enviarMensaje(self,mensaje):

        if self.USAR_WIFI and self.sock:
            try:
                self.sock.sendto(mensaje.encode('utf-8'), (self.UDP_IP,self.UDP_PORT))
            except Exception as e:
                print(f'Error al enviar el mensaje, error de red: {e}')

