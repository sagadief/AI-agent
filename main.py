
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from search_download_pdf import search_download
import arxiv
from preprocc_pdf import PromptTranslatorEnRu, read_file_pdf, append_full_text, en_pdf_to_ru_txt
from GigaChat_module import txt_to_summary, reading_txt_giga

TOKEN = '7059633748:AAExQg88Pgn-E5b5y4XB3CinT-a4KPHc2BI'
bot = TeleBot(TOKEN)
translator = PromptTranslatorEnRu()

from langchain.chat_models.gigachat import GigaChat
from langchain.chains import RetrievalQA
orig_token = "NTlkY2MyZmItM2Q4ZC00ZWMzLWE2NjAtNTI3MzZhOTk2ZjQzOjVhZGJiZDQxLTc0YjAtNDQxNi04YjAzLTUxZDVmYTY4NTkwNw=="

llm = GigaChat(credentials=orig_token, scope="GIGACHAT_API_CORP",verify_ssl_certs=False,model="GigaChat-Pro")


user_states = {}  # Словарь для хранения состояний пользователей
user_name_find = {}
user_count_find = {}
user_finded_result = {}
user_qa_db = {}
user_qa_db_chain = {}


main_text = '''👋 Привет! Я — AI Agent DeepHack, твой виртуальный помощник, который помогает быстро находить, читать и анализировать научные статьи. 🚀
Я могу упростить твой доступ к сложным научным знаниям, обобщая ключевую информацию из статей и ответив на твои вопросы по теме. Ты можешь рассчитывать на меня в поиске научных материалов по интересующим тебя ключевым словам.
🌍 В настоящее время я работаю только с запросами на английском языке. Пожалуйста, пришли мне ключевые слова, чтобы я начал поиск. Например: "Аrtificial intelligence in medicine" (Искусственный интеллект в медицине).'''

sec_text = 'Какое количество статей вы хотите увидеть?'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_states[user_id] = 'waiting_main_text'  # Устанавливаем состояние ожидания main_text
    bot.send_message(chat_id=message.chat.id, text=main_text)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_main_text')
def handle_main_text(message):
    user_id = message.from_user.id
    user_states[user_id] = 'waiting_sec_text'  # После ответа на main_text ожидается sec_text
    user_name_find[user_id] = message.text
    print(user_name_find)
    bot.send_message(chat_id=message.chat.id, text=sec_text, reply_markup=create_keyboard())



@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_sort_text')
def handle_sort_text(message):
    user_id = message.from_user.id
   
    string_find = f"Ищю последние статьи на тему: {user_name_find[message.from_user.id]}"
    bot.send_message(chat_id=message.chat.id, text = string_find)


@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'qa_model')
def qa_model(message):
    user_id = message.from_user.id
    
    print("Start qa")
    print(message.text)

    if user_id in user_qa_db:

        db = user_qa_db[user_id]
        #docs = db.similarity_search(message.text,k=100)
        #qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

        qa_chain = user_qa_db_chain[user_id] 
        #result
        answer = qa_chain({"query": message.text})['result']
        #print()
        bot.send_message(chat_id=message.chat.id, text = answer)





@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_sec_text')
def handle_sec_text(message):
    user_id = message.from_user.id
    print(user_id)
    сount = message.text
    user_states[user_id] = 'waiting_sort_text'
    user_count_find[user_id] = int(сount)


    inline_markup = InlineKeyboardMarkup()
    buttons = [
        InlineKeyboardButton("Релевантность ", callback_data=f"{user_id}/button1/"),
        InlineKeyboardButton("Дата публикации", callback_data=f"{user_id}/button2/")
    ]
    inline_markup.add(*buttons)

    # Отправляем сообщение с текстом и кнопками
    bot.send_message(chat_id=message.chat.id, 
                     text='Выберите сортировку:', 
                     reply_markup=inline_markup)
    
#ОБРАБОТКА КНОПОК ПОД ТЕКСТОМ    
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data
    
    
    data_splitter = data.split("/")
    user_id = int(data_splitter[0])
    #print(user_id)



    if call.message:

        count = int(user_count_find[user_id])
        print(count)
        name_paper = user_name_find[user_id]
        print(name_paper)

        if data_splitter[1] == "v2":
            res = user_finded_result[user_id]
            index = int(data_splitter[2])
            article = res[index - 1]
            print(article)
            path_pdf = article['path_pdf']
            title = article['title']
        
            text_start_summary = f"📘Отличный выбор! Сейчас я подготовлю краткую выжимку из статьи {title} и пришлю тебе основные моменты. Дай мне всего несколько секунд!\n\n"
            bot.send_message(chat_id=call.message.chat.id, text=text_start_summary)

            path_txt = en_pdf_to_ru_txt(path_pdf)

            summary = txt_to_summary(path_txt)

            bot.send_message(chat_id=call.message.chat.id, text=summary+"\n\n")

            bot.send_message(chat_id=call.message.chat.id, text = "🏥 Есть ли другие вопросы по этой cтатьи?")

            user_states[user_id] = 'qa_model'
            db = reading_txt_giga(path_txt)
            qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())
            user_qa_db[user_id] = db
            user_qa_db_chain[user_id] = qa_chain
            return

        text_start_find = "🔍 Понял твой запрос! Сейчас я найду самые свежие исследования по этой теме и буду присылать тебе"
        if data_splitter[1] == 'button1':
            #bot.send_message(chat_id=call.message.chat.id, text='Вы выбрали релевантность.')
            #SortCriterion.Relevance
            bot.send_message(chat_id=call.message.chat.id, text=text_start_find)
            res = search_download("./h1", name_paper, count, arxiv.SortCriterion.Relevance)
            print(res)
            
        elif data_splitter[1] == 'button2':
            #bot.send_message(chat_id=call.message.chat.id, text='Вы выбрали сортировку по дате публикации.')
            bot.send_message(chat_id=call.message.chat.id, text=text_start_find)
            res = search_download("./h1", name_paper, count, arxiv.SortCriterion.Relevance)
            print(res)
            #SortCriterion.SubmittedDate

    
    

    # Отправляем каждую ссылку в отдельном сообщении с кнопкой
    for index, article in enumerate(res, start=1):
        if index <= user_count_find[user_id] <= len(res):
            url = article['link_paper']
            title = article['title']
            path_pdf = article['path_pdf']
            #path_txt = en_pdf_to_ru_txt(path_pdf)
            #summary = txt_to_summary(path_txt)


            button_text = f"Статья {index}: {title[:30]}" if len(title) > 30 else f"Статья {index}: {title}"

            
            
            # Создаем InlineKeyboardMarkup с одной кнопкой для текущей ссылки
            inline_markup = InlineKeyboardMarkup()
            inline_button = InlineKeyboardButton(button_text,  callback_data=f"{user_id}/v2/{index}")
            inline_markup.add(inline_button)
            
            # Отправляем сообщение с текущей ссылкой и кнопкой
            bot.send_message(chat_id=call.message.chat.id, text=url)
            bot.send_message(chat_id=call.message.chat.id, text=title, reply_markup=inline_markup)

    bot.send_message(chat_id=call.message.chat.id, text="👀 Нажми на интересующию статью и я расскажу про нее подробнее")
    user_finded_result[user_id] = res
    
    return


    for paper_info in res:

        path_pdf = paper_info['path_pdf']
        
        path_txt = en_pdf_to_ru_txt(path_pdf)

        
        #res = txt_to_summary(path_txt)
        #bot.send_message(chat_id=call.message.chat.id, text= res)

        #res = reading_txt_giga(path_txt)
        break

    #print(user_name_find[user_id])
    bot.send_message(chat_id=call.message.chat.id, text= f'Вы выбрали {user_count_find[user_id]}\nПо названию { user_name_find[user_id]}')



    



def create_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in range(1, 11):
        markup.add(KeyboardButton(str(i)))
    return markup

bot.polling()
#if __name__ == "__name__":

    