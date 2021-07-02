import requests
import logging
from BarbotOrder import BarbotOrder

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

TOKEN = "1820138808:AAF7krmrA3f07P6g2fG5naSEbyYMLAbC1f8"
JOPPE = "";

Orders = []
ReplyKeyboard = [["Cola", "Cola Light"], ["Bier", "Bier 0.0"], ["Rode Wijn", "Patat Oorlog"]]

def getJoppe():
    r = requests.get('http://85.214.240.144/Joppe/GetDailyName')
    data = r.json()
    return data['name']


def ordersToString():
    line = ""

    for bo in Orders:
        line += bo.name + " :: " + bo.drink + "\n"

    return line;


def start(update: Update, context: CallbackContext) -> int:
    #r = requests.get('http://85.214.240.144/Joppe/GetDailyName')
    #data = r.json()
    #update.message.reply_text('De naam is ' + data['name'])
    return ConversationHandler.END

def createNewOrderList(update: Update, context: CallbackContext) -> int:
    Orders.clear();
    update.message.reply_text("Nieuwe rondje")
    return ConversationHandler.END

def startNewOrder(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    #Orders.append(BarbotOrder(user.first_name, "ah bier!"));
    update.message.reply_text("wa mot je hebbe dan?", 
        reply_markup=ReplyKeyboardMarkup(
            ReplyKeyboard, selective="reply_to_message_id", one_time_keyboard=True, input_field_placeholder='Boy or Girl?'
        ))
    return "HANDJE"

def createNewOrder(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user

    if user.first_name.upper() == "JOPPE":
        Orders.append(BarbotOrder(getJoppe(), update.message.text))
    else:
        Orders.append(BarbotOrder(user.first_name, update.message.text))

    update.message.reply_text(ordersToString(), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def getOverview(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(ordersToString())
    return ConversationHandler.END


def getJoppeResponse(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(getJoppe())
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def getExplanation(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "/handjes om een nieuw lijstje te beginnen.\n" +
        "/handje om een keuze te maken! Ah bier.\n" +
        "/enklaar om een overzichtje te krijgen van alle meedrinkers.\n" + 
        "/joppe om de naam van " + getJoppe() + " te krijgen.", 
        reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(entry_points=[
            CommandHandler('start', start),
            CommandHandler('handjes', createNewOrderList),
            CommandHandler('handje', startNewOrder),
            CommandHandler('enklaar', getOverview),
            CommandHandler('huh', getExplanation),
            CommandHandler('joppe', getJoppeResponse)
        ],
        states={
            "HANDJE": [MessageHandler(Filters.text, createNewOrder)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],)

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT.  This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    print("Starting barbot")
    main()