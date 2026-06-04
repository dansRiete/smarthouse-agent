import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Hardcoded whitelist to prevent unauthorized access
ALLOWED_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text("SmartHouse AI Agent is online. Isolated and ready. How can I help?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        logging.warning(f"Unauthorized access attempt from User ID: {update.effective_user.id}")
        return
        
    user_text = update.message.text
    
    # Send an initial typing action
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        # Invoke the LangChain Agent
        agent = context.bot_data.get('agent')
        response = await asyncio.to_thread(agent.invoke, {"input": user_text})
        
        await update.message.reply_text(response["output"])
    except Exception as e:
        logging.error(f"Agent error: {e}")
        await update.message.reply_text(f"Sorry, I encountered an error: {str(e)}")

from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def scheduled_watchdog_task(agent, bot):
    # This is where the Python service will wake up, run an AI prompt automatically, 
    # and send you a Telegram message if something is wrong.
    try:
        logging.info("Running scheduled Watchdog check...")
        # response = await asyncio.to_thread(agent.invoke, {"input": "Check if DEH power is anomalous."})
        # await bot.send_message(chat_id=ALLOWED_USER_ID, text=response["output"])
    except Exception as e:
        logging.error(f"Watchdog error: {e}")

def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logging.error("TELEGRAM_BOT_TOKEN environment variable is not set. Exiting.")
        return

    from agent import create_agent
    try:
        smart_agent = create_agent()
    except Exception as e:
        logging.error(f"Failed to create agent: {e}")
        return

    application = Application.builder().token(bot_token).build()
    
    # Store agent in bot_data to access it inside handlers
    application.bot_data['agent'] = smart_agent

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Setup Watchdog Scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_watchdog_task, 
        'cron', 
        hour=10, 
        minute=0, 
        args=[smart_agent, application.bot]
    )
    scheduler.start()

    logging.info("Starting secure SmartHouse Telegram Agent with Autonomous Watchdog...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
