from data.config import ADMIN_LIST
from keyboards.main import create_reply_keyboard, create_inline_keyboard, BACK_BTN_TEXT


def main_keyboard(user_id):
    buttons_matrix = [
        ('📝 Создать сделку', ' 📤 Отправить отчет'),
        ('👤 Профиль', '🦹‍♂️ Написать поддержке'),
        ('🧾 Правила бота', '👑 Топ воркеров')
        ]
    if user_id in ADMIN_LIST:
        buttons_matrix.append(('🙆‍♂️ Админка',))
    return create_reply_keyboard(buttons_matrix)

def profile_keyboard():
    buttons_matrix = [
        [('💳 История сделок', 'orders_history;profile;1')],
        [('🗂 История отчетов', 'reports_history;profile;1')],
        ]
    
    return create_inline_keyboard(buttons_matrix)

def new_order_keyboard():
    buttons_matrix = [
        [(ADMIN_LIST[admin_id], f'new_order_select_admin;{admin_id}',)] for admin_id in ADMIN_LIST
        ]
    
    return create_inline_keyboard(buttons_matrix)

def new_order_add_comment_keyboard():
    buttons_matrix = [
        [('Пропустить', 'skip_add_comment')],
        [(BACK_BTN_TEXT, 'new_order')],
        ]
    
    return create_inline_keyboard(buttons_matrix)

def new_report_keyboard():
    buttons_matrix = [
        [(ADMIN_LIST[admin_id], f'new_report_select_admin;{admin_id}',)] for admin_id in ADMIN_LIST
        ]
    
    return create_inline_keyboard(buttons_matrix)

def new_report_add_file(back_callback):
    buttons_matrix = [
        [('Пропустить', f'skip_add_file;{back_callback}')],
        [(BACK_BTN_TEXT, back_callback)],
        ]
    
    return create_inline_keyboard(buttons_matrix)

def support_keyboard(chat_id):
    buttons_matrix = [
        [('Ответить', f'support_answer;{chat_id}')],
        ]
    
    return create_inline_keyboard(buttons_matrix)
