from libs.sqlhandler import sqlconnect
from libs.qulib import string_generator
from main import bot_path
import sqlite3
import enum
import os


class SettlementAccess(enum.IntEnum):
    Public = 1
    Private = 2


class quConquest(object):

    def __init__(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS conquest(settlement_id INTEGER PRIMARY KEY ,invite_string BLOB,\
                    date_created BLOB,founderid BLOB,leaderid BLOB,name BLOB,treasury INTEGER,tech_attack INTEGER,\
                    tech_defence INTEGER, size INTEGER, tech_tree BLOB,\
                    type INTEGER,entry_fee INTEGER, wins INTEGER, losses INTEGER, experience INTEGER)")
            cursor.execute("CREATE TABLE IF NOT EXISTS members(userid INTEGER PRIMARY KEY, settlement_id INTEGER)")
            cursor.execute("CREATE TABLE IF NOT EXISTS resources(settlement_id INTEGER PRIMARY KEY, cloth INTEGER, wood INTEGER, stone INTEGER, food INTEGER)")
            cursor.execute("CREATE TABLE IF NOT EXISTS buildings(id INTEGER PRIMARY KEY, name BLOB, mltplr_cloth INTEGER, mltplr_food INTEGER, mltplr_stone INTEGER, mltplr_wood INTEGER, mltplr_gold INTEGER)")
            # Inserting buildings
            cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (1, 'Town Hall', 0, 1, 1, 1, 250,))
            cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (2, 'Training Grounds', 5, 5, 2, 2, 0,))
            cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (3, 'Market Square', 0, 0, 0, 0, 2500,))
            cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (4, 'Walls', 0, 0, 5, 5, 50,))
            cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (5, 'Quarry', 3, 3, 0, 0, 20))
            cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (6, 'Farms', 0, 0, 0, 7, 20))
            cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (7, 'Weavery', 0, 7, 0, 0, 5))
            cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (8, "Lumberjack's Camp", 2, 7, 0, 0, 5))
            cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (9, 'Warehouse', 0, 0, 0, 0, 5000))
            cursor.execute("INSERT OR IGNORE INTO buildings(id, name, mltplr_cloth, mltplr_food, mltplr_stone, mltplr_wood, mltplr_gold) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (10, 'Academy', 0, 0, 5, 5, 125))

    @staticmethod
    async def level_converter(item: str):
        return int(item) if item != "X" else 10

    @classmethod
    async def get_settlement(self, get_string: str, input_data):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            if get_string == 'user':
                cursor.execute("SELECT * FROM conquest WHERE leaderid=?", (input_data,))
            elif get_string == 'settlement':
                cursor.execute("SELECT * FROM conquest WHERE name=?", (input_data,))
            elif get_string == 'code':
                cursor.execute("SELECT * FROM conquest WHERE invite_string=?", (input_data,))
            elif get_string == 'id':
                cursor.execute("SELECT * FROM conquest WHERE settlement_id=?", (input_data,))
            elif get_string == 'member':
                cursor.execute("SELECT c.* FROM conquest as c INNER JOIN members as m ON c.settlement_id = m.settlement_id WHERE m.userid=?", (input_data,))
            else:
                return None

            db_output = cursor.fetchone()
            if db_output is None:
                return None
            else:
                db_output = list(db_output)
                return_dict = dict(settlement_id=db_output[0], invite_string=db_output[1], date_created=db_output[2], founderid=db_output[3],
                                   leaderid=db_output[4], name=db_output[5], treasury=db_output[6], tech_attack=db_output[7],
                                   tech_defence=db_output[8], size=db_output[9], tech_tree=db_output[10], type=db_output[11],
                                   entry_fee=db_output[12], wins=db_output[13], losses=db_output[14], experience=db_output[15])
                return return_dict

    @classmethod
    async def create_settlement(self, user_id: int, data: dict):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO conquest(founderid, leaderid, treasury, entry_fee, invite_string, date_created, tech_attack, tech_defence, name, tech_tree, type, size, wins, losses, experience) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           [user_id, user_id, data["entry_fee"], data["entry_fee"], data["invite_string"], data["date_created"], '0', '0', data["name"], '0000000000', data["type"], '1', 0, 0, 0])
            return cursor.lastrowid

    @classmethod
    async def update_settlement(self, get_string: str, input_actor, data: dict):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            if get_string == 'user':
                cursor.execute("UPDATE conquest SET leaderid=?, treasury=?, entry_fee=?, invite_string=?, date_created=?, tech_attack=?, tech_defence=?, name=?, tech_tree=?, type=?, size=?, wins=?, losses=?, experience=? WHERE leaderid=?",
                               [data["leaderid"], data["treasury"], data["entry_fee"], data["invite_string"], data["date_created"], data["tech_attack"], data["tech_defence"],
                                data["name"], data["tech_tree"], data["type"], data["size"], data["wins"], data["losses"], data["experience"], input_actor])
            elif get_string == 'invite':
                cursor.execute("UPDATE conquest SET leaderid=?, treasury=?, entry_fee=?, invite_string=?, date_created=?, tech_attack=?, tech_defence=?, name=?, tech_tree=?, type=?, size=?, wins=?, losses=?, experience=? WHERE invite_string=?",
                               [data["leaderid"], data["treasury"], data["entry_fee"], data["invite_string"], data["date_created"], data["tech_attack"], data["tech_defence"],
                                data["name"], data["tech_tree"], data["type"], data["size"], data["wins"], data["losses"], data["experience"], input_actor])
            elif get_string == 'id':
                cursor.execute("UPDATE conquest SET leaderid=?, treasury=?, entry_fee=?, invite_string=?, date_created=?, tech_attack=?, tech_defence=?, name=?, tech_tree=?, type=?, size=?, wins=?, losses=?, experience=? WHERE settlement_id=?",
                               [data["leaderid"], data["treasury"], data["entry_fee"], data["invite_string"], data["date_created"], data["tech_attack"], data["tech_defence"],
                                data["name"], data["tech_tree"], data["type"], data["size"], data["wins"], data["losses"], data["experience"], input_actor])
        return None

    @classmethod
    async def delete_settlement(self, settlement_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("DELETE FROM conquest WHERE settlement_id=?", (settlement_id,))
            cursor.execute("DELETE FROM members WHERE settlement_id=?", (settlement_id,))

    @classmethod
    def delete_data(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("DELETE FROM conquest")
            cursor.execute("DELETE FROM members")
            cursor.execute("DELETE FROM resources")

    @classmethod
    async def is_settlement(self, settlement_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("SELECT settlement_id FROM conquest WHERE settlement_id=?", (settlement_id,))
            output = cursor.fetchone()
            return True if output else False

    @classmethod
    async def get_leaderboard(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("SELECT settlement_id, name, experience, DENSE_RANK() OVER (ORDER BY experience DESC) as rank FROM conquest")
            output = cursor.fetchall()
            return output

    @classmethod
    async def get_rank(self, user_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("SELECT rank FROM (SELECT settlement_id, DENSE_RANK() OVER (ORDER BY experience DESC) as rank FROM conquest) as cq INNER JOIN members as m ON m.settlement_id = cq.settlement_id WHERE m.userid=?", (user_id,))
            output = cursor.fetchone()
            return output[0] if output else None

    @classmethod
    async def add_member(self, user_id: int, settlement_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO members(userid, settlement_id) VALUES(?, ?)", (user_id, None))
            cursor.execute("UPDATE members SET settlement_id=? WHERE userid=?", (settlement_id, user_id))

    @classmethod
    async def remove_member(self, user_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("DELETE FROM members WHERE userid=?", (user_id,))

    @classmethod
    async def find_member(self, user_id: int, settlement_id: int = None):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO members(userid, settlement_id) VALUES(?, ?)", (user_id, None))
            if settlement_id:
                cursor.execute("SELECT userid FROM members WHERE settlement_id=?", (settlement_id,))
            else:
                cursor.execute("SELECT settlement_id FROM members WHERE userid=?", (user_id,))
            db_output = cursor.fetchone()

            if settlement_id:
                return True if db_output != None else False
            else:
                return True if None not in {db_output, db_output[0]} else False

    @classmethod
    async def get_settlement_id(self, user_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO members(userid, settlement_id) VALUES(?, ?)", (user_id, None))
            cursor.execute("SELECT settlement_id FROM members WHERE userid=?", (user_id,))
            db_output = cursor.fetchone()
            return db_output[0] if db_output != None else None

    @classmethod
    async def generate_new_code(self, user_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            new_code = string_generator(15)
            cursor.execute("SELECT invite_string FROM conquest WHERE invite_string=?", (new_code,))

            while cursor.fetchone():
                new_code = string_generator(15)
                cursor.execute("SELECT invite_string FROM conquest WHERE invite_string=?", (new_code,))

            cursor.execute("UPDATE conquest SET invite_string=? WHERE leaderid=?", (new_code, user_id,))
            return True if cursor.rowcount > 0 else False

    @classmethod
    async def get_unique_code(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            new_code = string_generator(15)
            cursor.execute("SELECT invite_string FROM conquest WHERE invite_string=?", (new_code,))

            while cursor.fetchone():
                new_code = string_generator(15)
                cursor.execute("SELECT invite_string FROM conquest WHERE invite_string=?", (new_code,))

            return new_code

    @classmethod
    async def get_code(self, user_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("SELECT invite_string FROM conquest WHERE leaderid=?", (user_id,))
            db_output = cursor.fetchone()
            return db_output[0] if db_output != None else None

    @classmethod
    async def get_resources(self, settlement_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("INSERT OR IGNORE INTO resources(settlement_id, cloth, wood, stone, food) VALUES(?, ?, ?, ?, ?)", (settlement_id, 0, 0, 0, 0,))
            cursor.execute("SELECT * FROM resources WHERE settlement_id=?", (settlement_id,))
            db_output = cursor.fetchone()
            if db_output is None:
                return None
            else:
                db_output = list(db_output)
                return_dict = dict(settlement_id=db_output[0], cloth=db_output[1], wood=db_output[2], stone=db_output[3], food=db_output[4])
                return return_dict

    @classmethod
    async def update_resources(self, settlement_id: int, data):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("UPDATE resources SET cloth=?, wood=?, stone=?, food=? WHERE settlement_id=?", (data["cloth"], data["wood"], data["stone"], data["food"], settlement_id,))
            return True if cursor.rowcount > 0 else False

    @classmethod
    async def send_resource_dailies(self):
        conn = sqlite3.connect(os.path.join(bot_path, 'databases', 'conquest.db'))
        cursor = conn.cursor()
        cursor_update = conn.cursor()
        cursor.row_factory = sqlite3.Row
        for row in cursor.execute("SELECT r.settlement_id, r.cloth, r.wood, r.stone, r.food, c.tech_tree FROM resources AS r INNER JOIN conquest AS c ON r.settlement_id=c.settlement_id"):
            row_info = list(row)
            tech_tree = row_info[5]
            # Indexes: 4 = quarry; 5 = farms ; 6 = weavery; 7 = lumberjack; 8 = warehouse
            for i in range(1, 5):
                row_info[i] += pow(await quConquest.level_converter(tech_tree[3 + i]), 2)
                if int(tech_tree[8]) == 0:
                    row_info[i] = row_info[i] if row_info[i] <= 1000 else 1000
            cursor_update.execute("UPDATE resources SET cloth=?, wood=?, stone=?, food=? WHERE settlement_id=?", (row_info[1], row_info[2], row_info[3], row_info[4], row_info[0]))
        conn.commit()
        conn.close()

    @classmethod
    async def get_resource_production_rate(self, building_id: int, settlement_id: int):
        if 5 <= building_id <= 8:
            with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
                cursor.execute("SELECT tech_tree FROM conquest WHERE settlement_id=?", (settlement_id,))
                db_output = cursor.fetchone()
                if db_output is None:
                    return None
                else:
                    tech_tree = db_output[0]
                    return pow(await quConquest.level_converter(tech_tree[building_id - 1]), 2)

    # Settlement Buildings

    @classmethod
    async def get_building(self, building_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("SELECT * FROM buildings WHERE id=?", (building_id,))
            db_output = cursor.fetchone()
            if db_output is None:
                return None
            else:
                db_output = list(db_output)
                return_dict = dict(id=db_output[0], name=db_output[1], cloth=db_output[2], food=db_output[3], stone=db_output[4], wood=db_output[5], gold=db_output[6])
                return return_dict

    @classmethod
    async def get_buildings(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM buildings")
            db_output = [dict(row) for row in cursor.fetchall()]
            return db_output

    @classmethod
    async def get_building_names(self):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("SELECT id, name name FROM buildings")
            output = cursor.fetchall()
            return {x[1].lower(): x[0] for x in output} if output else None

    @classmethod
    async def upgrade_building(self, settlement_id: int, building_id: int):
        with sqlconnect(os.path.join(bot_path, 'databases', 'conquest.db')) as cursor:
            cursor.execute("SELECT tech_attack, tech_defence, tech_tree FROM conquest WHERE settlement_id=?", (settlement_id,))
            tech_points = cursor.fetchone()
            if tech_points:
                tech_points = list(tech_points)
                level = await quConquest.level_converter(tech_points[2][building_id - 1])
                new_points = int(pow(1.638, level))
                if building_id == 2:
                    tech_points[0] += new_points
                elif building_id == 4:
                    tech_points[1] += new_points
                elif building_id == 10:
                    new_points = int(pow(1.48, level))
                    tech_points[0] += new_points
                    tech_points[1] += new_points
                cursor.execute("UPDATE conquest SET tech_attack=?, tech_defence=? WHERE settlement_id=?", (tech_points[0], tech_points[1], settlement_id,))
