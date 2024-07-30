from config import TOKEN, SBER_TOKEN
from aiogram import Bot, Dispatcher, types, F
import asyncio
from aiogram.filters import CommandStart
from aiogram.types import LabeledPrice, PreCheckoutQuery
import TgBotKeyboard
import pandas as pd
from aiogram.fsm.context import FSMContext
from utils.states import delete_clothes, add_clothes, user_choose_clothes, create_or_delete_folder, send_to_all_users
from DataBaseSettings import get_csv_file_names, generate_unique_string
from importlib import reload
import os
from DataBaseSettings import Database
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

df2 = pd.DataFrame(columns=['discription', 'photo_id', 'unique_item_id', 'is_taken'])
price = [LabeledPrice(label = 'зарезервировать', amount = 50000)]
db = Database('users.sql')
tgbot =Bot(token=TOKEN)
dp = Dispatcher()
photo_id = 0
ItemsInfo = ''
df = pd.DataFrame(columns=['discription', 'photo_id', 'unique_item_id', 'is_taken'])
csv_file_names = get_csv_file_names()
choosen_fail_to_add = ''
choosen_file_to_delete = ''
unique_id = ''
#!2.1! старт команда
@dp.message(CommandStart())
async def start(message: types.Message):
    if message.chat.type == 'private':
        if not db.user_exist(message.from_user.id):
            db.add_user(message.from_user.id)
    await message.answer(text ='здравствуйте, это магзин одежды DenBox', reply_markup=TgBotKeyboard.AfterPressingStart)
#!2.1! старт команда
#!2.2! выдать список категории одежды и список одежды
@dp.message(F.text == 'категории одежды')
async def show_clothes(message: types.Message, state: FSMContext):
    await state.set_state(user_choose_clothes.start_choosing)
    await message.answer(text= 'какой товар вас интересует?', reply_markup=TgBotKeyboard.ClothesKb)

@dp.message(user_choose_clothes.start_choosing)
async def show_kurtki(message: types.Message, state: FSMContext):
    csv_file_names = get_csv_file_names()
    global unique_id, df2
    if message.text in csv_file_names:
        df2 = pd.read_csv(message.text + '.csv', index_col=0)
        for index, row in df2.iterrows():
            await message.answer(text = row['discription'])
            unique_id = row['unique_item_id']
            PayKb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Зарезервировать одежду', callback_data= 'reserve_'+ row['unique_item_id'] )]])
            await message.answer_photo(photo=row['photo_id'], reply_markup=PayKb)
    await message.answer(text='Зарезервировать одежду стоит 500р. Эта сумма будет вычтена из стоимости товара, когда вы придете за ним в секонд. Если вы не придете в течении недели деньги возвращены не будут', reply_markup=TgBotKeyboard.AfterPressingStart)
#!2.2! выдать список категории одежды и список одежды
#!2.3! колбек с кнопки зарезервировать одежду
@dp.callback_query(lambda c: c.data.startswith('reserve_'))
async def reserve_clothing(callback: types.CallbackQuery):
    global unique_id
    unique_id = callback.data.split('_')[1]
    if df2['is_taken'].loc[df2.index[df2['unique_item_id'] == unique_id].tolist()].values == False:
        await tgbot.send_invoice(chat_id = callback.message.chat.id, title= 'reserve', description = 'desc', payload = 'some_invoice', currency = 'rub', prices = price, need_email = True, start_parameter = 'example', provider_token = SBER_TOKEN)
        await callback.answer(' ')
    else:
        await tgbot.send_message(chat_id = callback.message.chat.id, text='предмет уже зарезервирован')
        await callback.answer(' ')
@dp.pre_checkout_query(lambda query: True)
async def pre_checkout_process(pre_checkout: PreCheckoutQuery):
    await tgbot.answer_pre_checkout_query(pre_checkout.id, ok = True)

@dp.message(F.successful_payment)
async def sucsessfull_payment(message: types.Message):
    await tgbot.send_message(message.chat.id, text='платеж прошел успешно, вот ваш код -' + unique_id)
    df2.loc[df2['unique_item_id' == unique_id].index, 'is_taken'].values = True
#!2.3! колбек с кнопки зарезервировать одежду
#!2.4! about
@dp.message(F.text == 'о нас')
async def start(message: types.Message):
    await message.answer(text='**** - наш адрес')
    await message.answer(text='**** - номер для связи')
    await message.answer(text='мы работаем с xx:xx до xx:xx', reply_markup=TgBotKeyboard.AfterPressingStart)
#!2.4! about



#комманды доступные только админу НАЧАЛО !1!
@dp.message((F.chat.id == 1090048585) & (F.text == 'вызвать панель админа'))
async def admin_panel(message: types.Message):
    await message.answer(text = 'выбирите действие', reply_markup=TgBotKeyboard.AdminAddClothesKb)
    
#рассылка!6!
@dp.message(F.text == 'рассылка', F.chat.id == 1090048585)
async def sendall_set_state(message: types.Message, state: FSMContext):
    await message.answer(text = 'введите сообщение, которое хотите отправить всем пользователям бота')
    await state.set_state(send_to_all_users.start_sending)
@dp.message(send_to_all_users.start_sending)
async def start_sending(message: types.Message):
    text_to_send = message.text
    users = db.get_users()
    for row in users:
        await tgbot.send_message(row[0], text_to_send)
#рассылка!6!

#выведение списка забронированной одежды !7!
@dp.message(F.text == 'список забронированной одежды', F.chat.id == 1090048585)
async def taken_clothes(message: types.Message):
    for file in csv_file_names:
        df = pd.read_csv(file, index_col=0)
        for index, row in df.iterrows():
            if row['is_taken'] == True:
                await message.answer(text = row['unique_item_id'] + '  :  ' + row['discription'])
                await message.answer_photo(text = row['photo_id'])

#выведение списка забронированной одежды !7!

#создание файла для одежды !4!
@dp.message(F.text  == 'создать папку', F.chat.id == 1090048585)
async def start_creating_folder(message: types.Message, state: FSMContext):
    await state.set_state(create_or_delete_folder.creating_folder)
    await message.answer(text='Введите название папки, которую хотите создать. Название должно содержать ТОЛЬКО символы латиницы и кирилицы, любые вспомогательные знаки(пробелы, точки и тд) ЗАПРЕЩЕНЫ, ЛЮБОЕ НЕСООТВЕТСТВИЕ ИНСТРУКЦИИ ВЫЗОВЕТ ОШИБКУ')

@dp.message(create_or_delete_folder.creating_folder)
async def create_folder(message: types.Message, state: FSMContext):
    folder_to_create = message.text + '.csv'
    new_folder = pd.DataFrame(columns=['discription', 'photo_id', 'unique_item_id'])
    new_folder.to_csv(folder_to_create, index_label='index')
    await message.answer(text='не забудьте добавить в новую папку обьект')
    await state.set_state()
    await message.answer(text='.', reply_markup=TgBotKeyboard.AdminAddClothesKb)
    reload(TgBotKeyboard)   
#создание файла для одежды !4!

#удаление файла с одеждой !5!
@dp.message(F.text == 'удалить папку', F.chat.id == 1090048585)
async def start_deleting_folder(message: types.Message, state: FSMContext):
    await state.set_state(create_or_delete_folder.deleting_folder)
    await message.answer(text='выберите папку, которую хотите удалить', reply_markup=TgBotKeyboard.ClothesKb)

@dp.message(create_or_delete_folder.deleting_folder)
async def create_folder(message: types.Message, state: FSMContext):
    folder_to_delete = message.text + '.csv'
    os.remove(folder_to_delete)
    await message.answer(text='папка успешно удалена', reply_markup=TgBotKeyboard.AdminAddClothesKb)
    reload(TgBotKeyboard)
    await state.set_state()
#удаление файла с одеждой !5!

#удаление одежды из базы данных !2!
@dp.message(F.text == 'удалить одежду', F.chat.id == 1090048585)
async def delete_pos(message: types.Message, state: FSMContext):
    await state.set_state(delete_clothes.delete_from_file)
    await message.answer(text='введите номер одежды, которую хотите удалить', reply_markup=TgBotKeyboard.ClothesKb)

@dp.message(delete_clothes.delete_from_file)
async def chose_file_to_delete(message: types.Message, state: FSMContext):
    global choosen_file_to_delete, df
    choosen_file_to_delete = message.text
    df = pd.read_csv(choosen_file_to_delete + '.csv', index_col=0)
    clothes_info = str(df)
    await message.answer(text = clothes_info)
    await state.set_state(delete_clothes.index_to_delete)
    await message.answer(text= 'теперь введите номер позиции, которую хотите удалить')

@dp.message(delete_clothes.index_to_delete)
async def delete_index(message: types.Message, state = FSMContext):
    global df, choosen_file_to_delete
    index_to_drop = int(message.text)
    df = pd.read_csv(choosen_file_to_delete + '.csv', index_col=0)
    df = df.drop(index=index_to_drop, axis=1)
    df.to_csv(choosen_file_to_delete + '.csv', index_label= 'index')
    await message.answer(text='удаление прошло успешно')
    await state.set_state()
#удаление одежды из базы данных !2!

#добавление одежды в базу данных !3!
@dp.message(F.text == 'добавить одежду', F.chat.id == 1090048585)
async def add_position(message: types.Message, state: FSMContext):
    await state.set_state(add_clothes.choose_fail_to_add)
    await message.answer(text =  'сначала выбирите категорию', reply_markup=TgBotKeyboard.ClothesKb)
    
    

@dp.message(add_clothes.choose_fail_to_add)
async def choose_category(message: types.Message, state : FSMContext):
    global choosen_fail_to_add
    choosen_fail_to_add = message.text
    await message.answer(text= ' теперь отправьте фото')
    await state.set_state(add_clothes.clothes_photo_id)

@dp.message(add_clothes.clothes_photo_id)
async def add_photo(message: types.Message, state: FSMContext):
    global photo_id
    photo_data = message.photo[-1]
    photo_id = photo_data.file_id
    await message.answer(text= 'теперь отправьте описание')
    await state.set_state(add_clothes.clothes_discription)


@dp.message(add_clothes.clothes_discription)
async def add_photo(message: types.Message, state: FSMContext):
    global photo_id, df,choosen_fail_to_add, unique_id
    ItemDiscription = message.text
    df = pd.read_csv(choosen_fail_to_add + '.csv', index_col=0)
    unique_id =  generate_unique_string(length = 6, from_file = choosen_fail_to_add, csv_file_names = csv_file_names)
    full_info = {'discription' : ItemDiscription, 'photo_id' : photo_id, 'unique_item_id': unique_id, 'is_taken': False}
    df = df._append(full_info, ignore_index=True)
    df.to_csv(choosen_fail_to_add + '.csv', index_label= 'index')
    await message.answer(text= 'добавлено')
    await state.set_state()
# добавление одежды в базу данных !3!
# КОНЕЦ !1!
        



    


async def main():
    await dp.start_polling(tgbot)

    

asyncio.run(main())

