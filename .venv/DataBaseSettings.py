import os
import sqlite3
import string
import random
import pandas as pd

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def user_exist(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchmany(1)
            return bool(len(result))
    
    def select_user_id(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchmany(1)
            return result
        
    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute('INSERT INTO `users` (`user_id`) VALUES (?)', (user_id,))

    def get_users(self):
        with self.connection:
            return self.cursor.execute('SELECT `user_id` FROM users').fetchall()

def get_csv_file_names():
    file_names = os.listdir('C:\\tgbot\\')
    csv_file_names = []
    for item in file_names:
        if '.csv' in item:
            csv_file_names.append(item.rstrip('.csv'))
    return csv_file_names

def generate_unique_string(length, from_file, csv_file_names):
    df = pd.read_csv(from_file + '.csv', index_col=0)
    characters = string.ascii_letters + string.digits
    if from_file in csv_file_names:
        while True:
            result = ''.join(random.choice(characters) for _ in range(length))
            if result not in df['unique_item_id'].values:
                return result
                break
