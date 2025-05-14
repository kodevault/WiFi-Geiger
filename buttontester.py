import RPi.GPIO as GPIO
import time

#> GLOBALS | Asignacion de pines | Definicion de botones y buzzer <#

BOTON_START = 17
BOTON_STOP = 27
BUZZER = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(BOTON_START, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BOTON_STOP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZZER, GPIO.OUT)

#> FUNCIONES <# #> FUNCIONES <# #> FUNCIONES <# #> FUNCIONES <# #> FUNCIONES <# #> FUNCIONES <# #> FUNCIONES <#

def BEEP(tiempo=0.5):
    print("Sonando")   
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(tiempo)
    GPIO.output(BUZZER, GPIO.LOW)
    print("Silencio")

def START(channel):
    print("START")
    BEEP()
    print("En espera")

def STOP(channel):
    print("STOP")
    BEEP()
    print("En espera")

#> BOTONES
GPIO.add_event_detect(BOTON_START, GPIO.RISING, callback=START, bouncetime=300)
GPIO.add_event_detect(BOTON_STOP, GPIO.RISING, callback=STOP, bouncetime=300)

#> MAIN
print("Inicio.")
print("En espera")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()