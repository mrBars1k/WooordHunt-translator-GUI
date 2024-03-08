import requests
from bs4 import BeautifulSoup
import urllib3

from tkinter import *
from tkinter import ttk
import psycopg2
from psycopg2 import sql
from tk import *

## ## ## ## ## ## ## ##

adb = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port)

cur = adb.cursor()

## ## ## ## ## ## ## ##

cur.execute("""CREATE TABLE IF NOT EXISTS translations (
    id bigserial PRIMARY KEY,
    eng varchar(400) NOT NULL UNIQUE,
    transcription varchar(400) NOT NULL UNIQUE,
    ru varchar(400) NOT NULL UNIQUE,
    date timestamp DEFAULT CURRENT_TIMESTAMP(1) NOT NULL
);""")
adb.commit()

## ## ## ## ## ## ## ##

def take_word(word):
    url = requests.get(f"https://wooordhunt.ru/word/{word}", verify=False)
    resp_check = url.text
    soup = BeautifulSoup(resp_check, "html.parser")
    try:
        translate = soup.find("div", class_="t_inline_en").text
        transcript = soup.find(
            "span",
            class_="transcription",
            title=f"британская транскрипция слова {word}",
        ).text
        return f"{word}{transcript} {translate}"
    except:
        return word

## ## ## ## ## ## ## ##

mainw = Tk() ## main window;
mainw.title("WOORDHUNT") ## headline;
mainw.geometry("1920x1080") ## resolution;
mainw.wm_minsize(1280, 720)  ## min width and hight;
mainw.wm_maxsize(1920, 1080)  ## max width and hight;

## ## ## ## ## ## ## ##

word_to_translate = Entry(mainw, width=40, font=("Arial", 18))
word_to_translate.place(x=50, y=50)

def translate():
    need = word_to_translate.get()

    cur.execute("")

trans_btn = Button(mainw, text="GO", width=10, command=translate)
trans_btn.place(x=100, y=100)


## ## ## ## ## ## ## ##
mainw.mainloop()
cur.close()
adb.close()