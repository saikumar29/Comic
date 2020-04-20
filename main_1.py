import sys
from model import api_call
from mysql.connector import MySQLConnection
from mysql.connector.errors import Error
import speech_recognition as sr
from obj_detection import object_dectection
import os
from io import BytesIO
import time
from PIL import Image
import datetime
import pyttsx3
from IPython.display import Audio
import pygame
from tempfile import TemporaryFile
from gtts import gTTS
from datetime import date

def listen_to_blind():
    mic=sr.Microphone()
    r=sr.Recognizer()
    with mic as source:
        time.sleep(1)
        send_the_message('start speaking at Microphone')
        r.adjust_for_ambient_noise(source)
        audio=r.listen(source)
    try:
        voice_text=r.recognize_google(audio)
        return voice_text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        retry_voice=retry_listening()
        if retry_voice is None:
            sys.exit()
        return retry_voice
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        sys.exit()

def retry_listening():
    mic=sr.Microphone()
    r=sr.Recognizer()
    with mic as source:
        send_the_message('can you speak once again')
        audio=r.listen(source)
    try:
        voice_text=r.recognize_google(audio)
        return voice_text
    except sr.UnknownValueError:
        print("Sorry, Google speech Recognition could not understand audio")
        send_the_message("Sorry,Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return None

def ask_the_request(request):
    s = time.time()
    with BytesIO() as f:
        gTTS(request, lang='en').write_to_fp(f)
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
        sys.exit(0)

def send_the_message(request):
    with BytesIO() as f:
        gTTS(request, lang='en').write_to_fp(f)
        f.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(f)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

### converting byte array to image

def byte_array_to_image(byte_image):
    file = BytesIO()
    file.write(byte_image)
    file.seek(0)
    img = Image.open(file)
    return img

#check the text
def preprocess(text,check):
    text=text.lower()
    if str(check) in str(text):
        return True

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

def generate_objects(obj_lis):
    objects=''
    obj_dict=obj_lis[0]
    for keys,val in obj_lis.items():
        val=str(val.decode('utf-8'))
        objects=objects+' '+val
    return objects

def get_user_id(name,phone_number):
    try:
            connector = MySQLConnection(user='root', password='Pooja@143',
                                        host='127.0.0.1',
                                        database="project")
            cursor = connector.cursor()
    except Error as e:
            print("connection error {}".format(e))
            sys.exit("unable to connect to db")
    try:
        # check the values in the database
        insert_values=(str(name.split()[0]),str(name.split()[1]),phone_number)
        insert_command = "SELECT user_id FROM user WHERE (user_first_name=%s and user_last_name=%s and user_phone_number=%s)"
        cursor.execute(insert_command, insert_values)
        connector.commit()
        user_id=cursor.fetchone()[0]
        return user_id
    except:
        print("cannot find user ID sorry cannot enter the  Comments")
        return None

#start of the main application
class start_application():
     def __init__(self):
        #self.id=ask_the_request('Enter your username')
        self.welcome=send_the_message('Welcome to Comic World')
        # mice should be activated.
        self.comment = False
        self.reponse=ask_the_request("Would to like to listen to Comics If so say Yes or say no")
        user_intial_reponse=preprocess(self.reponse,'no')
        if bool(user_intial_reponse)==True:
            send_the_message('Okay we are closing application now ')
            sys.exit(0)
        else:
            self.first_name=ask_the_request('Please tell your first name')
            self.last_name=ask_the_request("Please tell your Last nane")
            self.name=self.first_name + " "+self.last_name
            self.phone_number=ask_the_request("Please tell your phone number")
            self.chapter=ask_the_request("Please tell the chapter ID you want to listen")
            self.chapter_id=extract_chapter_id(self.chapter)
            if self.chapter_id is None:
                  send_the_message("we didn't recieve Chapter ID")
                  self.chapter=ask_the_request("Please mention again proper Chaper Id you want to listen at Microphone")
                  self.chapter_id=extract_chapter_id(self.chapter)

     def store_user_information_db(self):
        try:
            connector = MySQLConnection(user='root', password='Pooja@143',
                                        host='127.0.0.1',
                                        database="project")
            cursor = connector.cursor()
        except Error as e:
            print("connection error {}".format(e))
            sys.exit("unable to connect to db")
        try:
            insert_values = (self.first_name, self.last_name,self.phone_number)
            #check the values in the database
            insert_command = "INSERT INTO user_info(user_first_name, user_last_name,user_phone_number VALUES(%s,%s,%s)"
            result = cursor.execute(insert_command, insert_values)
            connector.commit()
        except:
            print("cannot insert user information into DB")

# ask the user A which date he want to know about the comic
class ask_data_to_user(start_application):
    def __init__(self,ClassA):
        self.chapter_id=ClassA.chapter_id
        self.name=ClassA.name
        self.phone_number=ClassA.phone_number

    def process_to_model(self):
        connector = MySQLConnection(user='root', password='Pooja@143', host='127.0.0.1', database='project')
        self.cx = connector.cursor()
        # need to change to the date format need to verify this
        query_fetch_raw_image_id="SELECT img_id FROM raw_image WHERE img_id=%s"
        chapter=(self.chapter_id,)
        self.cx.execute(query_fetch_raw_image_id,chapter)
        img_id=self.cx.fetchone()[0]
        for i in range(1,4):
            query_fetch_split_images="SELECT image FROM split_images WHERE img_id={} and img_no={}".format(img_id,i)
            self.cx.execute(query_fetch_split_images)
            image=self.cx.fetchone()[0]

            #  send img to api
            bubble_text=api_call.api_call(image)
            txt_from_bubble=bubble_text.detect_text()
            # preprocess the Bubble _text properly
            # if txt_from_bubble is None:
            #     # Run to image_captioning model
            # else:
            obj_detection=object_dectection(image)
            image_objects=obj_detection.run_model()
            objects = generate_objects(image_objects)


                # preprocess the Bubble _text properly
                # run the object dection model
#text-voice output to user

            send_the_message("we have " +str(objects) +" in the current scene ")
            send_the_message("they are speaking like this " +str(txt_from_bubble))

        # ask the user to review on comic on the particular date
        self.comment_on_comic=ask_the_request("Would you like to comment on this chapters if yes say Yes else NO")
        comment_reponse=preprocess(self.comment_on_comic,'yes')
        if bool(comment_reponse) ==True:
            comment=ask_the_request("Please mention your comment now")
            user_id=get_user_id(self.name,self.phone_number)
            self.store_the_comment(user_id,self.chapter_id,comment)

        # listem to comment
        self.listen_to_user_comments=ask_the_request("Would you like to listen to User comments on same chapter or different is same say yes else no")
        listen_comments_reponse=preprocess(self.listen_to_user_comments,'yes')
        if bool(listen_comments_reponse)==True:
            stored_comments=self.fetch_comments(self.chapter_id)
        else:
            chapter_number=ask_the_request("Mention the Chapter Number")
            chapter=preprocess(chapter_number)
            store_comments=self.fetch_comments(chapter)

        # ask again user to continue the series
        request_for_continution=ask_the_request("would you like to countinue the series if yes say yes else no")
        continution_response=preprocess(request_for_continution,"yes")
        if bool(continution_response)==True:
            self.chapter_id=int(self.chapter_id)+1
            self.process_to_model()
        else:
            send_the_message("Thanks for using the Comic World I hope you like our experience")
            sys.exit()

    def store_the_comment(self,user_id,chapter_id,comment):
        self.user_id=user_id
        self.chapter_id=chapter_id
        self.comment=comment
        self.comment_date=str(date.today())
        try:
            connector = MySQLConnection(user='root', password='Pooja@143',
                                        host='127.0.0.1',
                                        database="project")
            cursor = connector.cursor()
        except Error as e:
            print("connection error {}".format(e))
            sys.exit("unable to connect to db")
        try:
            insert_values = (self.user_id, self.chapter_id,self,comment,self.comment_date)
            # check the values in the database
            insert_command = "INSERT INTO chapter_comments(user_id,chapter_id,user_comment,comment_date) VALUES(%s,%s,%s,%s)"
            result = cursor.execute(insert_command, insert_values)
            connector.commit()
        except:
            print("cannot insert user information into DB")

    def fetch_comments(self,chapter_id):
        self.chapter_id=chapter_id
        try:
            connector = MySQLConnection(user='root', password='Pooja@143',
                                        host='127.0.0.1',
                                        database="project")
            cursor = connector.cursor()
        except Error as e:
            print("connection error {}".format(e))
            sys.exit("unable to connect to db")
        try:
            # check the values in the database
            insert_values=(self.chapter_id)
            insert_command = "SELECT comments FROM chapter_comments WHERE chapter_id={}"
            cursor.execute(insert_command, insert_values)
            comments=cursor.fetchone()
## seprate test
            for i in comments:
                send_the_message(i)
            connector.commit()
        except:
            print("cannot insert user information into DB")







