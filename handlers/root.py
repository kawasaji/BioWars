from utils.bot import Bot
from utils.father import Father
from utils.strings import strings


from datetime import datetime

import traceback
import os
import importlib
import inspect
import io
import html
import ast

from aiogram.types import Message
from meval import meval


    
@Bot.module
class root:
    def __init__(self, bot: Bot, father: Father):

        self.bot: Bot = bot
        self.father = father

        self.owners = [780882761]

        self.bot.add_watcher(
            func=self.handler,
            handle='text',
            filter=lambda m: m.text and m.from_user and m.from_user.id in self.owners # пропускает только овнеров
        )

    async def handler(self, message: Message, bot: Bot):
        if message.text.lower().startswith('/code'):
            code = message.text[5::].strip()
            text = f'<i>Код:</i><blockquote>{html.escape(code)}</blockquote>'
            answ = await bot.send_message(chat_id=message.chat.id, text=text)
            try: 
                result = await meval(
                    code, 
                    globs=globals(), 
                    message=message, 
                    print=lambda *values: str(*values)
                )
            except: result = traceback.format_exc(1)
            if '{' in str(result) and '}' in str(result):
                result = strings.format_dict(strings.is_dict_string(result)) if strings.is_dict_string(result) else result
                result = strings.format_dict(strings.is_valid_json(result)) if strings.is_valid_json(result) else result

            text += f'<i>Результат:</i><blockquote>{html.escape(str(result))}</blockquote>'
            if len(text) < 5000:
                await bot.edit_message(text, chat_id=answ.chat.id, message_id=answ.message_id)
            else:
                text = f'<i>Результат:</i><blockquote>{html.escape(str(result))}</blockquote>'
                if len(text) < 5000: await bot.send_message(chat_id=message.chat.id, text=text)
                else:
                    text_file = io.BytesIO(str(result).encode('utf-8'))
                    text_file.name = 'answer'
                    await bot.bot.send_document(message.chat.id, text_file, caption="<i>Ответ превышает 5000 символов.</i>")


        if message.text.lower() == '/reload':
            text = f"<i>Перезагрузка модулей ({datetime.now().strftime('%d.%m.%Y %H:%M:%S')})</i>"
            answ = await bot.send_message(message.chat.id, text)

            self.father.bot.watchers = {"text": [], "callback": []}
            self.father.bot.modules = []

            path = 'handlers'

            text += f"<blockquote><i>"
            count = 0

            for p in [f for f in os.listdir(path) if f.endswith('.py')]:
                spec = importlib.util.spec_from_file_location("", path + '/' + p)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if hasattr(obj, '__class__') and obj.__class__ == Bot.module:
                        try: 
                            self.father.bot.modules.append(obj.func(self.father.bot, self.father))
                            count += 1
                            text += f"{count}. Модуль <code>{obj.func.__name__}</code> загружен\n"
                            await answ.edit_text(text=text + f"</i></blockquote>")
                        except: 
                            count += 1
                            print(traceback.print_exc(1))
                            text += f"{count}. Модуль <code>{obj.func.__name__}</code> не загружен\n"
                            await answ.edit_text(text=text + f"</i></blockquote>")
            await answ.edit_text(text=text + f"</i></blockquote><i>Перезагрузка завершена ({datetime.now().strftime('%d.%m.%Y %H:%M:%S')})</i>")
