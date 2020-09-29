#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Codename: CONNOR.
Simple Telegram Bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Commands list:
/start, /help, /search, /link, /refresh, /r, /support, /status 
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

$ref = 'luckyflo95-21';
http://www.amazon.com/dp/ASIN/?tag=luckyflo95-21
"""

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram import ParseMode
from bs4 import BeautifulSoup
import requests
import itertools
import time
import json
from proxywrap import GimmeProxyAPI
from mwt import MWT
import os
import sys
from threading import Thread
import urllib.request

REF_TAG_VALUE="&tag=luckyflo95-21"

# Enable logging.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Attivazione di LuckyFloBot\nUn secondo di pazienza, grazie.')
    time.sleep(1.5)
    update.message.reply_text('Ciao bello! Scrivi /help per conoscere cosa posso fare!')

def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Lista dei comandi supportati:\n\n/cerca: trova i migliori prodotti di Amazon consigliati da LuckyFlo.')

def support_command(update, context):
    """Send a message when the command /support is issued."""
    update.message.reply_text('Ciao, se il bot non funziona correttamente contatta @sgabelloni o @LuckyFlo')

# Setting proxy with a GimmeProxy wrapper.
# This is a debug command and shouldn't be used by common users.
def refresh(update,context):
    try:
        proxy = GimmeProxyAPI(country="IT,UK")
        print("Connected with IP: " + proxy.get_ip_port())
    except Exception:
        update.message.reply_text("I nostri server proxy non rispondono al momento :(")

# /search command. The command makes an Amazon.it research using the passed keywords
# and returns some links with pricess as of version 0.2.
def search(update, context):
    """Search for Amazon product and return it. Need to issue /cerca keywords."""

    # Initial nullness check for keywords. If no keyword is passed it's not worth to perform the scrap.
    if (not context.args):
        update.message.reply_text("Prova ad aggiungere qualche parola da cercare dopo il comando /cerca :)")
        return

    # Check if target site is reachable.
    if not check_net():
        update.message.reply_text("Target site is not responding! Try /support to seek help.")
        return

    # Saving user-supplied keywords. Keyword var will be used for scraping (ence the + divisor), suppkey is meant to be printed.
    keyword = ""
    suppkey = ""
    for word in context.args:
        keyword = keyword + "+" + word
        suppkey += " " + word

    # Build Amazon search link.
    amzn = "https://www.amazon.it/s?k={}{}"
    url = amzn.format(keyword, REF_TAG_VALUE)

    # Setting a header to trick Amazon. This way it will think that the scraper is a legit user.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    # Scrape the web page using bs4 and lxml parser.
    r = requests.get(url, headers = headers)
    soup = BeautifulSoup(r.content, "lxml")

    # Parse the right tags and save them into the links list.
    links = soup.find_all('a', {'class': 'a-link-normal s-no-outline'}, href=True)

    # Just a confirmation for the user.
    update.message.reply_text("La tua richiesta per \"{}\" è stata ricevuta. \nAttendi qualche secondo affinché venga processata.".format(suppkey.strip()))

    # Setting response message.
    response = "Per la tua ricerca su \"{}\" ho trovato i seguenti link:\n\n\n".format(suppkey.strip())
    # Adding links to the response. Product_url var contains the link of a single product and will be used to scrap product information.
    for index, a in zip(range(4), links):
        product_url = "https://amazon.it" + a['href']
        '''debug print
        update.message.reply_text(product_url + " HO FATTO URL N*" + str(index+1))''' 
        # Preparing the soup for single product scraping. (Price and name)
        s = requests.get(product_url, headers = headers)
        prodsoup = BeautifulSoup(s.content, "lxml")
        price = prodsoup.find_all('span', {'class': 'a-size-medium a-color-price'})
        name = prodsoup.find_all('span', {'id': 'productTitle'})
        '''debug print
        update.message.reply_text(name[0].get_text() + " prezzo: " + price[0].get_text())''' 
        response += str(index+1) + ".   [{}]({}) \nPrezzo: {}\n\n".format(name[0].get_text().strip(), product_url, price[0].get_text())
    
    # Returned message. Parsed as markdown to enable hypertext links visualization.
    update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, link_preview=True, disable_web_page_preview=False)
    
def link (update, context):
    """Convert  Amazon link in to Referal Amazon Link. Need to issue /link and post link."""
    # Saving user-link and .
    if (not context.args):
        update.message.reply_text("Prova ad aggiungere il link da trasformare dopo il comando /link :)")
        return
        
    if not check_net():
        update.message.reply_text("Target site is not responding! Try /support to seek help.")
        return
        
    link    = context.args
    reflink = link , "&", REF_TAG_VALUE
    
    response = "Ecco il referal link: ", format(reflink, [])
    print (link)
    print (response)
    
    # Returned message. Parsed as markdown to enable hypertext links visualization.
    update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, link_preview=True, disable_web_page_preview=False)
    

 
    # Check if target site is reachable.
   


  
   
    
 

# Method for getting admin ids. Useful to allow the performing of specific commands.
@MWT(timeout=60*60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

# Core of /status command. Checks if site is reachable or not.
def check_net():
    try:
        urllib.request.urlopen('https://amazon.it', timeout=2)
        return True
    except urllib.request.URLError as err: 
        return False    

# /status command. The command pings target site and checks if server is reachable.
def status(update, context):
    if update.effective_user.id in get_admin_ids(context.bot, update.message.chat_id):
        if check_net():
            update.message.reply_text("Server DOES respond")
        else:
            update.message.reply_text("Server does NOT respond")


# Main function.
def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = "1355056584:AAFs2ZlWL3xOKjLVssEw-5VtGPM5-EvWEI0"
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Stop current instance of the program and start a new one in a new process.
    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        print("Stopping bot.")
        updater.stop()
        print("Bot is now restarting.")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # Check if user requesting is an admin and perform the thread restart.
    def restart(update, context):
        if update.effective_user.id in get_admin_ids(context.bot, update.message.chat_id):
            update.message.reply_text('Admin request detected: bot will restart now...')
            Thread(target=stop_and_restart).start()
        else:
            update.message.reply_text('Admin NOT detected.')

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

   
    dp.add_handler(CommandHandler("cerca", search))
    dp.add_handler(CommandHandler("search", search))
    
    # on command i.e cerca - link Amazon  return referal Amazon link.
    dp.add_handler(CommandHandler("link", link))

    # on command i.e refresh - change bot ip so it doesn't get banned
    dp.add_handler(CommandHandler("refresh", refresh))

    # on command i.e support - give some basic support help (like staff contacts)
    dp.add_handler(CommandHandler("support", support_command))

    # on command i.e. r - restart the bot. Should only be performed by admins.
    dp.add_handler(CommandHandler('r', restart))

    # on command i.e. r - check target site availability. Should only be performed by admins or internally.
    dp.add_handler(CommandHandler('status', status))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()