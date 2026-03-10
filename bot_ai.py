import os
import telebot
from dotenv import load_dotenv
from telebot.types import Message
from groq import Groq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

tgBot = telebot.TeleBot(TELEGRAM_TOKEN)

aiClient = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
Ты консультант салона оптики. Отвечай вежливо, по делу и на русском языке.
Помогай клиентам с вопросами об общих рекомендациях по выбору оптики. Если клиент спрашивает про конкретные модели товаров, цены или наличие, отвечай: (вариант ответа).
Не придумывай информацию. Если не знаешь ответ, предложи связаться с оператором.
"""

@tgBot.message_handler(commands=["start"])
def send_welcome(message: Message):
  tgBot.reply_to(
    message,
    "Привет! Я консультант магазина \n\n"
    "Помогу с выбором нужной оптики\n"
    "Команды:\n"
    "/help — список команд\n"
    "/info — контакты магазина"
  )


@tgBot.message_handler(commands=["help"])
def send_help(message: Message):
  tgBot.reply_to(
    message,
    "Доступные команды:\n\n"
    "/start — начать диалог заново\n"
    "/help — показать это сообщение\n"
    "/info — контакты и график работы магазина\n\n"
    "Просто напишите свой вопрос, и я постараюсь помочь!"
  )

@tgBot.message_handler(commands=["info"])
def send_info(message: Message):
  tgBot.reply_to(
    message,
    "Магазин \n\n"
    "Сайт: ru\n"
    "Email: \n"
    "Телефон:\n"
    "Режим работы:\n"
    "Пн-Пт: 9:00-20:00\n"
    "Сб-Вс: 10:00-18:00"
  )

def chat_ai(user_message: str):
  try:
    completion = aiClient.chat.completions.create(
      model="openai/gpt-oss-120b",
      messages=[
        {
          "role": "system", 
          "content": SYSTEM_PROMPT},
        {
          "role": "user",
          "content": user_message
        },
      ],
      temperature=1,
      max_completion_tokens=8192,
      top_p=1,
      reasoning_effort="medium",
      stream=True,
      stop=None
    )

    response_text = ""
    for chunk in completion:
      delta = chunk.choices[0].delta.content
      if delta:
        response_text += delta    

    return response_text

  except Exception as e:
    print(f"Ошибка при обращении к ИИ: {e}")

    return (
      "Извините, произошла ошибка при обработке запроса."
      "Попробуйте позже или свяжитесь с оператором."
    )

@tgBot.message_handler(func=lambda message: True)
def handle_message(message: Message):
  user_text: str = message.text
  tgBot.send_chat_action(message.chat.id, "typing")
  response_text = chat_ai(user_text)
  tgBot.send_message(message.chat.id, response_text)

if __name__ == "__main__":
  print("Бот с ИИ запущен и ожидает сообщений...")
  print("Для остановки нажмите Ctrl+C")
  tgBot.polling(none_stop=True)

