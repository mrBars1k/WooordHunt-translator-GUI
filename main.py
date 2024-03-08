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



## ## ## ## ## ## ## ##
mainw.mainloop()
cur.close()
adb.close()