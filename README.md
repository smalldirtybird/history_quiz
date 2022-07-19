## History quiz bot

![](https://psv4.userapi.com/c237031/u328907/docs/d22/c4bf21793985/history_quiz_tg_demo.gif?extra=CEbKQqAqZmNVohHhmNls1nAp4uTMC1lAiushZ12R7bSoIXbqwPjAeb2ekmEjGkEmoHBwNKtMPfF-LajHTTn8yettWE-th-_jZXct_sZfq4U300ytXr9G46hmP_dE85_5nhhRX-KWEJ-Rt5ieEQ)

Automate a history quiz with [Telegram](https://t.me/QuizStoryBot) and [VK](https://vk.com/im?sel=-214235425) bots

## How it works:
Send to bot `/start` command to begin a quiz. Then push `Новый вопрос` button for a new question and try the correct answer by typing it in the text input box. If you don't know the answer, click `Сдаться` to get a new question.

Examples of working bots are available at the links in the titles.

## How to prepare:
1. Make sure Python installed on your PC - you can get it from [official website](https://www.python.org/).


2. Install libraries with pip:
```
pip3 install -r requirements.txt
```


3. Create a Telegram bot which will talk with users and send mesages about program errors - just send message `/newbot` to [@BotFather](https://telegram.me/BotFather) and follow instructions.
After bot will be created, get token from @BotFather and add to .env file:
```
TELEGRAM_BOT_TOKEN ='your_telegram_bot_token'
```
Put your token instead of value in quotes.


4. Get Telegram id of user who will receive mesages about program errors - send message `/start` to [@userinfobot](https://telegram.me/userinfobot) and copy value of id from answer.
Add the string
```
TELEGRAM_CHAT_ID='YourTelegramID'
```
to .env file.


5. For [VK](https://vk.com/) bot you should generate VK API token from community page. Proceed to [Managed communities page](https://vk.com/groups?tab=admin), chose your group and on `Manage/API usage` tab generate token by clicking `Generate token` button. Then put the token to /env file:
```
VK_GROUP_TOKEN = 'yor vk_group_token'
```

6. Create database on [Redislabs](https://redis.com/). 
7. Add the following lines to .env file:
```
DB_HOST = 'your_database_address'
DB_PORT = 'database_port'
DB_PASSWORD = 'database+password'
```
8. Add to .env file string with path to folder with quiz files:
```
QUIZ_FILES_PATH = 'folder_path'
```
9. You can delete unnecessary files from the folder, or add new ones with .txt extension. New files must follow the structure:
```
Вопрос <number of question>. <question_text>
\n
\n
Ответ. <answer_text>
\n
\n
```

## How to run:

Bot can be launched from the terminal with the commands:

Telegram bot:`$ python3 tg_bot.py`

VK bot: `$ python3 vg_bot.py`
