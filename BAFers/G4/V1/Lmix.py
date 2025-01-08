if __name__ == "__main__":
    import vk_api
    from vk_api.longpoll import VkLongPoll, VkEventType
    import random
    import time
    import os
    import re
    import string
    import sqlite3
    import json
    import math
    import traceback
    import datetime
    import logging
    import pytz
    #~~~~~~~~~~~~~~~~~
    from func import *
else:
    raise Exception("Lmix.py isn't a module")

#-------------------------------------------------------------

class MyLongPoll(VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as error:
                print(f"\n(@id{my_id}) - Переподключение к серверам ВК - {error}\n")
                time.sleep(3)
                session_api = vk_session.get_api()
                self.__init__(vk_session)
                continue


class BannedError(Exception):
    pass

class TurnOff(Exception):
    pass

#-------------------------------------------------------------
print(f"\x1b[34m(@id{my_box[1][1]}) \x1b[30mNow:\x1b[m Unboxing data...")

(
    my_token,
    my_id,
    my_gen,
    my_version,
    my_lang_mode,
    my_trigger,
    my_preffix,
    my_reporting,
    my_were_work,
    my_work,
    my_real_class,
    my_races,
    my_effects,
    my_custom_commands,
    my_custom_reactions,
    my_voice,
    my_wait_time,
    my_time,
    my_work_mode
    ) = unboxing_data(my_box)

print(f"\x1b[34m(@id{my_id}) \x1b[32mSuc.:\x1b[m Unboxing data")
#~~~~~~~~~~~~~~~~~
print(f"\x1b[34m(@id{my_id}) \x1b[30mNow:\x1b[m work with API VK...")

vk_session = vk_api.VkApi(token=my_token)
session_api = vk_session.get_api()
long_pool = MyLongPoll(vk=vk_session)

print(f"\x1b[34m(@id{my_id}) \x1b[32mSuc.:\x1b[m work with API VK")
#~~~~~~~~~~~~~~~~~
order = []
all_events = []
adapt = 0
last_update_time = 0
last_save_time = math.ceil(time.time())
delete_time = 0
save_time = 300
delete = False
#~~~~~~~~~~~~~~~~~
print(f"\x1b[34m(@id{my_id}) \x1b[30mNow:\x1b[m Open game data...")

g_classes, g_races = open_game_data()

print(f"\x1b[34m(@id{my_id}) \x1b[32mSuc.:\x1b[m Open game data")
#~~~~~~~~~~~~~~~~~
print(f"\x1b[34m(@id{my_id}) \x1b[30mNow:\x1b[m STARTING WORK AND LOGGING...")

tz = pytz.timezone("Europe/Moscow")
log_file_path = os.path.join(f"{my_id}", f"{my_id}_G{my_gen}V{my_version}L{my_lang_mode[:-3]}.log")
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode="w")
logging.info(f"---Start process----")

print(f"\x1b[34m(@id{my_id})\x1b[32m Suc.: START \x1b[m{my_gen}/{my_version}/{my_lang_mode}")
send_msg(vk_session, "user", my_id, f"---start---\nMY_ID: {my_id}\n🌐G{my_gen}.V{my_version}.{my_lang_mode[:len(my_lang_mode)-3]}\nВас приветсвует программа BAFers\n\nВаши последние настройки: {my_preffix}{my_trigger}\nПодключенных в работу чатов: {len(my_were_work)}\nБлагодарим за использование!", notice=True)
#890775441

black_list, white_list, last_update_time = get_bw_lists(my_id)


#-------------------------------------------------------------
while True:

    #~~~~~~~~~~~~~~~~~
    for filename in ["main_base\AccessControl.db", f"{my_id}\AccessControl_{my_id}.db"]:
        if last_update_time < os.path.getatime(filename):
            black_list, white_list, last_update_time = get_bw_lists(my_id)
            if my_id in black_list:
                logging.error("BANNED")
                raise BannedError(f"BANNED @id{my_id}")

    try:
        for api_event in long_pool.listen():
            if api_event.type == VkEventType.MESSAGE_NEW:
                if api_event.from_group:
                    if api_event.group_id == 182985865 or api_event.group_id == 183040898:
                        all_events.append(((-1)*api_event.group_id, api_event.text, api_event.message_id, api_event))
                elif api_event.from_chat:
                    if api_event.chat_id in my_were_work:
                        all_events.append((api_event.user_id, api_event.text, api_event.message_id, api_event))
                    elif api_event.text == f"{chr(92)}chat_add":
                        my_were_work, my_box = repackaging(api_event.chat_id, my_box, (2, "were_work"), "add")
                        with open(f"{my_id}\{my_id}_settings.json", "w") as json_file:
                            json.dump(my_box[2], json_file, indent=4)
                        logging.info(f"Сохранение после добавления чата №{api_event.chat_id} в работу")
                        send_msg(vk_session, "chat", api_event.chat_id, "✅Этот чат был добавлен в работу, теперь мои бафы будут доступны всем, кто в этом чате!\nВнимательно изучите после этого сообщения иснтрукции из команды 'help' для личного пользования")
            #~~~~~~~~~~~~~~~~~
            if math.ceil(time.time())%5 == 0:
                _ = session_api.users.get() #костыль для незакрытия соединения!!!
                time.sleep(1)
            if len(all_events) > 0:
                break
    except Exception:
        continue
    #~~~~~~~~~~~~~~~~~
    while len(all_events) > 0:
        (user_id, msg, msg_id, api_event) = all_events[0]
        if user_id > 0:
            msg_info = session_api.messages.getById(message_ids=[msg_id])["items"][0]
            msg_fwd = msg_info["fwd_messages"]
            msg_atch = msg_info["attachments"]
            if check_target(user_id) == 0:
                save_target_id(user_id, msg_id)
            if msg.startswith(f"{my_preffix}{my_trigger} "):
                if user_id in black_list:
                    logging.info(f"Отказ @id{user_id} в обслуживании")
                    send_msg(vk_session, "chat", api_event.chat_id, "🚫Вы находитесь в массовом или личном черном списке, я не могу взаимодецствовать с вами в автоматическом режиме, простите...", reply_to=msg_id)
                elif len(msg_fwd) == 0:
                    msg = msg[len(f"{my_preffix}{my_trigger} "):]
                    order.append([user_id, msg, msg_id])
                    logging.info(f"Принят заказ от @id{user_id}")
                    send_msg(vk_session, "chat", api_event.chat_id, f"✅Ваш запрос #{len(order)} в очереди!", reply_to=msg_id)
                elif len(msg_fwd) == 1:
                    msg_fwd = msg_fwd[0]
                    if msg_fwd["from_id"] not in black_list:
                        order.append([msg_fwd["from_id"], msg[len(f"{my_preffix}{my_trigger} "):], msg_fwd["id"]])
                        logging.info(f"Принят заказ от @id{user_id} для @id{msg_fwd['from_id']}")
                        send_msg(vk_session, "chat", api_event.chat_id, f"✅Ваш запрос для @id{msg_fwd['from_id']} #{len(order)} в очереди!", reply_to=msg_id)
                    else:
                        logging.info(f"Отказ запроса @id{user_id} для @id{msg_fwd['from_id']}")
                        send_msg(vk_session, "chat", api_event.chat_id, f"🚫@id{msg_fwd['from_id']} находится в массовом или личном черном списке, я не могу взаимодецствовать с этим аккакунтом в автоматическом режиме, простите...", reply_to=msg_id)
            #~~~~~~~~~~~~~~~~~
            elif (user_id == my_id
                or (user_id == 890775441   
                    and my_id in msg)):
                if my_id != 890775441 and user_id == 890775441:
                    msg = msg.replace(str(my_id), "")
                if msg.lower() == "\chat_dell":
                    my_were_work, my_box = repackaging(api_event.chat_id, my_box, (2, "were_work"), "dell")
                    with open(f"{my_id}\{my_id}_settings.json", "w") as json_file:
                        json.dump(my_box[2], json_file, indent=4)
                    logging.info(f"Сохранение настроек программы после выхода из чата №{api_event.chat_id}")
                    send_msg(vk_session, "chat", api_event.chat_id, "Я больше не буду работать в этом чате!")
                elif msg.lower().startswith("trigger"):
                    my_trigger, my_box = repackaging(msg.replace("trigger ", ""), my_box, (2, "trigger"))
                    logging.info(f"Смена триггера в чате №{api_event.chat_id} триггер: {my_trigger}")
                    send_msg(vk_session, "chat", api_event.chat_id, f"✅Триггер был изменен на: {my_trigger}\nТекущий полный вид команды: {my_preffix}{my_trigger}\nВНИМАНИЕ! Если команда совпадет с чужим баффером - обе системы будут одновременно реагировать на ваш запрос!", reply_to=msg_id)
                elif (msg.startswith("preffix") and  " " in msg):
                    my_preffix, my_box = repackaging(msg.replace("preffix ", ""), my_box, (2, "preffix"))
                    logging.info(f"Смена преффикса в чате №{api_event.chat_id} преффикс: {my_preffix}")
                    send_msg(vk_session, "chat", api_event.chat_id, f"✅Преффикс был изменен на: {my_preffix}\nТекущий вид команды: {my_preffix}{my_trigger}\nВНИМАНИЕ! Если команда совпадет с чужим баффером - обе системы будут одновременно реагировать на ваш запрос!", reply_to=msg_id)
                elif msg.lower() == "preffix":
                    my_preffix, my_box = repackaging("", my_box, (2, "preffix"))
                    logging.info(f"Отключение преффикса в чате №{api_event.chat_id}")
                    send_msg(vk_session, "chat", api_event.chat_id, f"✅Преффикс был отключен!\nТекущий вид команды: {my_preffix}{my_trigger}\nВНИМАНИЕ! Если команда совпадет с чужим баффером - обе системы будут одновременно реагировать на ваш запрос!", reply_to=msg_id)
                elif msg[1:].lower().startswith("info"):
                    msg = msg.replace("+", "ON")
                    msg = msg.replace("-", "OF")
                    if my_reporting != msg[:2]:
                        logging.info("Переключение режима уведомлений... ")
                        if msg[:2] == "ON":
                            my_reporting, my_box = repackaging("ON", my_box, (2, "work_mode"))
                        else:
                            my_reporting, my_box = repackaging("OF", my_box, (2, "work_mode"))
                        logging.info(f"Уведомления переключены в режим: {my_reporting}")
                        send_msg(vk_session, "chat", api_event.chat_id, f"✅Уведомления находятся в режиме: {my_reporting.replace('F', 'FF')}", reply_to=msg_id)
                    else:
                        send_msg(vk_session, "chat", api_event.chat_id, "🌚Уведомления и так находятся в этом режиме или команда была написанна не корректно!\nНаппомним:\n+info - включает уведомления\n-info - отключает", reply_to=msg_id)
                elif msg.lower().startswith("custom"):
                    old_my_box = my_box
                    old_my_custom_commands = my_custom_commands
                    try:
                        msg = msg.replace("custom\n", "")
                        big_st_data = msg.split("\n")
                        _, my_box = repackaging({}, my_box, (2, "my_custom_commands"))
                        if len(my_work) > 1:
                            for obj in big_st_data:
                                sml_st_data = obj.split(" - ")
                                for part in range(1, len(my_effects)):
                                    if sml_st_data[0] == my_effects[part]:
                                        my_custom_commands, my_box = repackaging(sml_st_data[1], my_box, (2, "my_custom_commands",), mode="add key", key=sml_st_data[0])
                            logging.info(f"Изменение команд на кастомные: {my_custom_commands}")
                            send_msg(vk_session, "chat", api_event.chat_id, "✅Ваша команда была распознанна корректно, новые настройки вступили в силу!", reply_to=msg_id)
                        else:
                            logging.info(f"Отказ в создании кастомных команд, причина: отсутсвие информации о персонаже")
                            send_msg(vk_session, "chat", api_event.chat_id, "🚫Вы не проводили адаптацию ранее, прошу примените \check для адаптации!\nПодробнее в команде 'help'", reply_to=msg_id)
                    except Exception as error:
                        logging.error(f"Ошибка создания кастомных команд: {error}")
                        my_box = old_my_box
                        my_custom_commands = old_my_custom_commands
                        send_msg(vk_session, "chat", api_event.chat_id, "🚫Ваша команда была распознанна не корректно или в ней содержатся ошибки!\nИзменения не были сохранены!\nПроверьте команду перед отправкой!", reply_to=msg_id)
                elif msg.lower() == "info":
                    logging.info(f"Вызов информации о настройках программы")
                    send_msg(vk_session, "chat", api_event.chat_id, f"⚙Ваши текущие настройки:\n👤Класс: {my_real_class}({my_voice}), {my_races}\n👥Количество рабочих чатов: {len(my_were_work)}\n\n🤖Вид команды: {my_preffix}{my_trigger}\n✨Мои эффекты: {str(my_custom_commands)[1:len(my_box)-2]}", reply_to=msg_id)
                elif msg == "save_settings":
                    with open(f"{my_id}\{my_id}_settings.json", "w") as json_file:
                        json.dump(my_box[2], json_file, indent=4)
                    logging.info(f"Сохранение настроек программы")
                    send_msg(vk_session, "chat", api_event.chat_id, "💾Ваши настройки были успешно сохранены!", reply_to=msg_id)
                elif msg.lower() == "\check":
                    adapt = api_event.chat_id
                    logging.info(f"Применен публичный вызов профиля в чате")
                    send_msg(vk_session, "chat", adapt,  f"😎@id{my_id}(Мой) профиль для пользователя программы @club194013021(BAFers)!")
                elif msg.lower() == "\check_s":
                    adapt = api_event.chat_id
                    logging.info(f"Применен тихий вызов профиля в личные сообщения воплощения")
                    send_msg(vk_session, "peer", -183040898, f"👀Тайно хочу увидеть @id{my_id}(Мой) профиль для пользователя программы @club194013021(BAFers)...")
                elif msg.lower() == "turn_off":
                    with open(f"{my_id}\{my_id}_settings.json", "w") as json_file:
                        json.dump(my_box[2], json_file, indent=4)
                    logging.info(f"Выключение бота...")
                    send_msg(vk_session, "chat", api_event.chat_id, "🔌Бот выключается...", reply_to=msg_id)
                    raise TurnOff("Turn off")
                elif msg.lower() == "delete my data":
                    if delete:
                        send_msg(vk_session, "chat", api_event.chat_id, "👀Удаление ваших данных...", reply_to=msg_id)
                        self_destruct(my_id)
                        send_msg(vk_session, "chat", api_event.chat_id, "✅Ваши данные, включая эту программу - удалены! Спасибо что были с нами!\n🔌Бот выключается...", reply_to=msg_id)
                        raise TurnOff("Turn off")
                    delete = True
                    delete_time = math.ceil(time.time())
                    send_msg(vk_session, "chat", api_event.chat_id, "Внимание! Эта команда безвозвратно удалит ВСЕ ваши данные из проетка и выключит бота! Если вы уверены в своем решении - напишите эту команду еще раз в течении 30-ти секунд", reply_to=msg_id)
                elif msg.lower().startswith("!я "):
                    if msg[3:] in g_races:
                        my_races = msg[3:].split('-')
                        logging.info(f"Успешная ручная адаптация расы")
                        send_msg(vk_session, "chat", api_event.chat_id, "✅Ручная адаптация расы прошла успешно!", reply_to=msg_id)
                    elif msg[3:] in g_classes:
                        my_real_class, my_box = repackaging(msg[3:], my_box, (2, "real_my_class"))
                        if my_races[0] != "Unknown":
                            my_work, my_custom_commands, my_effects, my_wait_time  = adaptation(my_real_class, my_races, g_classes, g_races)
                            my_work, my_box = repackaging(my_work, my_box, (2, "my_work"))
                            my_effects, my_box = repackaging(my_effects, my_box, (2, "my_effects"))
                            logging.info(f"Успешная ручная адаптация класса")
                            send_msg(vk_session, "chat", api_event.chat_id, "✅Ручная адаптация класса прошла успешно!", reply_to=msg_id)
                        else:
                            logging.error("Ошибка ручной адаптации")
                            send_msg(vk_session, "chat", api_event.chat_id, "🚫Ручная адаптация не удалась, нам неизвестна ваша расса\nПодробнее по команде 'help'", reply_to=msg_id)
                        with open(f"{my_id}\{my_id}_settings.json", "w") as json_file:
                            json.dump(my_box[2], json_file, indent=4)
                    else:
                        logging.error("Ошибка ручной адаптации, причина: неподдерживаемый класс")
                        send_msg(vk_session, "chat", api_event.chat_id, "🚫Ручная адаптация не удалась, данный класс не поддерживается программой или он написан с ошибкой\nПодробнее по команде 'help'", reply_to=msg_id)
                elif ", Ваш профиль:" in msg:
                    user_id, u_class, race, guild, role, karma, lvl, force, dexterity, health, atack, armor = read_profile(msg)
                    if user_id == my_id:
                        if "(" in u_class:
                            my_voice = int(re.findall(r"([\d]+)", u_class)[0])
                            u_class = "апостол"
                        my_races, my_box = repackaging(race, my_box, (2, "my_race"))
                        if adapt > 0:
                            if u_class in g_classes:
                                my_real_class, my_box = repackaging(u_class, my_box, (2, "real_my_class"))
                                my_box[2]["my_work"], my_box[2]["my_effects"] = adaptation(my_real_class, my_races, g_classes, g_races)
                                with open(f"{my_id}\{my_id}_settings.json", "w") as json_file:
                                    json.dump(my_box[2], json_file, indent=4)
                                logging.info("Успешная автоматическая адаптация")
                                send_msg(vk_session, "chat", adapt, "✅Адаптация прошла успешно!")
                            else:
                                logging.error("Ошибка автоматической адаптации")
                                send_msg(vk_session, "chat", adapt, "🚫Автоматическая адаптация не удалась, используйте команду !я для ручного определения своего класса\nПодробнее по команде 'help'")
                            adapt = 0
        #~~~~~~~~~~~~~~~~~
        else:
            if "Заработано репутации Ордена:" in msg:
                my_voice += 1
                logging.error(f"Убито чудовище подземелий, мой голос: {my_voice}")
            elif ", Ваш профиль:" in msg:
                    user_id, u_class, race, guild, role, karma, lvl, force, dexterity, health, atack, armor = read_profile(msg)
                    if user_id == my_id:
                        if "(" in u_class:
                            my_voice = int(re.findall(r"([\d]+)", u_class)[0])
                            u_class = "апостол"
                        my_races, my_box = repackaging(race, my_box, (2, "my_race"))
                        if adapt > 0:
                            if u_class in g_classes:
                                my_real_class, my_box = repackaging(u_class, my_box, (2, "real_my_class"))
                                my_box[2]["my_work"], my_box[2]["my_effects"] = adaptation(my_real_class, my_races, g_classes, g_races)
                                with open(f"{my_id}\{my_id}_settings.json", "w") as json_file:
                                    json.dump(my_box[2], json_file, indent=4)
                                logging.info("Успешная автоматическая адаптация")
                                send_msg(vk_session, "chat", adapt, "✅Адаптация прошла успешно!")
                            else:
                                logging.error("Ошибка автоматической адаптации")
                                send_msg(vk_session, "chat", adapt, "🚫Автоматическая адаптация не удалась, используйте команду !я для ручного определения своего класса\nПодробнее по команде 'help'")
                            adapt = 0
        #~~~~~~~~~~~~~~~~~
        all_events.remove(all_events[0])
    #~~~~~~~~~~~~~~~~~
    if (my_time+my_wait_time) < math.ceil(time.time()) and len(order) > 0:
        new_order = order[0]
        try:
            new_order, possition = get_react(my_effects, new_order)
            if possition is None:
                print(possition)
        except Exception as error:
            print(f"322 {error}")
        my_time = math.ceil(time.time())
        new_order = new_order[1:]
        order[0] = new_order
        if len(order[0]) == 0:
            order.remove(order[0])
            print("empty!")
        else:
            print("at work...")
    if delete and delete_time < math.ceil(time.time()-30):
        delete = False
        delete_time = 0

    if math.ceil(time.time()) % save_time == 0:
        with open(f"{my_id}\{my_id}_settings.json", "w") as json_file:
            json.dump(my_box[2], json_file, indent=4)