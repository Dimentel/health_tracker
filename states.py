from aiogram.fsm.state import State, StatesGroup


class UserProfile(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()


class FoodCalories(StatesGroup):
    product_name = State()
    calories_per_100g = State()
    amount = State()
