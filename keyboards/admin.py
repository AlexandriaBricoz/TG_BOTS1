from data.config import ADMIN_LIST
from keyboards.main import BACK_BTN_TEXT, create_reply_keyboard, create_inline_keyboard


def admin_keyboard():
    buttons_matrix = [
        [('📤 Рассылка', 'distribution'), ('👥 Пользователи', 'all_users;1')],
        [('📑 История сделок', 'orders_history;admin;1'), ('🗂 История отчетов', 'reports_history;admin;1')],       
        [('🖨 Выгрузить отчеты', 'download_reports'),],

    ]
    return create_inline_keyboard(buttons_matrix)

def user_page_keyboard(user_id, ban_status, page):
    buttons_matrix = [
        [('💳 История сделок', f'orders_history;select_user;{user_id};{page};{page}')],
        [('🗂 История отчетов', f'reports_history;select_user;{user_id};{page};{page}')],
        [('💸 Изменить баланс', f'update_user_balance;{user_id};{page}')],
        [('🔓 Разблокировать', f'update_user_ban_status;{user_id};0;{page}') if ban_status else ('🔒 Заблокировать', f'update_user_ban_status;{user_id};1;{page}')],   
        [(BACK_BTN_TEXT, f'all_users;{page}')]
    ]
    return create_inline_keyboard(buttons_matrix)

def accept_update_user_ban_status_keyboard(user_id, page):
    buttons_matrix = [
        [('Да', 'accept_update_user_ban_status')],
        [(BACK_BTN_TEXT, f'select_user;{user_id};{page}')],
        ]
    return create_inline_keyboard(buttons_matrix)

def order_keyboard(order_num, status, back_callback=None, page=1):
    buttons_matrix = []

    if status == 'pending':
        buttons_matrix += [
            [('🟢 Принять', f'accept_order;{order_num};{page}')],
            [('🔴 Отклонить', f'cancel_order;{order_num};{page}')],
        ]

    if back_callback:
        buttons_matrix.append([(BACK_BTN_TEXT, f'orders_history;{back_callback};1')])

    return create_inline_keyboard(buttons_matrix)

def cancel_order_skip_reason_keyboard(order_num, page):
    buttons_matrix = [
        [('Пропустить', 'skip_add_cancel_order_reason')],
        [(BACK_BTN_TEXT, f'select_order;admin;{order_num};{page}')],
        ]
    
    return create_inline_keyboard(buttons_matrix)