from aiogram.fsm.state import StatesGroup, State


class add_clothes(StatesGroup): 
    clothes_discription = State()
    clothes_photo_id = State()
    choose_fail_to_add = State()

class delete_clothes(StatesGroup):
    index_to_delete = State()
    delete_from_file = State()

class user_choose_clothes(StatesGroup):
    start_choosing = State()

class create_or_delete_folder(StatesGroup):
    creating_folder = State()
    deleting_folder = State()

class send_to_all_users(StatesGroup):
    start_sending= State()