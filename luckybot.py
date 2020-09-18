#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
/start, /help, /cerca
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler
from bs4 import BeautifulSoup
import requests
import itertools
import time
import json


# Enable logging.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Attivazione di LuckyFloBot V. 0.2 \nUn secondo di pazienza, grazie.')
    time.sleep(1.5)
    update.message.reply_text('Ciao bello! Scrivi /help per conoscere cosa posso fare!')

def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Lista dei comandi supportati:\n\n/cerca: trova i migliori prodotti di Amazon consigliati da LuckyFlo.')

# /cerca command. The command makes an Amazon.it research using the passed keywords
# and returns some links as of version 1.0.
def search(update, context):
    """Search for Amazon product and return it. Need to issue /cerca keywords."""

    proxy = GimmeProxyAPI(country="IT,UK")
    print(proxy.get_ip_port())

    #Initial nullness check for keywords. If no keyword is passed it's not worth to perform the scrap.
    if (not context.args):
        update.message.reply_text("Prova ad aggiungere qualche parola da cercare dopo il comando /cerca :)")
        return

    #Saving user-supplied keywords. Keyword var will be used for scraping (ence the + divisor), suppkey is meant to be printed.
    keyword = ""
    suppkey = ""
    for word in context.args:
        keyword = keyword + "+" + word
        suppkey += " " + word

    #Build Amazon search link.
    AMZN = "https://www.amazon.it/s?k="
    #REF = "tag=luckyflo95-21"
    url = AMZN + keyword #+ "&" + REF
    # Setting a header to trick Amazon. This way it will think that the scraper is a legit user.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    #Scrape the web page using bs4 and lxml parser.
    r = requests.get(url, headers = headers)
    soup = BeautifulSoup(r.content, "lxml")

    #Parse the right tags and save them into the links list.
    links = soup.find_all('a', {'class': 'a-link-normal s-no-outline'}, href=True)

    #Just a confirmation for the user.
    update.message.reply_text("La tua richiesta per \"" + suppkey + "\" è stata ricevuta. \nAttendi qualche secondo affinché venga processata.")

    #Setting response message.
    response = "Per la tua ricerca su" + suppkey + " ho trovato i seguenti link:\n ----------------------\n\n\n"
    #Adding links to the response. Product_url var contains the link of a single product and will be used to scrap product information.
    for index, a in zip(range(5), links):
        product_url = "https://amazon.it" + a['href']
        #debug print# update.message.reply_text(product_url + " HO FATTO URL N*" + str(index+1))
        #Preparing the soup for single product scraping. (Price and name)
        s = requests.get(product_url, headers = headers)
        prodsoup = BeautifulSoup(s.content, "lxml")
        #debug print# update.message.reply_text("scrappato URL N*"+ str(index+1))
        price = prodsoup.find_all('span', {'class': 'a-size-medium a-color-price'})
        name = prodsoup.find_all('span', {'id': 'productTitle'})
        
        response += "["+ str(index+1) + ". " + name[0].get_text() +"](" + product_url + ") " + "Prezzo: " + price[0].get_text() + "\n\n"
    response = ""
    
    #Returned message.
    update.message.reply_text(response, link_preview=True)
    

#Main function.
def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1355056584:AAFs2ZlWL3xOKjLVssEw-5VtGPM5-EvWEI0", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e cerca - search for Amazon results and return links.
    dp.add_handler(CommandHandler("cerca", search))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()