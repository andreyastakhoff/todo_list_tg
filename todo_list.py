import telebot
from telebot import types
import time
import json
import os.path

class Task:
    def __init__(self, name, task_day="", task_time=""):
        self.id = time.time()
        self.name = name
        self.day = task_day
        self.time = task_time
        self.message_id = 0


BUTTONS = ["Новая задача ✏️", "Список дел 📋"]
WEEK_BUTTONS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
TASK_BUTTONS = ["✅","❌","🗓","🕒"]
TIME_START = 7
TIME_END = 21
FILE_NAME = "data.json"

bot=telebot.TeleBot('5303995352:AAGbVdOK7BsoD-vqPCZoAZn3SuoQJQX3o1x')


def get_todo_list(chat_id):
    chats_todo_list = read_file()
    todo_list = chats_todo_list.get(str(chat_id))
    if todo_list == None:
        todo_list = []  
    return todo_list, chats_todo_list

def set_todo_list(chats_todo_list, todo_list, chat_id):
    chats_todo_list[str(chat_id)] = todo_list
    write_file(chats_todo_list)

def encode_task(task):
    return {"type":"Task", "id":task.id, "name":task.name,"day":task.day, "time":task.time, "message_id":task.message_id}

def decode_task(dictionary):
    if dictionary.get("type") == "Task":
        name = dictionary.get("name")
        day = dictionary.get("day")
        time = dictionary.get("time")
        id = dictionary.get("id")
        message_id = dictionary.get("message_id")
        new_task = Task(name, day, time)
        new_task.id = id
        new_task.message_id = message_id
        return new_task
    else:
        return dictionary

def write_file(chats_todo_list ):
    with open(FILE_NAME,"w") as file:
        json.dump(chats_todo_list, file, default=encode_task)

def read_file():
    if os.path.getsize(FILE_NAME):
        with open(FILE_NAME) as file:        
            data = json.load(file, object_hook=decode_task)
            return data
    else:
        return {}


def task_keyboard(id_task):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard_buttons = []
    for button in TASK_BUTTONS:
        data = {'id':id_task, 'action':button}
        json_string = json.dumps(data)
        task_button=types.InlineKeyboardButton(button, callback_data=json_string)
        keyboard_buttons.append(task_button)
    keyboard.add(*keyboard_buttons)
    return keyboard

def day_keyboard(id_task):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard_buttons = []
    for day in WEEK_BUTTONS:
        data = {'id':id_task, 'action':'day'}
        data['day_index'] = WEEK_BUTTONS.index(day)
        json_string = json.dumps(data)
        day_btn=types.InlineKeyboardButton(day, callback_data=json_string)
        keyboard_buttons.append(day_btn)
    keyboard.add(*keyboard_buttons)
    return keyboard

def time_keyboard(id_task):
    keyboard_time = types.InlineKeyboardMarkup(row_width=5)
    keyboard_buttons_time = []
    for time in range(TIME_START, TIME_END + 1):
        data = {'id':id_task, 'action':'time'}
        time_str = f"{time}:00"
        data['time'] = time_str 
        json_string = json.dumps(data)
        time_btn=types.InlineKeyboardButton(time_str, callback_data=json_string)
        keyboard_buttons_time.append(time_btn)
    keyboard_time.add(*keyboard_buttons_time)
    return keyboard_time


def add_new_task(message):
    bot.send_message(message.chat.id, "✏️ Введите название задачи:")

def print_todo_list(message):
    todo_list, chats_todo_list = get_todo_list(message.chat.id)
    if not todo_list:
        bot.send_message(message.chat.id, "Ваш список пуст! 😕")
    else:
        for i, task in enumerate(todo_list):
            bot.delete_message(message.chat.id, task.message_id)
            text = f"🔸 Задача № {i + 1}. {task.name}\n{task.day} {task.time}\n"
            new_message = bot.send_message(message.chat.id, text, reply_markup=task_keyboard(task.id))
            task.message_id = new_message.id
            set_todo_list(chats_todo_list, todo_list, message.chat.id)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    new_task_btn = types.KeyboardButton(BUTTONS[0])
    todo_list_btn = types.KeyboardButton(BUTTONS[1])
    markup.row(new_task_btn, todo_list_btn)
    bot.send_message(message.chat.id, "Привет, что нужно сделать?  🙃", reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message):
	bot.send_message(message.chat.id,
				"Привет! Вот список доступных команд:\n/start - начало работы\n/help - список доступных команд\n/new_task - добавить новую задачу\n/todo_list - посмотреть список дел")
 
@bot.message_handler(commands=['newtask'])
def newtask(message):
    add_new_task(message)

@bot.message_handler(commands=['todolist'])
def todolist(message):
    print_todo_list(message)

@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text == BUTTONS[0]:
        add_new_task(message)
    elif message.text == BUTTONS[1]:
        print_todo_list(message)
    else:
        todo_list, chats_todo_list = get_todo_list(message.chat.id)
        new_task = Task(message.text)
        todo_list.append(new_task)
        new_message = bot.send_message(message.chat.id, f"✏️ Добавлена задача \n{new_task.name}", reply_markup=task_keyboard(new_task.id))
        new_task.message_id = new_message.id
        set_todo_list(chats_todo_list, todo_list, message.chat.id)

def day_select(call, id_task, day_index):
    todo_list, chats_todo_list = get_todo_list(call.message.chat.id)
    for i, task in enumerate(todo_list):
        if task.id == id_task:
            task.day = WEEK_BUTTONS[day_index]
            set_todo_list(chats_todo_list, todo_list, call.message.chat.id)
            bot.edit_message_text(f"🔸 Задача № {i + 1}. {task.name}\n{task.day} {task.time}", call.message.chat.id, call.message.message_id, reply_markup=task_keyboard(task.id))
            bot.answer_callback_query(call.id)

def time_select(call, id_task, time):
    todo_list, chats_todo_list = get_todo_list(call.message.chat.id)
    for i, task in enumerate(todo_list):
        if task.id == id_task:
            task.time = time
            set_todo_list(chats_todo_list, todo_list, call.message.chat.id)
            bot.edit_message_text(f"🔸 Задача № {i + 1}. {task.name}\n{task.day} {task.time}", call.message.chat.id, call.message.message_id, reply_markup=task_keyboard(task.id))
            bot.answer_callback_query(call.id)

def delete_task(call, id_task, new_text):
    todo_list, chats_todo_list = get_todo_list(call.message.chat.id)
    for task in todo_list:
        if task.id == id_task:
            todo_list.remove(task)
            set_todo_list(chats_todo_list, todo_list, call.message.chat.id)
            bot.edit_message_text(new_text, call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: True)
def handler(call):
    data = json.loads(call.data)
    id_task = data.get("id")
    action = data.get("action")
    if action == TASK_BUTTONS[0]:
        delete_task(call, id_task, "Задача выполнена ✅")
    elif action == TASK_BUTTONS[1]:
        delete_task(call, id_task, "Задача удалена ❌")
    elif action == TASK_BUTTONS[2]:
        bot.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id, reply_markup=day_keyboard(id_task))
    elif action == 'day':
        day_index = data.get("day_index")
        day_select(call, id_task, day_index)
    elif action == TASK_BUTTONS[3]:
        bot.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id, reply_markup=time_keyboard(id_task))
    elif action == 'time':
        time = data.get("time")
        time_select(call, id_task, time)


bot.polling(none_stop=True, interval=0)
