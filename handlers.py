from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from states import *
from utils import *

router = Router()
users = {}


# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply(
        "Добро пожаловать! Я ваш бот-помощник.\n"
        "Помогу рассчитать дневные нормы\n"
        "воды и калорий, а также отслеживать\n"
        "тренировки и питание.\n"
        "Введите /help, чтоб посмотреть доступные команды:\n"
    )


# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Могу работать с командами:\n"
        "/start - начать работу\n"
        "/help - помощь\n"
        "/set_profile - настроить профиль\n"
        "/log_water <количество, мл> - запись и контроль выпитой воды\n"
        "/log_food <название продукта> - запись продукта и его калорийности\n"
        "/log_workout <тип тренировки> <время, мин> - запись тренировки\n"
        "/check_progress - проверка прогресса\n"
    )


# Обработчик команды /set_profile
# Заполнение формы с профилем пользователя. Вес
@router.message(Command("set_profile"))
async def profile_weight(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (в кг):\n")
    await state.set_state(UserProfile.weight)


# Заполнение формы с профилем пользователя. Рост
@router.message(UserProfile.weight)
async def profile_height(message: Message, state: FSMContext):
    await state.update_data(weight=float(message.text))
    await message.reply("Введите ваш рост (в см):\n")
    await state.set_state(UserProfile.height)


# Заполнение формы с профилем пользователя. Возраст
@router.message(UserProfile.height)
async def profile_age(message: Message, state: FSMContext):
    await state.update_data(height=float(message.text))
    await message.reply("Введите ваш возраст:\n")
    await state.set_state(UserProfile.age)


# Заполнение формы с профилем пользователя. Активность
@router.message(UserProfile.age)
async def profile_activity(message: Message, state: FSMContext):
    await state.update_data(age=float(message.text))
    await message.reply("Сколько минут активности у вас в день?\n")
    await state.set_state(UserProfile.activity)


# Заполнение формы с профилем пользователя. Активность
@router.message(UserProfile.activity)
async def profile_activity(message: Message, state: FSMContext):
    await state.update_data(activity=float(message.text))
    await message.reply("В каком городе вы поживаете?\n")
    await state.set_state(UserProfile.city)


# Заполнение формы с профилем пользователя. Город проживания
@router.message(UserProfile.city)
async def profile_city(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    weight = data.get('weight')
    height = data.get('height')
    age = data.get('age')
    activity = data.get('activity')
    city = message.text
    cur_temp = await current_temperature(city)
    if cur_temp > 35:
        add_water = 1000
    elif cur_temp > 25:
        add_water = 500 + 50 * (cur_temp - 25)
    else:
        add_water = 0
    user = {
            "weight": weight,
            "height": height,
            "age": age,
            "activity": activity,
            "city": city,
            "water_goal": 30 * weight + add_water,  # на данном этапе прибавка от тренировок нулевая
            "calorie_goal": 10 * weight + 6.25 * height - 5 * age,  # на данном этапе прибавка от тренировок нулевая
            "logged_water": 0,
            "logged_calories": 0,
            "burned_calories": 0
        }
    users[user_id] = user
    await message.reply(
        f"Профиль id{user_id} заполнен!\n"
        f"Ваш вес: {weight} кг\nВаш рост: {height} см\nВаш возраст: {age} лет\n"
        f"Ваш активность: {activity} минут\nВаш город проживания: {city}")
    await state.clear()


# Обработчик команды /log_water <количество>
@router.message(Command("log_water"))
async def cmd_log_water(
        message: Message,
        command: CommandObject
):
    user_id = message.from_user.id
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None :
        await message.reply(
            "Ошибка: не указали количество воды в мл. Пример:\n"
            "/log_water 100"
        )
        return
    # Если аргумент не число, то ошибка
    if command.args.isdigit() is False:
        await message.reply(
            "Ошибка: количество воды указано не числом в мл. Пример:\n"
            "/log_water 100"
        )
        return

    water_amount = int(command.args)
    users[user_id]["logged_water"] += water_amount
    estimated_water = users[user_id]["water_goal"] - users[user_id]["logged_water"]
    await message.reply(
        f"Записано {water_amount} мл. воды\n"
        f"Осталось выпить сегодня {estimated_water} мл. воды\n"
    )


# Обработчик команды /log_food <название продукта>
@router.message(Command("log_food"))
async def cmd_log_food(
        message: Message,
        command: CommandObject,
        state: FSMContext
):
    user_id = message.from_user.id
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None :
        await message.reply(
            "Ошибка: не указали название продукта. Пример:\n"
            "/log_food banana"
        )
        return
    # Если аргумент число, то ошибка
    if command.args.isdigit() is True:
        await message.reply(
            "Ошибка: название продукта указано числом. Пример:\n"
            "/log_food banana"
        )
        return

    food_name = command.args
    food_info = await get_food_info(food_name)
    if food_info is not None:
        product_name = food_info["name"]
        calories_per_100g = food_info["calories"]
        await message.reply(f"{product_name} — {calories_per_100g} ккал на 100 г. Сколько грамм вы съели?\n")
        await state.update_data(product_name=product_name,
                                calories_per_100g=calories_per_100g)
    else:
        await message.reply("Не удалось получить данные о калорийности. Попробуйте другой продукт.")

    await state.set_state(FoodCalories.amount)


# Добавление калорий съеденной пищи
@router.message(FoodCalories.amount)
async def food_calories(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    calories_per_100g = user_data.get('calories_per_100g')
    try:
        amount = float(message.text)
        total_calories = (calories_per_100g * amount) / 100
        users[user_id]["logged_calories"] += total_calories
        await message.reply(f"Записано: {total_calories:.1f} ккал.")
    except ValueError:
        await message.reply("Пожалуйста, введите число, представляющее количество граммов.")

    await state.clear()


# Обработчик команды /log_workout <название активности> <длительность активности, мин>
@router.message(Command("log_workout"))
async def cmd_log_workout(
        message: Message,
        command: CommandObject
):
    user_id = message.from_user.id
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None or len(command.args.split()) != 2:
        await message.reply(
            "Ошибка: укажите название активности и длительность активности, мин. Пример:\n"
            "/log_workout бег 30>"
        )
        return

    activity_name = command.args.split()[0]
    activity_duration = command.args.split()[1]

    # Если длительность активности не число, то ошибка
    if activity_duration.isdigit() is False:
        await message.reply(
            "Ошибка: длительность активности указана не числом в мл. Пример:\n"
            "/log_workout run 30"
        )
        return
    else:
        activity_duration = float(command.args.split()[1])
    # Если название активности число, то ошибка
    if activity_name.isdigit() is True:
        await message.reply(
            "Ошибка: название активности указано числом. Пример:\n"
            "/log_workout run 30"
        )
        return

    calories_per_1_hour = await activity_info(activity_name, users[user_id]["weight"])
    if calories_per_1_hour is not None:
        total_calories = (calories_per_1_hour * activity_duration) / 60
        users[user_id]["burned_calories"] += total_calories
        add_water = int(200 * activity_duration / 30)
        users[user_id]["water_goal"] += add_water
        await message.reply(
            f"{activity_name} {activity_duration} мин — {total_calories} ккал\n"
            f"Дополнительно выпейте {add_water} мл воды\n"
        )
    else:
        await message.reply("Не удалось получить данные о калорийности тренировки. Попробуйте другую активность.")


# Обработчик команды /check_progress
@router.message(Command("check_progress"))
async def check_progress(message: Message):
    user_id = message.from_user.id

    await message.reply(
        "Прогресс:\n"
        f"- Выпито воды: {users[user_id]['logged_water']} мл из {users[user_id]['water_goal']} мл\n"
        f"- Осталось выпить воды: {users[user_id]['water_goal'] - users[user_id]['logged_water']} мл\n"
        "\n"
        "Калории\n"
        f"- Потреблено: {users[user_id]['logged_calories']} ккал из {users[user_id]['calorie_goal']} ккал\n"
        f"- Сожжено: {users[user_id]['burned_calories']} ккал"
        f"- Баланс: {users[user_id]['logged_calories'] - users[user_id]['burned_calories']} ккал\n"
    )
