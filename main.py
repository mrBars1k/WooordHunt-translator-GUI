import requests
from bs4 import BeautifulSoup
import urllib3

from tkinter import *
from tkinter import ttk
import psycopg2
from psycopg2 import sql
from tk import *

## ## ## ## ## ## ## ##
urllib3.disable_warnings()

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

mainw = Tk() ## main window;
mainw.title("WOORDHUNT") ## headline;
mainw.geometry("1920x1080") ## resolution;
mainw.wm_minsize(1280, 720)  ## min width and hight;
mainw.wm_maxsize(1920, 1080)  ## max width and hight;

## ## ## ## ## ## ## ##

word_to_translate = Entry(mainw, width=40, font=("Arial", 18))
word_to_translate.place(x=50, y=50)

## ## ## ## ## ## ## ##

tree = ttk.Treeview(mainw, columns=("ID", "English", "Transcription", "Russian"))
tree.column("#0", width=0, anchor="center")
tree.column("#1", width=10, anchor="center")
tree.column("#2", width=150, anchor="center")
tree.column("#3", width=150, anchor="center")
tree.column("#4", width=800, anchor="center")

## ## ## ##

tree.heading("#1", text="ID")
tree.heading("#2", text="English")
tree.heading("#3", text="Transcription")
tree.heading("#4", text="Russian")

tree.place(x=650, y=50, height=780, width=1200)

## ## ## ## ## ## ## ##

def take_word(event=None):
    word = word_to_translate.get().strip() ## word to translate;
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

        cur.execute(f"""INSERT INTO translations (eng, transcription, ru) VALUES (
                        '{word}', 
                        '{transcript.replace('|', '[', 1).replace('|', ']', 1)}', 
                        '{translate}'
                    )""")
        adb.commit()
        word_to_translate.delete(0, END) ## clear field;
        update_table()
        print("Перевод успешно добавлен!")
    except:
        update_table()
        adb.rollback()
        print("Слово не найдено!")

## ## ## ## ## ## ## ##

def delete():
    item = tree.selection()[0]
    id_text = tree.item(item, "values")[1]

    cur.execute(f"DELETE FROM translations WHERE eng = '{id_text}'")
    adb.commit()
    update_table()

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

context_menu = Menu(mainw, tearoff=0)
context_menu.add_command(label="Удалить", command=delete)
## ## ## ## ## ## ## ##

def update_table():
    cur.execute("SELECT eng, transcription, ru FROM translations;")
    all_info = cur.fetchall()
    count = 1
    for i in range(len(all_info)):
        all_info[i] = (count,) + all_info[i]
        count += 1

    for i in tree.get_children():
        tree.delete(i)

    for j in all_info:
        tree.insert("", "end", values=j)

word_to_translate.bind("<Return>", take_word)
tree.bind("<Button-3>", show_context_menu)
## ## ## ## ## ## ## ##
update_table()
mainw.mainloop()
cur.close()
adb.close()