import RPi.GPIO as GPIO
import subprocess
import time
import threading

#> GLOBALS | Asignacion de pines | Definicion de botones y buzzer <#

SSID_objetivo = None
Beeping = False

BOTON_START = 17
BOTON_STOP = 27
BUZZER = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(BOTON_START, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BOTON_STOP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZZER, GPIO.OUT)

#> FUNCIONES <# #> FUNCIONES <# #> FUNCIONES <# #> FUNCIONES <# #> FUNCIONES <# #> FUNCIONES <# #> FUNCIONES <#

def escanear_redes():
#   Escanea las redes y devuelve un diccionario con todos los SSID encontrados
    salida = subprocess.check_output(["iwlist", "wlan0", "scan"]).decode()
    redes = []
    ssid = ""
    print("Escaneando redes...")
    for linea in salida.split("\n"):
        linea = linea.strip()
        if "ESSID" in linea:
            ssid = linea.split(":")[1].strip('"')
        if "Signal level" in linea:
            intensidad = int(linea.split("Signal level=")[1].split(" ")[0])
            redes.append((ssid, intensidad))
    return redes

def medir_intensidad(SSID_objetivo):
#   Devuelve la intensidad de la señal de una red wifi concreta
    salida = subprocess.check_output(["iwconfig", "wlan0"]).decode()
    if SSID_objetivo in salida:
        for linea in salida.split("\n"):
            if "Signal level" in linea:
                intensidad = int(linea.split("Signal level=")[1].split(" ")[0])
                return intensidad
    return None

def geiger():
#   Activa el buzzer en base a la intensidad de la señal que se esta monitorizando
    global Beeping
    while Beeping:
        intensidad = medir_intensidad(SSID_objetivo)
        if intensidad is not None:
            duracion = max(0.1, 5 - abs(intensidad) / 10)
            GPIO.output(BUZZER, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(BUZZER, GPIO.LOW)
            time.sleep(duracion)
        else:
            time.sleep(1)

def START(channel):
#   Invoca el escaneo de redes y fija como objetivo la señal mas fuerte
#   Invoca el contador geiger

    global SSID_objetivo, Beeping
    print("START")
    redes = escanear_redes()
    if redes:
        SSID_objetivo = max(redes, key=lambda x: x[1])[0]
        print("Objetivo fijado:", SSID_objetivo)
        Beeping = True
        threading.Thread(target=geiger, daemon=True).start()

def STOP(channel):
#   Detiene el escaneo en curso y libera las variables para comenzar de nuevo
    global SSID_objetivo, Beeping
    print("STOP")
    Beeping = False
    SSID_objetivo = None
    GPIO.output(BUZZER, GPIO.LOW)

#> BOTONES
GPIO.add_event_detect(BOTON_START, GPIO.RISING, callback=START, bouncetime=300)
GPIO.add_event_detect(BOTON_STOP, GPIO.RISING, callback=STOP, bouncetime=300)

#> MAIN
print("Wi-Fi Geiger")
print("Pitando durante 1 segundo para indicar arranque completo.")
GPIO.output(BUZZER, GPIO.HIGH); time.sleep(1); GPIO.output(BUZZER, GPIO.LOW)
print("Esperando instrucciones...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt: # Ctrl+C to exit
    GPIO.cleanup()