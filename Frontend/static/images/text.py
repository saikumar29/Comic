import pyttsx3
import time

def run(request):
    print("Listening to sound")
    e = pyttsx3.init()
    e.say(request)
    e.runAndWait()
    time.sleep(1)
run("MY NAME IS SAIKUMAR I AM FROM NORTHEASTERN UNIVERSITY")