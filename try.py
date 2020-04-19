import sys
from model import api_call
from mysql.connector import MySQLConnection
from mysql.connector.errors import Error
import speech_recognition as sr
from io import BytesIO
import time
from PIL import Image
import pygame
from gtts import gTTS
from obj_detection import object_detection
from datetime import date
import re
#from get_user_info import get_user_id


def listen_to_blind():
    mic=sr.Microphone()
    r=sr.Recognizer()
    with mic as source:
        time.sleep(1)
        send_the_message('speak now')
        r.adjust_for_ambient_noise(source)
        audio=r.listen(source)
    try:
        voice_text=r.recognize_google(audio)
        return voice_text
    except sr.UnknownValueError:
        print("Google Speech Recognition couldn't recognize")
        retyed_voice=retry_listening()
        # if retyed_voice is None:
        #     sys.exit()
        # return retyed_voice
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        sys.exit()

def retry_listening():
    mic=sr.Microphone()
    r=sr.Recognizer()
    with mic as source:
        time.sleep(1)
        send_the_message('can you speak again')
        r.adjust_for_ambient_noise(source)
        audio=r.listen(source)
    try:
        voice_text=r.recognize_google(audio)
        return voice_text
    except sr.UnknownValueError:
        print("Sorry, Google speech Recognition could not understand audio")
        send_the_message("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return None

def ask_the_request(request):
    with BytesIO() as f:
        gTTS(request, lang='en-UK').write_to_fp(f)
        f.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(f)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
    voice_text=listen_to_blind()
    if voice_text is not None:
        return voice_text
    else:
        sys.exit()

def send_the_message(request):
    with BytesIO() as f:
        gTTS(request, lang='en').write_to_fp(f)
        f.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(f)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

def extract_chapter_id(text):
    chapter_id=None
    text=text.lower()
    if bool(text.strip())==False:
        chapter_id=None
    elif "chapter" in text:
        text_list=text.lower().split('chapter')
        for i in range(1,len(text_list)):
            for j in range(0,len(text_list[i].split())):
                try:
                    chapter_id=int(text_list[i].split()[j].strip())
                except ValueError:
                    pass
    elif len(text)<3 and bool(text.strip())!=False:
        chapter_id=text.strip()
    return chapter_id


listen_to_user_comments =ask_the_request("Would you like to listen to User comments on same chapter or different, if yes please say yes or say no else say bye")
print(listen_to_user_comments)

if bool('b' in listen_to_user_comments.lower()) == True:
    send_the_message("Thanks for using comic world I hope you like it")
    sys.exit()