from aiogram.fsm.state import State, StatesGroup


class AddSubscriptionStates(StatesGroup):
    service_name = State()
    price = State()
    currency = State()
    period = State()
    custom_period = State()
    billing_date = State()
    cancel_url = State()


class EditSubscriptionStates(StatesGroup):
    select_field = State()
    edit_value = State()
