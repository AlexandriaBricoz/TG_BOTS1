from aiogram.types import (
	KeyboardButton,
	Message,
	ReplyKeyboardMarkup,
	ReplyKeyboardRemove,
	InlineKeyboardMarkup,
	InlineKeyboardButton
)

from data.config import *
from utils.other import convert_unix_to_msk

BACK_BTN_TEXT = '⬅️ Назад'

def create_reply_keyboard(buttons_matrix):
	"""
	Создает кастомную клавиатуру на основе списка списков кнопок.

	:param buttons_matrix: Список списков с названиями кнопок для каждого ряда.
	"""
	keyboard = []

	for row in buttons_matrix:
		keyboard_row = [KeyboardButton(text=btn) for btn in row]
		keyboard.append(keyboard_row)

	markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
	return markup

def create_inline_keyboard(buttons_matrix):
    """
    Создает кастомную инлайн-клавиатуру на основе списка списков кнопок, 
    распределяя кнопки по рядам с максимум 2 кнопками в каждом ряду.

    :param buttons_matrix: Список списков с данными для каждой кнопки. 
                           Каждая кнопка представлена как кортеж (текст, callback_data).
    """
    keyboard = []

    for row in buttons_matrix:
        # Разбиваем длинные ряды на подряды по 2 кнопки
        for i in range(0, len(row), 3):
            keyboard_row = [InlineKeyboardButton(text=text, callback_data=callback_data) 
                            for text, callback_data in row[i:i + 3]]
            keyboard.append(keyboard_row)

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup

def back_to_keyboard(callback_data, text=BACK_BTN_TEXT):
    if not callback_data: return None
    
    buttons_matrix = [[(text, callback_data)]]
    return create_inline_keyboard(buttons_matrix)


def page_keyboard(all_items, page, page_callback, select_callback, back_callback, items_type, add_button_text=None, add_button_callback_data=None, items_in_page_count=10):
    buttons_matrix = []
    
    items_total = len(all_items)
    pages_count = -(-items_total // items_in_page_count)

    if not (0 < page <= pages_count):
        return False

    start_index = (page - 1) * items_in_page_count
    end_index = start_index + items_in_page_count
    page_items = all_items[start_index:end_index]

    for items in page_items:

        
        if items_type == 'orders_history':
            num, amount, create_time, status = items

            if status == 'pending':
                status_icon = '🟡'
            elif status == 'finished':
                status_icon = '✅'
            else:
                status_icon = '❌'
            msk_date = convert_unix_to_msk(create_time)
            message_text = f'{status_icon} | {msk_date} | {amount}'

        elif items_type == 'reports_history':
            num, create_time, edited_status = items

            icon = '📝' if edited_status else '📄'

            msk_date = convert_unix_to_msk(create_time)
            message_text = f'{icon} | {msk_date}'

        elif items_type == 'all_users':
            user_id, username = items
            message_text = f'{user_id} | {username}'
            num = user_id


        buttons_matrix.append([(message_text, f'{select_callback};{num};{page}')])

    prev_page = max(page - 1, 1)
    next_page = min(page + 1, pages_count)

    if page == pages_count:
        middle_btn_page = 1
    else:
        middle_btn_page = pages_count

    buttons_matrix.append(
            [
                ('⬅️', f'{page_callback};{prev_page}'),
                (f'{page}/{pages_count}', f'{page_callback};{middle_btn_page}'),
                ('➡️', f'{page_callback};{next_page}')
            ]
        )


    if add_button_text and add_button_callback_data:
        buttons_matrix.append([(add_button_text, add_button_callback_data)])

    if back_callback:
        buttons_matrix.append([(BACK_BTN_TEXT, back_callback)])

    return create_inline_keyboard(buttons_matrix)


def report_keyboard(order_num, back_callback, page=1):
    buttons_matrix = []


    buttons_matrix += [
        [('📝 Изменить', f'edit_report;{back_callback};{order_num};{page}')],
    ]

    buttons_matrix.append([(BACK_BTN_TEXT, f'reports_history;{back_callback};1')])

    return create_inline_keyboard(buttons_matrix)