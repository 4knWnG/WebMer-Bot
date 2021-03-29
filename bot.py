from aiogram import Bot, Dispatcher, executor, types
from asyncio import sleep
from io import BytesIO
import subprocess
import os
import re
import random
from dotenv import load_dotenv
import requests

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)



class FFMConvertor:

   def convert_webm_mp4(self, input_file, output_file):
      try:
         command = 'ffmpeg -i ' + input_file + ' ' + output_file + ' -y'
         subprocess.run(command)
      except:
         print('Some Exeption')


ffm = FFMConvertor()

chatid = 0


@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):

   await message.answer("Да просто добавь меня в чат и если ты или кто нибудь в чате напишут 300, то я отвечу отсоси у тракториста, и все в этом духе!")



@dp.message_handler(commands=['setup'])
async def setup_message(message: types.message):
    
    await bot.send_message(message.from_user.id, "Add me to your channel / group and make me an administrator, and then just send me any message from there!")



@dp.message_handler(content_types=['document','text'])
async def convert_webm(message: types.file):
    global ffm

    if message.document.mime_subtype == 'webm':
        try:
            webmid = message.document.file_id
            await bot.send_message(message.from_user.id, "Конвертирую в mp4...")
            webmvid = await bot.download_file_by_id(webmid)

            input_file_name = str(webmid + 'input.webm')
            output_file_name = str(webmid + 'output.mp4')

            b = BytesIO()
            b.write(webmvid.getvalue())
            with open(input_file_name, 'wb') as f:
                f.write(b.getvalue())
            ffm.convert_webm_mp4(input_file_name, output_file_name)
            file = types.InputFile(output_file_name)
            await bot.send_document(int(-1001380241545), file)
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), input_file_name)
            os.remove(path)
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), output_file_name)
            os.remove(path)
        except:
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), input_file_name)
            os.remove(path)
            await bot.send_message(message.from_user.id, "Ошибка конвертации")
    
    elif re.search(r'webm$', message.text.lower()):
        webmid = 'dsfghsdgdfsg'
        await bot.send_message(message.from_user.id, "Конвертирую в mp4...")
        request = requests.get(message.text)
        input_file_name = str(webmid + 'input.webm')
        output_file_name = str(webmid + 'output.mp4')
        with open(input_file_name, 'wb') as file:
            file.write(request.content)
        ffm.convert_webm_mp4(input_file_name, output_file_name)
        file = types.InputFile(output_file_name)
        await bot.send_video(int(-1001380241545), file, supports_streaming=True)
        
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), input_file_name)
        os.remove(path)
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), output_file_name)
        os.remove(path)
    
    else:
        await bot.send_message(message.from_user.id, "Требуется .webm файл или ссылка на него")
   


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
