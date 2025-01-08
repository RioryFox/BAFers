if __name__ == "__main__":
    #-------------Work with system
    import os
    import sys
    #-------------Work with timers and random 
    import time
    import random
    #-------------Work with strings
    import re
    import string
    #-------------Work with DB
    import sqlite3
    import json
    import logging
    import zipfile
    from func import self_destruct
    #-------------Work with VK and ethernet
    import vk_api
    import requests
    #-------------
else:
    raise Exception("main.py is't a module")

if not len(sys.argv) in range(2, 4):
    raise Exception("wrong start!")

#-------------------------------------------------------------

global my_box #save all info to start work here

class BannedError(Exception):
    pass

if not os.path.exists(f"{sys.argv[1]}") and not str(sys.argv[1]).isdigit():
    token_user = sys.argv[1]
elif str(sys.argv[1]).isdigit() and os.path.exists(f"{sys.argv[1]}"):
    with open(f"{sys.argv[1]}\{sys.argv[1]}_settings.json", "r") as json_file:
        data = json.load(json_file)
        if not len(data["token"]) > 0:
            raise Exception("No token with this id!")
        token_user = data["token"]
else:
    raise Exception("No token or files with this id!")


for _ in range(3):
    try:
        vk_test = vk_api.VkApi(token=token_user).get_api()
        me = vk_test.users.get()[0]["id"]
        break
    except Exception:
        try:
            result = requests.get("https://yandex.ru")
        except Exception:
            raise Exception("No Ethernet!")
else:
    raise Exception("Can't connect to vk by token!")

#-------------------------------------------------------------
def create_archive(id, path="", end=True):
    files = []
    if not path == "":
        wheight = os.listdir(path=path)
    else:
        wheight = os.listdir()
    for file in wheight:
        if str(id) in file:
            files.append(file)
    if not len(files) > 0:
        return
    if not os.path.exists("archive"):
        os.mkdir("archive")
    zip = zipfile.ZipFile(os.path.join("archive", f"archiveArchive @id{id}.zip"), "w", zipfile.ZIP_DEFLATED)
    for file in files:
        zip.write(os.path.join(path, file))
    else:
        zip.close()
        for file in files:
            if not "." in file:
                create_archive(id, os.path.join(path, file), False)
    if end:
        return True
    return
    


def process_file(file_path):
    try:
        print(f"\x1b[34m(@id{me}) \x1b[30mNow: \x1b[32mSTART \x1b[mexec file \x1b[m{file_path}")
        with open(file_path, "r", encoding="utf-8") as file:
            exec(file.read())
        return "good"
    except Exception as error:
        time.sleep(5)
        if str(error) == f"BANNED @id{me}":
            return "ban"
        elif str(error)=="Turn off":
            return "turn off"
        print(f"\x1b[34m(@id{me})\x1b[0m ERROR: \x1b[31m{error}")
        return "error"


def get_re_search(search, big_list):
    i = 0
    pattern = re.compile(rf"{search}")
    while i < len(big_list):
        match = pattern.fullmatch(big_list[i])
        if not match:
            big_list.remove(big_list[i])
        else:
            i += 1
    return big_list


def check_update(sw_versions, box, only_new=False, get_struct=False):
    now_gen, _, now_lang_mode = box
    struct = {}
    for gen in get_re_search(r'G\d+', os.listdir()):
        for version in get_re_search(r'V\d+', os.listdir(f"{gen}")):
            struct[gen] = {}
            struct[gen][version] = get_re_search(r'L\w+.py', os.listdir(f"{gen}{chr(92)}{version}"))

    for box in sw_versions:
        if len(struct) == 0:
            break
        gen, version, lang = box
        gen = f"G{gen}"
        version = f"V{version}"
        lang = f"L{lang}"
        if not (gen in struct and version in struct[gen] and lang in struct[gen][version]):
            struct[gen][version].remove(lang)
        if len(struct[gen][version]) == 0:
            struct[gen].remove(version)
        if len(struct[gen]) == 0:
            struct.remove(gen)
    if len(struct) == 0 or f"G{now_gen}" not in struct:
        new_version = 0
    else:
        new_version = max(
            int(ver[1:]) for ver in struct[f"G{now_gen}"]
        )
    answear = [now_gen, new_version, now_lang_mode]
    if only_new:
        answear.append(new_version)
    if get_struct:
        answear.append(struct)
    if len(answear) > 3:
        return answear
    answear.append(f"{os.path.join(os.getcwd(), f'G{now_gen}{chr(92)}V{new_version}{chr(92)}L{now_lang_mode}')}")
    return answear


def create_db(me_id, token):
    first = False
    for name in ["main_base", f"{me_id}"]:
        if not os.path.exists(name):
            print(f"\x1b[34m(@id{me_id})\x1b[0m CREATE FLODER: {name}\\")
            os.mkdir(name)
            time.sleep(0.05)
    

    for name in ["main_base\VersionControl.db"]:
        if not os.path.exists(name):
            first = True
            print(f"\x1b[34m(@id{me_id})\x1b[0m CREATE FILE: {name}")
            with sqlite3.connect(name) as db:
                cursor = db.cursor()
                inj = """
                CREATE TABLE IF NOT EXISTS sw_versions(
                version INTEGER,
                lang_mode TEXT,
                gen INTEGER
                );
                CREATE TABLE IF NOT EXISTS dw_versions(
                version INTEGER,
                lang_mode TEXT,
                gen INTEGER
                );
                CREATE TABLE IF NOT EXISTS test_w(
                version INTEGER,
                lang_mode TEXT,
                gen INTEGER
                );
                """
                db.executescript(inj)
                db.commit()
                time.sleep(0.05)

    for name in ["main_base\AccessControl.db", f"{me_id}\AccessControl_{me_id}.db"]:
        if not os.path.exists(name):
            print(f"\x1b[34m(@id{me_id})\x1b[0m CREATE FILE: {name}")
            with sqlite3.connect(name) as db:
                cursor = db.cursor()
                inj = f"""
                CREATE TABLE IF NOT EXISTS black (
                user_id INTEGER
                );
                CREATE TABLE IF NOT EXISTS white (
                user_id INTEGER
                );
                """
                if not str(me_id) in name:
                    inj += """\n
                    CREATE TABLE IF NOT EXISTS acsess_list (
                    userid INTEGER
                    );
                    """
                db.executescript(inj)
                db.commit()
                time.sleep(0.05)
            
    for name in ["main_base\profile.db"]:
        if not os.path.exists(name):
            print(f"\x1b[34m(@id{me_id})\x1b[0m CREATE FILE: {name}")
            with sqlite3.connect(name) as db:
                cursor = db.cursor()
                inj = """
                CREATE TABLE IF NOT EXISTS profile(
                userid INTEGER,
                guild TEXT,
                man_class TEXT,
                race TEXT,
                lvl INTEGER,
                force INTEGER,
                dexterity INTEGER,
                health INTEGER,
                role TEXT,
                red_s TEXT,
                blue_s TEXT 
                );
                CREATE TABLE IF NOT EXISTS target(
                userid INTEGER,
                msg_id INTEGER
                );
                """
                cursor.executescript(inj)
                db.commit()
                time.sleep(0.05)

    for name in ["main_base\classes.json"]:
        if not os.path.exists(name):
            print(f"\x1b[34m(@id{me_id})\x1b[0m CREATE FILE: {name}")
            with open(name, "w") as json_file:
                data ={
                    "classes": {
                        "апостол": {
                            "react_to": "Благословение",
                            "list_react": {
                                "а": "атаки",
                                "з": "защиты",
                                "у": "удачи",
                                "о": "орка",
                                "д": "демона",
                                "ч": "человека",
                                "э": "эльфа",
                                "н": "нежити",
                                "гн": "гнома",
                                "го": "гоблина"
                            },
                            "start_react": ["баф", "а", "з", "у"],
                            "wait_time": 70
                        },
                        "воплощение света": {
                            "react_to": "свет",
                            "list_react": {
                                "п": "-",
                                "с": "светом"
                            },
                            "start_react": ["очищение", "п", "о"],
                            "wait_time": 3610
                        },
                        "крестоносец": {
                            "react_to": "крес",
                            "list_react": {
                                "п": "-",
                                "о": "огнем"
                            },
                            "start_react": ["очищение", "п", "о"],
                            "wait_time": 3610
                        },
                        "повелитель мрака": {
                            "react_to": "прок",
                            "list_react": {
                                "н": "неудачи",
                                "б": "боли",
                                "д": "добычи"
                            },
                            "start_react": ["проклятие", "н", "б", "д"],
                            "wait_time": 3610
                        },
                        "жнец душ": {
                            "react_to": "прок",
                            "list_react": {
                                "н": "неудачи",
                                "б": "боли",
                                "д": "добычи"
                            },
                            "start_react": ["проклятие", "н", "б", "д"],
                            "wait_time": 3610
                        }
                    },
                    "race": {
                        "орк": "о",
                        "демон": "д",
                        "человек": "ч",
                        "эльф": "э",
                        "нежить": "н",
                        "гном": "гн",
                        "гоблин": "го"
                    }
                }
                json.dump(data, json_file, indent=4)
                json_file.close()
                time.sleep(0.05)

    for name in [f"{me_id}\{me_id}_settings.json"]:
        if not os.path.exists(name):
            print(f"\x1b[34m(@id{me_id})\x1b[0m CREATE FILE: {name}")
            with open(name, "w") as json_file:
                trigger = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"[random.randrange(0, 33)]
                prefix = string.punctuation[random.randrange(0, len(string.punctuation))]
                data = {
                    "my_work": [],
                    "were_work": [],
                    "my_version": 0,
                    "gen": 4,
                    "lang_mode": "mix.py",
                    "work_mode": "ON",
                    "trigger": trigger,
                    "priffix": prefix,
                    "reporting": 0,
                    "real_my_class": "Unknown",
                    "my_race": ["Unknown"],
                    "my_effects": ["Unknown"],
                    "my_custom_commands": [],
                    "my_custom_reactions": [],
                    "my_voice": 0,
                    "wait_time": 3610,
                    "my_time": 0,
                    "token": token
                }
                json.dump(data, json_file, indent=4)
                json_file.close()
    
    if first:
        with sqlite3.connect("main_base\AccessControl.db") as db:
            cursor = db.cursor()
            inj = """
            INSERT INTO acsess_list (userid) VALUES (?)
            """
            cursor.execute(inj, [me_id])
            db.commit()
    
    with sqlite3.connect("main_base\AccessControl.db") as db:
        cursor = db.cursor()
        inj = """
        SELECT userid
        FROM acsess_list
        WHERE userid = ?
        """
        alpha = cursor.execute(inj, [me_id])
        alpha = cursor.fetchall()
        if not len(alpha) == 1:
            #self_destruct(me_id)
            raise Exception("Banned acsess")
    with open(f"{me_id}\{me_id}_settings.json", "r") as json_file:
        data = json.load(json_file)
    return data


def add_new_version(where, what):
    with sqlite3.connect("main_base\VersionControl.db") as db:
        cursor = db.cursor()
        inj = f"SELECT version, lang_mode FROM {where} WHERE version = ? AND lang_mode = ? AND gen = ?"
        cursor.execute(inj, what)
        alpha = cursor.fetchone()
        if alpha is None:
            inj = f"INSERT INTO {where} (version, lang_mode, gen) VALUES(?, ?, ?)"
            cursor.execute(inj, what)
        db.commit()


def delete_version(where, what):
    with sqlite3.connect("main_base\VersionControl.db") as db:
        cursor = db.cursor()
        inj = f"DELETE FROM {where} WHERE version = ? AND lang_mode = ? AND gen = ?"
        cursor.execute(inj, what)
        db.commit()


def get_all_info(user_id, token):
    my_data = create_db(user_id, token)
    with sqlite3.connect("main_base\VersionControl.db") as db:
        cursor = db.cursor()
        inj = "SELECT gen, version, lang_mode FROM sw_versions"
        cursor.execute(inj, [])
        list_sw_versions = cursor.fetchall()
        inj = "SELECT gen, version, lang_mode FROM dw_versions"
        cursor.execute(inj, [])
        list_dw_versions = cursor.fetchall()
        inj = "SELECT gen, version, lang_mode FROM test_w"
        cursor.execute(inj, [])
        list_test_w = cursor.fetchall()
        db.commit() 

        return list_sw_versions, list_dw_versions, list_test_w, my_data

#-------------------------------------------------------------

if __name__ == "__main__":
    while True:
        global_sw_versions, global_dw_versions, _, my_data= get_all_info(me, token_user)
        my_box = [(global_sw_versions, global_dw_versions), (token_user, me), my_data]
        my_version = my_box[2]["my_version"]
        my_gen = my_box[2]["gen"]
        my_lang_mode = my_box[2]["lang_mode"]

        my_gen, my_version, my_lang_mode, file_path = check_update(global_sw_versions, [my_gen, my_version, my_lang_mode])
        if not create_archive(me):
            print(f"\x1b[34m(@id{me})\x1b[0m ERROR: \x1b[31mCan't create archive!")
            break
        if my_version == 0:
            print(f"\x1b[34m(@id{me}) \x1b[5;35;40mNO WORK VERSIONS: \x1b[0mSTOP WORK")
            break
        print(f"\x1b[34m(@id{me}) \x1b[32mSTART work with: \x1b[0m{my_gen}/{my_version}/{my_lang_mode[:len(my_lang_mode)-3]}")
        result = process_file(file_path)
        with open(f"{me}\{me}_settings.json", "w") as json_file:
            json.dump(my_box[2], json_file, indent=4)
        if result == "good":
            print(f"\x1b[34m(@id{me}) \x1b[32mNEW GOOD version: {my_gen}/{my_version}/{my_lang_mode[:len(my_lang_mode)-3]}")
            add_new_version("sw_versions", [my_version, my_lang_mode, my_gen])
        elif result == "error":
            print(f"\x1b[34m(@id{me}) \x1b[31mNEW BAD version: \x1b[0m{my_gen}/{my_version}/{my_lang_mode[:len(my_lang_mode)-3]}")
            delete_version("sw_versions", [my_version, my_lang_mode, my_gen])
            add_new_version("dw_versions", [my_version, my_lang_mode, my_gen])
        else:
            print(f"\x1b[34m(@id{me}) \x1b[5;34;40mROOT ANSWEAR \x1b[0mSTOP WORK")
            break
        logging.shutdown()
        time.sleep(5)