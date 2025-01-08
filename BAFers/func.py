if not __name__ == "__main__":
    #-------------Work with system
    import os
    import sys
    import shutil
    #-------------Work with timers and math
    import time
    import math
    import multiprocessing
    #-------------Work with strings
    import re
    import string
    #-------------Work with DB
    import sqlite3
    import json
else:
    raise Exception("This is not main file, it is a library")

#-------------------------------------------------------------

#Unbox "big" data from global box
def unboxing_data(box):
    return (
        box[1][0], 
        box[1][1],  
        box[2]["gen"],
        box[2]["my_version"],
        box[2]["lang_mode"],
        box[2]["trigger"],
        box[2]["priffix"],
        box[2]["reporting"],
        box[2]["were_work"],
        box[2]["my_work"],
        box[2]["real_my_class"],
        box[2]["my_race"],
        box[2]["my_effects"],
        box[2]["my_custom_commands"],
        box[2]["my_custom_reactions"],
        box[2][ "my_voice"],
        box[2]["wait_time"],
        box[2]["my_time"],
        box[2]["work_mode"]
    )

#Open DB with game data about classes and races
def open_game_data():
    with open("main_base\classes.json", "r") as json_file:
        data = json.load(json_file)
    return data["classes"], data["race"]

#Read profile with regular strings
def read_profile(prof):
    user_id = int(re.findall(r"\[id(\d+)\|", prof)[0])
    u_class = re.findall(r"Класс: ([\w\s]+),", prof)[0]
    race = re.findall(fr'{u_class}, (.+)', prof)[0]
    guild = re.findall(r'Гильдия: ([\w\s]+)', prof)[0]
    role = ""
    if '🌟' in prof or '⭐' in prof:
        role = "⭐" if '⭐' in prof else "🌟"
    karma = re.findall(fr'{guild}{role}\n.(.+)', prof)[0]
    lvl = int(re.findall(r"Уровень: ([\d]+)", prof)[0])
    force = int(re.findall(r'👊([\d]+)', prof)[0])
    dexterity = int(re.findall(r'🖐([\d]+)', prof)[0])
    health = int(re.findall(r'❤([\d]+)', prof)[0])
    atack = int(re.findall(r'🗡([\d]+)', prof)[0])
    armor = int(re.findall(r'🛡([\d]+)', prof)[0]) 
    return user_id, u_class, race, guild, role, karma, lvl, force, dexterity, health, atack, armor

#Serch profile with use history
def get_history(who, chat_id, start_message_id=None):
    lastMessage = who.method(
        "messages.getHistory",
        {
            "peer_id": chat_id,
            "start_message_id": start_message_id
        }
    )
    #for prof in lastMessage["items"]:
    #    if "ваш профиль" in prof["text"].lower():
    #        return prof["text"]
    return lastMessage["items"]

def delete_msg(who, peer_id, msg_id, delete_for_all=True):
    who.method(
        #session_api.messages.delete(message_ids=[answer], delete_for_all=1, peer_id=-182985865)
        "messages.delete",
        {
            "message_ids": [msg_id],
            "delete_for_all": delete_for_all,
            "peer_id": peer_id
        }
    )

#Search target
def get_target(who, user_id, timer=0):
    all_characters = (
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        + "абвгдеёжзийклмнопрстуфхцчшщъыьэюя".upper()
        + string.digits
        + "😀😃😄😁😆😅😂🤣😊😇"
        + string.punctuation
        + string.ascii_letters
        + string.whitespace
    )
    for word in all_characters:
        try:
            targetMessages = who.messages.search(
                q=word, user_id=user_id, preview_length=1
            )
            if len(targetMessages["items"]) > 0:
                for i in range(len(targetMessages["items"])):
                    if (
                        targetMessages["items"][i]["date"] > timer
                        and targetMessages["items"][i]["from_id"] == user_id
                    ):
                        return targetMessages["items"][i]["id"]
        except Exception as error:
            print(f"#get_target-{user_id} --> {error}")
        time.sleep(0.2)
    return 0

#Sertch phrase in part of msg of user
def check_prof(who, user_id, text, cut_len, timer=0):
    try:
        targetMessages = who.messages.search(
            q=text, user_id=user_id, preview_length=cut_len
        )
        for i in range(len(targetMessages["items"])):
            if (
                targetMessages["items"][i]["date"] > timer
                and targetMessages["items"][i]["from_id"] == user_id
                and text.lower() in targetMessages["items"][i]["text"].lower()
            ):
                return str(targetMessages["items"][i]["id"])
    except Exception as error:
        print(f"#get_target-{user_id} --> {error}")
    return "None"

#Send msg - nothing else
def send_msg(who, type, to_id, msg, message_id=None, reply_to=None, notice=False):
    who.method(
        "messages.send",
        {
            f"{type}_id": to_id,
            "message": msg,
            "reply_to": reply_to,
            "forward_messages": [message_id],
            "random_id": 0
        }
    )
    if notice:
        #890775441 878366772
        send_msg(who, type, 878366772, "Успешный запус программы!")
        delete_msg(who, 878366772, get_history(who, 878366772)[0]["id"], False)


def check_profile(user_id):
    find = "SELECT userid, guild, man_class, lvl, picture FROM profile WHERE userid = ?"
    try:
        db = sqlite3.connect("main_base\profile.db")
        cursor = db.cursor()
        cursor.execute(find, [user_id])
        alpha = cursor.fetchone()
        (
            userid,
            guild,
            man_class,
            lvl,
            photo,
        ) = alpha
        return userid, guild, man_class, lvl, photo
    except sqlite3.Error as e1:
        print(f"#check_profile -tablem-> {e1}")
        return f"@id{user_id}(Я) @id890775441(немного не работаю), простие меня :)"
    finally:
        cursor.close()
        db.close()


def get_bw_lists(me_id):
    black_list = []; white_list = []; last_update = 0
    for filename in ["main_base\AccessControl.db", f"{me_id}\AccessControl_{me_id}.db"]:
        for table in ["black", "white"]:
            with sqlite3.connect(filename) as db:
                cursor = db.cursor()
                inj = f"SELECT * FROM {table}"
                cursor.execute(inj, [])
                results = cursor.fetchall()
                for result in results:
                    if table == "black":
                        black_list.append(result[0])
                        next(table)
                    white_list.append(result[0])
            time.sleep(0.05)
        if last_update < os.path.getmtime(filename=filename):
            last_update = os.path.getmtime(filename=filename)
    else:
        return black_list, white_list, last_update

def check_target(target_id):
    with sqlite3.connect("main_base\profile.db") as db:
        cursor = db.cursor()
        inj = "SELECT msg_id FROM target WHERE userid = ?"
        cursor.execute(inj, [target_id])
        result = cursor.fetchone()
        if result is not None:
            return result[0]
        return 0
    
def save_target_id(target_id, msg_id):
    return

def adaptation(real_class, races, classes, list_races):
    return classes[real_class]['start_react'], classes[real_class]["react_to"], classes[real_class]["list_react"], classes[real_class]["wait_time"]

def get_react(effects, order):
    try:
        for word in len(order[1]):
            if order[1][word] in effects[0]:
                return effects[0].get(order[1][word])
        else:
            return None
    except Exception:
        return None


def repackaging(obj, box, way, option=None):
    if len(way) > 0:
        way = "box[" +  str(way)[1 : len(str(way))-1] + "]"
        way = way.replace(", ", "][")
        if option is None:
            exec(f"{way} = obj")
        if option == "add":
            exec(f"{way}.append({obj})")
        if option == "rm":
            exec(f"{way}.remove({obj})")
        obj = eval(f"{way}")
    return obj, box


def self_destruct(me_id, project=False):
    if not project:
        files = os.listdir()
        print(files)
        a = input()
        print
        for file in files:
            try:
                if not me_id in file or file in ["func.py", "main.py"]:
                    next(file)
                elif not "." in file:
                    shutil.rmtree(file)
                    next(file)
                os.remove(file)
            except Exception as error:
                print(error)
                continue
        os.remove(__file__)
        return
    shutil.rmtree(os.getcwd())

def eval_expression(expression, result_queue):
    try:
        result_queue.put(eval(expression))
    except Exception as e:
        result_queue.put(e)

def eval_with_timeout(expression, timeout):
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=eval_expression, args=(expression, result_queue))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        return "Слишком долгий процесс, простите, я не удержался и закрыл его))"
    else:
        return result_queue.get()