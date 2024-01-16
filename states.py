from aiogram.fsm.state import State, StatesGroup

class Distribution(StatesGroup):
    get_message = State()

class UpdateUserBalance(StatesGroup):
    get_balance = State()

class NewOrder(StatesGroup):
    get_amount = State()
    get_comment = State()

class BanUser(StatesGroup):
    get_reason = State()
    get_accept_answer = State()

class AcceptOrder(StatesGroup):
    get_check = State()

class CahncelOrder(StatesGroup):
    get_reason = State()

class Support(StatesGroup):
    get_message = State()

class NewReport(StatesGroup):
    get_data = State()
    get_file = State()

class DownloadReports(StatesGroup):
    get_day = State()