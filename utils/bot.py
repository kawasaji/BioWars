import requests
import aiogram
import asyncio
import os
import importlib
import inspect
import traceback
import datetime

from typing import Callable, Literal
from utils.father import Father

from config import WARN_CHAT

class ApiMethods:
    send_message: str = 'sendMessage'
    get_me: str = 'GetMe'


class Bot:

    def __init__(self, token, father: Father, loop=None):
        self.token: str = token
        self.father = father

        # формирование инфы о боте
        me = self.request(ApiMethods.get_me)['result']

        self.id: int = me['id']
        self.username: str = me['username']
        self.first_name: str = me['first_name']

        self.watchers: dict[str, list] = {
            "text": [],
            "callback": []
        }

        self.modules = []

        self.bot = aiogram.Bot(token=token, parse_mode='html')
        self.dp = aiogram.Dispatcher(self.bot)

        self.dp.register_message_handler(self.messages_handler)

    def add_watcher(self,
            func: Callable[[aiogram.types.Message, ], None], # функция, которая является обработчиком. принимает стандартный экземпляр сообщения и экземпляр бота
            handle: Literal["text", "callback"], # указывает какой тип сообщений обрабатывать этому обработчику
            filter: Callable[[aiogram.types.Message], bool] | list[Callable[[aiogram.types.Message], bool]] = None # фильтр лямбда функцией, можно массивом или одиночной
        ):
        if handle == "text": self.watchers['text'].append({"func": func, "filter": filter})
        if handle == "callback": self.watchers['callback'].append({"func": func, "filter": filter})

    async def on_start(self, bot: aiogram.Dispatcher):
        await bot.bot.send_message(WARN_CHAT, f"*Вход!* _(⏰{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')})_", parse_mode="Markdown")

    def polling(self, loop=None):
        aiogram.utils.executor.start_polling(self.dp, loop=loop, on_startup=self.on_start, skip_updates=True)

    async def messages_handler(self, message: aiogram.types.Message):
        valid = []
        for h in self.watchers['text']: # тут проверяет фильтры 
            if not h['filter']: valid.append(h) # если фильтр пустой, значит всегда пропускает
            elif isinstance(h['filter'], list): # если фильтр является массивом, то убеждается, что все фильтры массива являются True
                for f in h['filter']:
                    if not f(message): break
                valid.append(h)
            elif isinstance(h['filter'], Callable) and h['filter'](message): # если фильтр является функцей и функция выдает True
                valid.append(h)
        for v in valid:
            asyncio.gather(v['func'](message, self))


    def request(self, method: ApiMethods | str, params: dict = {}):
        return requests.post(f'https://api.telegram.org/bot{self.token}/', {
            'method': method, 
            **params
        }).json()
    
    async def send_message(self, chat_id: str | int, text: str, reply_to: int | str = None, buttons: list[list[dict]] = None, keyboard: list[list[dict]] = None, disable_web_page_preview: bool = True):
        message = await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_to,
            reply_markup=self.__markups(buttons) if buttons else None,
            disable_web_page_preview=disable_web_page_preview
        )

        # тут сохраняем отправленные сообщения итд

        return message
    
    async def edit_message(self, text: str, chat_id: str | int, message_id: str | int, buttons: list[list[dict]] = None, keyboard: list[list[dict]] = None, disable_web_page_preview: bool = True):
        message = await self.bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=self.__markups(buttons) if buttons else None,
            disable_web_page_preview=disable_web_page_preview
        )
        # тут сохраняем сообщения итд
        return message
    
    def __markups(table: list[list[dict]]) -> aiogram.types.InlineKeyboardMarkup: # превращаяет матрицу словарей в матрицу кнопок
        inline_kb = []
        count = 0
        for row in table:
            inline_kb.append([])
            for col in row:
                if col.get('callback'):
                    inline_kb[count].append(aiogram.types.InlineKeyboardButton(text=col['text'], callback_data=col['callback']))
                elif col.get('url'):
                    inline_kb[count].append(aiogram.types.InlineKeyboardButton(text=col['text'], url=col['url']))
            count += 1
        return aiogram.types.InlineKeyboardMarkup(inline_keyboard=inline_kb)
    def load_modules(self, path):
        for p in [f for f in os.listdir(path) if f.endswith('.py')]:
            spec = importlib.util.spec_from_file_location("", path + '/' + p)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for name, obj in inspect.getmembers(module):
                if hasattr(obj, '__class__') and obj.__class__ == Bot.module:
                    try: self.modules.append(obj.func(self, self.father))
                    except: 
                        print(f"Ошибка при инициализации модуля {obj.func.__name__} ⇩\n")
                        print(traceback.print_exc(1))

    class module:
        def __init__(self, func):
            self.func = func

        def __call__(self, *args, **kwargs):
            result = self.func(*args, **kwargs)
            return result