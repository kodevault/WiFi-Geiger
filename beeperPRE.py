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
#   Escanea las redes y devuelve los SSID encontrados y la intensidad de la señal
    salida = subprocess.check_output(["iwlist", "wlan0", "scan"]).decode()
    redes = []
    SSID = ""
    
    print("Escaneando redes...")
    for linea in salida.split("\n"):
        linea = linea.strip()
        if "ESSID" in linea:
            SSID = linea.split(":")[1].strip('"')
        if "Signal level" in linea:
            intensidad = int(linea.split("Signal level=")[1].split(" ")[0])
            redes.append((SSID, intensidad))
    return redes

def medir_intensidad(redes, SSID_objetivo):
#   Devuelve la intensidad de la señal de una red wifi concreta
    for ssid, intensidad in redes:
        if ssid == SSID_objetivo:
            return intensidad
    return None

def geiger():
#   Activa el buzzer en base a la intensidad de la señal que se esta monitorizando
    global Beeping
    while Beeping:
        redes = escanear_redes()
        intensidad = medir_intensidad(redes, SSID_objetivo)
        if intensidad is not None:
            duracion = max(0.1, 5 - abs(intensidad) / 10)
            GPIO.output(BUZZER, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(BUZZER, GPIO.LOW)
            time.sleep(duracion)
        else:
            print("Sin señal...")
            time.sleep(1)

def START(channel):
#   Invoca el escaneo de redes y fija como objetivo la señal mas fuerte
#   Invoca el contador geiger

    global SSID_objetivo, Beeping
    print("START")
    if not Beeping:
        redes = escanear_redes()
        if redes:
            SSID_objetivo = max(redes, key=lambda x: x[1])[0]
            print("Objetivo fijado:", SSID_objetivo)
            Beeping = True  # Iniciar el proceso de geiger
            threading.Thread(target=geiger, daemon=True).start()
        else:
            print("ERROR: No se encontraron redes.")
    else:
        print("Ya hay un escaneo en curso...")   
        
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