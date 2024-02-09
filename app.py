from utils.father import Father
import os

father = Father(path=os.path.dirname(os.path.abspath(__file__)))

father.bot.load_modules(path='handlers')
father.bot.polling()