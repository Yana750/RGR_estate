from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    username = State()
    filter_city = State()
    filter_category = State()
    mail_rass = State()
    Send_msg_mail = State()
    cancel = State()


if __name__ == '__main__':
    print(Form.all())