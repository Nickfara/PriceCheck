from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
import time
from io import BytesIO


async def parse_site(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    time.sleep(10)
    products = driver.find_elements(By.CLASS_NAME, 'ProductCard_title__iNsaD')
    brands = driver.find_elements(By.CLASS_NAME, 'ProductCard_title__iNsaD')
    prices = driver.find_elements(By.CLASS_NAME, 'ProductCard_price__aRuGG')
    pricesNEW = driver.find_elements(By.CLASS_NAME, 'CommonProductCard_priceText__bW6F9')
    volumes = driver.find_elements(By.CLASS_NAME, 'ProductCard_volume__PINyI')

    product_names = [product.text.split('\n') for product in products]
    brand_names = [brand.text.split('\n') for brand in brands]
    product_prices = [price.text.split('\n') for price in prices]
    product_pricesNEW = [priceNEW.text.split('\n') for priceNEW in pricesNEW]
    product_volumes = [volume.text.split('\n') for volume in volumes]
    max_length = max(len(product_names), len(brand_names), len(product_prices), len(product_pricesNEW), len(product_volumes))

    product_names += [None] * (max_length - len(product_names))
    brand_names += [None] * (max_length - len(brand_names))
    product_prices += [None] * (max_length - len(product_prices))
    product_pricesNEW += [None] * (max_length - len(product_pricesNEW))
    product_volumes += [None] * (max_length - len(product_volumes))

    #Функция для извлечения названия бренда из названия
    def extract_brand_name(full_name):
        parts = full_name.split()
        desired_parts = parts[2:-2]
        return ' '.join(desired_parts)
    brand_names = [extract_brand_name(brand.text) for brand in brands]

    # Функция для извлечения цены
    def extract_price(price_list):
        # Предполагаем, что цена всегда находится на втором месте в списке
        return price_list[1] if len(price_list) > 1 else None

    # Измененная строка для product_prices
    product_prices = [extract_price(price.text.split('\n')) for price in prices]

    # Функция для извлечения нужной части названия (аукционная цена)
    def extract_brand_name(full_name):
        parts = full_name.split()
        desired_parts = parts[2:-2]
        return ' '.join(desired_parts)
    brand_names = [extract_brand_name(brand.text) for brand in brands]

    # Функция для извлечения цены

    def process_priceNEW(price_list):
        if 'Цена со скидкой за 1 шт.' in price_list:
            # Возвращаем только число, если это цена со скидкой
            return price_list[1]
        elif 'Цена за 1 шт.' in price_list:
            # Возвращаем весь текст, если это обычная цена
            return ' None '
        else:
            # Возвращаем None, если список пуст или не соответствует ожидаемым значениям
            return None

    # Использование новой функции для обработки цен
    product_pricesNEW = [process_priceNEW(priceNEW.text.split('\n')) for priceNEW in pricesNEW]


    df = pd.DataFrame({
        'Название газировки': product_names,
        'Бренд': brand_names,
        'Цена': product_prices,
        'Цена со скидкой': product_pricesNEW,
        'Объем бутылки': product_volumes,
    })
        # print(df)
        # df.to_csv('ff1.csv', index=False)
        # df.to_excel('магнит_эа.xlsx', index=False)
    # Сохранение DataFrame в файл Excel
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    # Отправление файла Excel пользователю
    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=excel_file,
        filename='результаты_парсинга.xlsx'
    )



from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from my_parser import parse_site


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Введи ссылку на страницу сбермаркета, которую хочешь спарсить.')
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    await parse_site(update, context, url)

def main() -> None:
    application = Application.builder().token('7306002854:AAHIc35yMOXyho4bcYYeAS3W5PP0ey_1HXk').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling()


if __name__ == '__main__':
    main()