from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    username = State()
    filter_city = State()
    filter_category = State()
    mail_rass = State()
    add_filter =State()
    Results = State()

class UserAgreement(StatesGroup):
    is_agree = State()


if __name__ == '__main__':
    print(Form.all())