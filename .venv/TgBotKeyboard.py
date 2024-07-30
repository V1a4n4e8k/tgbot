from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from DataBaseSettings import get_csv_file_names
import os
csv_file_names = get_csv_file_names()




ClothesKb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text= csv_file_name) for csv_file_name in csv_file_names
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='вот что у нас есть',
    selective=True
)
AdminAddClothesKb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='добавить одежду'),
            KeyboardButton(text= 'удалить одежду'),
            KeyboardButton(text= 'удалить папку'),
            KeyboardButton(text= 'создать папку')
        ],
        [
            KeyboardButton(text = 'рассылка'),
            KeyboardButton(text='список забронированнолй одежды')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='выбирите действие',
    selective=True
)

AfterPressingStart = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='категории одежды'),
            KeyboardButton(text= 'о нас')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='выбирите действие',
    selective=True
)



def balance_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='пополнить', callback_data=f'add_balance')
    keyboard.adjust(1)
    return keyboard.as_markup()



def clothes_kb():
    items = [ 'куртки', 'штаны', 'кросовки']
    builder = ReplyKeyboardBuilder()
    [builder.button(text = item) for item in items]
    return builder.as_markup(resize_keyboard=True)
