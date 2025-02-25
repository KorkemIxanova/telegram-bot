import logging
import requests
import spacy
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from bs4 import BeautifulSoup
from googletrans import Translator
TOKEN = "7926421751:AAHPp7Ya2-E4DzMKCBb48aChz_VKlca3gwg"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
nlp = spacy.load("en_core_web_sm")
translator = Translator()
logging.basicConfig(level=logging.INFO)
def get_lyrics(artist, song):
    url = f"https://api.lyrics.ovh/v1/{artist}/{song}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("lyrics", "Текст не найден")
    return "Не удалось найти текст." 
def get_chords(song):
    search_url = f"https://www.ultimate-guitar.com/search.php?search_type=title&value={song}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("a", class_="js-search-result-link")
    if results:
        return results[0]["href"]
    return "Аккорды не найдены."
def analyze_grammar(text):
    doc = nlp(text)
    analysis = []
    for token in doc[:10]:
        analysis.append(f"{token.text} – {token.pos_} ({token.dep_})")
    return "\n".join(analysis)
def translate_words(text):
    doc = nlp(text)
    words = {token.text for token in doc if token.is_alpha}
    translated_words = {}
    for word in list(words)[:10]:
        translated = translator.translate(word, src="en", dest="ru").text
        translated_words[word] = translated
    return "\n".join([f"{word} – {translated_words[word]}" for word in translated_words])
@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    await message.answer("Привет! Отправь название и исполнителя (например: Coldplay - Yellow).")
@dp.message_handler()
async def process_song_request(message: Message):
    text = message.text.strip().split(" - ")
    if len(text) != 2:
        await message.answer("Пожалуйста, отправь запрос в формате 'Исполнитель - Песня'.")
        return
    artist, song = text
    lyrics = get_lyrics(artist, song)
    chords = get_chords(song)
    await message.answer(f"**Текст песни {song} от {artist}:**\n\n{lyrics[:1000]}...")
    grammar_analysis = analyze_grammar(lyrics[:500]) 
    translation = translate_words(lyrics[:500])
    await message.answer(f"**Грамматический анализ:**\n{grammar_analysis}")
    await message.answer(f"**Перевод ключевых слов:**\n{translation}")
    await message.answer(f"**Аккорды:** {chords}")
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
