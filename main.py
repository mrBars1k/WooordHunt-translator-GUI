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

## ##

cur.execute("""CREATE TABLE IF NOT EXISTS basket (
                eng varchar(400),
                transcription varchar(400),
                ru varchar(400)
                );""")
adb.commit()

## ## ## ## ## ## ## ##

mainw = Tk() ## main window;
mainw.title("WOOORDHUNT") ## headline;
mainw.geometry("1920x1080") ## resolution;
mainw.wm_minsize(1280, 720)  ## min width and hight;
mainw.wm_maxsize(1910, 1080)  ## max width and hight;

## ## ## ## ## ## ## ##
word_to_translate_lbl = Label(mainw, text="Добавить слово:", font=("Arial", 14))
word_to_translate_lbl.place(x=50, y=20)

word_to_translate = Entry(mainw, width=40, font=("Arial", 18))
word_to_translate.place(x=50, y=50)

word_to_translate.focus_set()

## ## ## ## ## ## ## ##
search_lbl = Label(mainw, text="Поиск слова:", font=("Arial", 14))
search_lbl.place(x=650, y=10)

search_entry = Entry(mainw, width=38, font=("Arial", 14))
search_entry.place(x=780, y=10)

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

def search_go(event=None):
    word_search = search_entry.get().strip()

    cur.execute(f"""SELECT eng, transcription, ru FROM translations 
    WHERE eng LIKE '%{word_search}%' OR ru LIKE '%{word_search}%';""")
    find_words = cur.fetchall()

    count = 1
    for i in range(len(find_words)):
        find_words[i] = (count,) + find_words[i]
        count += 1

    for i in tree.get_children():
        tree.delete(i)

    for j in find_words:
        tree.insert("", "end", values=j)

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
                        '{word.strip()}', 
                        '{transcript.replace('|', '[', 1).replace('|', ']', 1).strip()}', 
                        '{translate.strip()}'
                    )""")
        adb.commit()
        word_to_translate.delete(0, END) ## clear field;
        update_table()

    except:
        update_table()
        adb.rollback()

## ## ## ## ## ## ## ##

def delete():
    item = tree.selection() ## selected cell in table;

    if item == ():
        pass ## if not selected item;
    else:
        item = tree.selection()[0]
        eng_word = tree.item(item, "values")[1]
        trans_word = tree.item(item, "values")[2]
        ru_word = tree.item(item, "values")[3]

        popup2 = Toplevel() ## delete window instance;
        popup2.title("Delete menu:")

        screen_width = mainw.winfo_screenwidth()
        screen_height = mainw.winfo_screenheight()

        popup_width = 440
        popup_height = 190

        popup2.geometry("{}x{}+{}+{}".format(popup_width, popup_height, 900, 140))

        frame = Frame(popup2)
        frame.pack(expand=True, fill='both')

        confirm_lbl = Label(frame, text=f'Are you sure you want to remove the word\n<{eng_word}>?', font=("Arial", 14))
        confirm_lbl.pack(pady=10)

        button_frame = Frame(frame)
        button_frame.pack(pady=20)

        def del_tag():  ## remove word and close the window;
            cur.execute(f"""INSERT INTO basket (eng, transcription, ru) VALUES 
            ('{eng_word}', '{trans_word}', '{ru_word}');""")

            cur.execute(f"DELETE FROM translations WHERE eng = '{eng_word}'")
            adb.commit()

            popup2.destroy()
            update_table()

        def on_no(): ## close the window;
            popup2.destroy()

        yes_confirm = Button(button_frame, text='YES', width=15, height=1, command=del_tag)
        yes_confirm.pack(side='left', padx=10, pady=20)

        no_confirm = Button(button_frame, text='NO', width=15, height=1, command=on_no)
        no_confirm.pack(side='right', padx=10, pady=20)

## ## ## ## ## ## ## ##

def description_window():
    item = tree.selection() ## selected cell in table;

    if item == ():
        pass ## if not selected item;
    else:
        item = tree.selection()[0]
        all_word_info = tree.item(item, "values")

        popup = Toplevel()  ## word change window instance;
        popup.title("Menu:")

        screen_width = mainw.winfo_screenwidth()
        screen_height = mainw.winfo_screenheight()

        popup_width = 800
        popup_height = 250
        x_position = (screen_width - popup_width) // 2
        y_position = (screen_height - popup_height) // 2

        popup.geometry("{}x{}+{}+{}".format(popup_width, popup_height, x_position, y_position))

        eng_entry = Entry(popup, width=70, font=("Arial", 14))
        transcription_entry = Entry(popup, width=70, font=("Arial", 14))
        ru_entry = Entry(popup, width=70, font=("Arial", 14))

        eng_entry.place(x=10, y=10)
        transcription_entry.place(x=10, y=60)
        ru_entry.place(x=10, y=110)

        eng_entry.insert(0, f"{all_word_info[1]}")
        transcription_entry.insert(0, f"{all_word_info[2]}")
        ru_entry.insert(0, f"{all_word_info[3]}")

        def change_word():
            en = eng_entry.get()
            trans = transcription_entry.get()
            ru = ru_entry.get()

            cur.execute(f"""UPDATE translations SET 
                        eng = '{en}',
                        transcription = '{trans}',
                        ru = '{ru}'
                        WHERE eng = '{all_word_info[1]}'""")
            adb.commit()
            update_table()

        confirm_change_btn = Button(popup, text="Confirm", font=("Arial", 14), width=12, command=change_word)
        confirm_change_btn.place(x=340, y=170)

## ## ## ## ## ## ## ##

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

context_menu = Menu(mainw, tearoff=0)
context_menu.add_command(label="Изменить", command=description_window)
context_menu.add_command(label="Удалить", command=delete)

## ## ## ## ## ## ## ##

def update_table():
    cur.execute("SELECT eng, transcription, ru FROM translations ORDER BY eng ASC;")
    all_info = cur.fetchall()
    count = 1
    for i in range(len(all_info)):
        all_info[i] = (count,) + all_info[i]
        count += 1

    for i in tree.get_children():
        tree.delete(i)

    for j in all_info:
        tree.insert("", "end", values=j)

## ## ## ## ## ## ## ##

word_to_translate.bind("<Return>", take_word)
search_entry.bind("<Return>", search_go)
tree.bind("<Button-3>", show_context_menu)

## ## ## ## ## ## ## ##
update_table()
mainw.mainloop()
cur.close()
adb.close()