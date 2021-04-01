from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from io import BytesIO

import ffmpeg
import subprocess
import os
import re
import requests
import json
import random

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)


class FFMConvertor:

    def convert_webm_mp4(self, input_file, output_file):

        stream = ffmpeg.input(input_file)
        stream = ffmpeg.output(stream, output_file)
        ffmpeg.run(stream)

ffm = FFMConvertor()


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await bot.send_message(message.from_user.id, "Hi i am WEBMer Bot!"
                                                 "\nTo start send me any message from channel you want to post webm "
                                                 "and make me an admin of this channel!")
    channelname = get_channel_params(message)['channelname']
    await bot.send_message(message.from_user.id, f'The last time you posted on this channel: @{channelname}')


def get_channel_params(message):
    with open('channels.json') as f:
        data = json.load(f)
        for u in data['users']:
            if message.from_user.id == u['id']:
                channelid = u['channelid']
                channelname = u['channelname']
    return {'channelid': channelid, 'channelname': channelname}


@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Hi i am WEBMer - i can halp you to post webm videos to  your channels/chats!"
                           "\n- To start you need to connect me to your channel! Type /setup"
                           "\n- After that you can send me webm files and I will convert them to mp4 and immediately send them to your channel as a video message!")


@dp.message_handler(commands=['setup'])
async def setup_message(message: types.message):
    await bot.send_message(message.from_user.id,
                           "Add me to your channel / group and make me an administrator, and then just send me any message from there!")


@dp.message_handler(commands=['current'])
async def current_message(message: types.message):

    channel_params = get_channel_params(message)
    channelid = channel_params['channelid']
    channelname = channel_params['channelname']
    if channelid != 0:

        await bot.send_message(message.from_user.id, 'Currently connected server: ' + f'@{channelname}')

    else:

        await bot.send_message(message.from_user.id, "No channel connected! Forward me any message from it!")


@dp.message_handler(content_types=['document', 'text'])
async def convert_webm(message: types.file):
    global ffm

    channel_params = get_channel_params(message)
    channelid = channel_params['channelid']
    channelname = channel_params['channelname']

    if message.forward_from_chat:
        if not message.forward_from_chat.id:
            await bot.send_message(message.from_user.id, "I need a message forwarded from your channel!")
        else:
            with open('channels.json') as f:
                data = json.load(f)
                isnew = True
                for u in data['users']:
                    if message.from_user.id == u['id']:
                        u['channelid'] = message.forward_from_chat.id
                        u['channelname'] = message.forward_from_chat.username
                        isnew = False
            with open('channels.json', 'w') as f:
                if isnew:
                    newuser = ({'id': message.from_user.id, 'channelid': message.forward_from_chat.id,
                                'channelname': message.forward_from_chat.username})
                    data['users'].append(newuser)
                json.dump(data, f)
                f.close()
        channelid = message.forward_from_chat.id
        channelname = message.forward_from_chat.username
        await bot.send_message(message.from_user.id,
                               "Ready to post to channel: " + f'@{channelname}' + " Don't forget that i must be the admin of this channel!")

    if channelid == 0:
        await bot.send_message(message.from_user.id, "First you need to setup your server!")
    elif message.document:
        if message.document.mime_subtype == 'webm':
            try:
                webmid = message.document.file_id
                await bot.send_message(message.from_user.id, "Converting to mp4 ...")
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
                await bot.send_message(message.from_user.id,
                                       f"Converting finished, video sent to channel @{channelname}")
            except:
                path = os.path.join(os.path.abspath(os.path.dirname(__file__)), input_file_name)
                os.remove(path)
                await bot.send_message(message.from_user.id, "Conversion error!")

    elif re.search(r'webm$', message.text.lower()):
        webmid = str(random.randrange(10000000))
        await bot.send_message(message.from_user.id, "Converting to mp4 ...")
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
        await bot.send_message(message.from_user.id, f"Converting finished, video sent to channel @{channelname}")

    elif re.search(r'mp4$', message.text.lower()):
        webmid = str(random.randrange(10000000))
        request = requests.get(message.text)
        file_name = str(webmid + 'vid.mp4')
        await bot.send_message(message.from_user.id, "Downloading mp4")
        with open(file_name, 'wb') as file:
            file.write(request.content)
            file.close()
        await bot.send_message(message.from_user.id, f"Sending mp4 to channel @{channelname}")
        file = types.InputFile(file_name)
        await bot.send_video(int(channelid), file)

        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)
        os.remove(path)

    else:
        await bot.send_message(message.from_user.id, "WebM file or a link to it is required!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)