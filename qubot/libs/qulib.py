from libs.sqlhandler import sqlconnect
import sqlite3
import discord
import os
import sys
import random
import string
import json

bot_path = os.path.join(os.getcwd(), 'qubot')

#Check if the bot is running inside a virtual environment
def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def makefolders(root_path, folders_list):
    for folder in folders_list:
        os.makedirs(os.path.join(root_path, folder), exist_ok=True)

def safe_cast(value, to_type, default=None):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default

#data.json initialization
def sync_data_get():
    with open(os.path.join(bot_path, 'data/data.json'), 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    return json_data

async def data_get():
    with open(os.path.join(bot_path, 'data/data.json'), 'r') as json_file:
        json_data = json.load(json_file)
    json_file.close()
    return json_data

def sync_data_set(json_dump: dict):
    with open(os.path.join(bot_path, 'data/data.json'), 'w') as json_file: 
        json.dump(json_dump, json_file, indent=4, sort_keys=True,separators=(',', ': '))
    json_file.close()

async def data_set(json_dump: dict):
    with open(os.path.join(bot_path, 'data/data.json'), 'w') as json_file: 
        json.dump(json_dump, json_file, indent=4, sort_keys=True,separators=(',', ': '))
    json_file.close()

#Database folder creation(if missing) #TODO: Delete in the future (duplicate code <-> main.py)
if not os.path.exists(os.path.join(bot_path, 'databases')):
    os.makedirs(os.path.join(bot_path, 'databases'), exist_ok=True)

#Creating needed database files(if missing)
def user_database_init():
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users(userid INTEGER PRIMARY KEY , currency INTEGER, daily_time BLOB)")
        cursor.execute("CREATE TABLE IF NOT EXISTS giveaway_participants(userid INTEGER, msgid INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS giveaways(msgid INTEGER, value INTEGER)")

async def user_get(user: discord.User):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("INSERT OR IGNORE INTO users(userid, currency) VALUES(?, ?)", (user.id, '0'))
        cursor.execute("SELECT IfNull(currency,0), IfNull(daily_time,0) FROM users WHERE userid=?", (user.id,))
        db_output = list(cursor.fetchone())
        return_dict = dict(currency=db_output[0], daily_time=db_output[1])
        return return_dict

async def user_set(user: discord.User, dict_input):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("INSERT OR IGNORE INTO users(userid, currency) VALUES(?, ?)", (user.id, '0'))
        cursor.execute("UPDATE users SET currency=?, daily_time=? WHERE userid=?",
                        (dict_input['currency'], dict_input['daily_time'], user.id))
   
def string_generator(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

#Giveaway (Economy)

async def start_giveaway(msg_id: int, value: int):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("INSERT OR IGNORE INTO giveaways(msgid, value) VALUES(?, ?)", (msg_id, value,))

async def get_giveaway_value(msg_id: int):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("SELECT value FROM giveaways WHERE msgid=?", (msg_id,))
        db_output = cursor.fetchone()
        if db_output:
            db_output = list(db_output)
            return db_output[0] if db_output else None
        else:
            return None

async def get_giveaway_list():
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("SELECT msgid FROM giveaways")
        db_output = cursor.fetchall()
        return list(db_output[0]) if db_output else None

async def has_entered_giveaway(user_id: int, msg_id: int):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("SELECT rowid FROM giveaways WHERE msgid=?", (msg_id,))
        check = cursor.fetchone()
        if check:
            cursor.execute("SELECT rowid FROM giveaway_participants WHERE userid=? AND msgid=?", (user_id, msg_id,))
            db_output = cursor.fetchone()
            return True if db_output else False
        else:
            return None

async def enter_giveaway(user_id: int, msg_id: int):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("INSERT OR IGNORE INTO giveaway_participants(userid, msgid) VALUES(?, ?)", (user_id, msg_id,))

async def end_giveaway(msg_id: int):
    with sqlconnect(os.path.join(bot_path, 'databases', 'users.db')) as cursor:
        cursor.execute("DELETE FROM giveaway_participants WHERE msgid=?", (msg_id,))
        cursor.execute("DELETE FROM giveaways WHERE msgid=?", (msg_id,))
        result = cursor.rowcount
        return True if result > 0 else False