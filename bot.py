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

channelid = 0
print(channelid)
channelname = 0
channelname = []

@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):

   await message.answer("Hi i am WEBMer - i can halp you to post webm videos to  your channels/chats!"
   "\n- To start you need to connect me to your channel! Type /setup"
   "\n- After that you can send me webm files and I will convert them to mp4 and immediately send them to your channel as a video message!")



@dp.message_handler(commands=['setup'])
async def setup_message(message: types.message):
    
    await bot.send_message(message.from_user.id, "Add me to your channel / group and make me an administrator, and then just send me any message from there!")



@dp.message_handler(commands=['current'])
async def current_message(message: types.message):

    global channelid
    global channelname

    if channelid != 0:

        await bot.send_message(message.from_user.id, "@" + channelname)
    else:
        await bot.send_message(message.from_user.id, "No channel connected! Forward me any message from it!")



@dp.message_handler(content_types=["text"])
async def setup2_message(message: types.message):

    
    global channelid
    global channelname

    if not message.forward_from_chat.id:
        await bot.send_message(message.from_user.id, "I need a message forwarded from your channel!")
    else:
        channelid = message.forward_from_chat.id
        print(channelid)
        channelname = message.forward_from_chat.username
        print(channelname)



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
            await bot.send_document(int(channelid), file)
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
        await bot.send_video(int(channelid), file, supports_streaming=True)
        
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), input_file_name)
        os.remove(path)
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), output_file_name)
        os.remove(path)
    
    else:
        await bot.send_message(message.from_user.id, "Требуется .webm файл или ссылка на него")
   


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
