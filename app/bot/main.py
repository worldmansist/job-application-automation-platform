import asyncio

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.core.config import settings


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am a bot for managing applications."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - start the bot\n"
        "/help - show help\n"
        "/new_vacancy - create a new vacancy\n"
        "/cancel - cancel the current dialogue\n"
        "/status - check the status of your applications"
    )


COMPANY, POSITION, URL, DESCRIPTION = range(4)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.api_base_url}/applications"
            )
            response.raise_for_status()
    except httpx.HTTPError:
        await update.message.reply_text(
            "Could not get applications. Make sure FastAPI is running."
        )
        return

    applications = response.json()["applications"]
    if not applications:
        await update.message.reply_text("You have no applications yet.")
        return

    lines = [
        f"ID {application['id']}: "
        f"{application['company']} - "
        f"{application['position']} - "
        f"{application['status']}"
        for application in applications
    ]
    await update.message.reply_text("\n".join(lines))

async def new_vacancy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Enter the company name:")
    return COMPANY


async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["company"] = update.message.text
    await update.message.reply_text("Enter the position:")
    return POSITION


async def get_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["position"] = update.message.text
    await update.message.reply_text("Send the vacancy URL:")
    return URL


async def get_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["url"] = update.message.text
    await update.message.reply_text("Add a short description:")
    return DESCRIPTION


async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.api_base_url}/applications",
                json={
                    "company": context.user_data["company"],
                    "position": context.user_data["position"],
                    "url": context.user_data["url"],
                    "description": context.user_data["description"],
                },
            )
            response.raise_for_status()
    except httpx.HTTPError:
        await update.message.reply_text(
            "Could not save the application. Make sure FastAPI is running."
        )
        context.user_data.clear()
        return ConversationHandler.END

    application = response.json()["application"]
    await update.message.reply_text(
        f"Application created. ID: {application['id']}"
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Creating the application was cancelled.")
    return ConversationHandler.END


def main():
    if not settings.telegram_bot_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not configured in the .env file"
        )

    asyncio.set_event_loop(asyncio.new_event_loop())

    application = Application.builder().token(
        settings.telegram_bot_token
    ).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))

    vacancy_conversation = ConversationHandler(
        entry_points=[CommandHandler("new_vacancy", new_vacancy)],
        states={
            COMPANY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)
            ],
            POSITION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_position)
            ],
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_url)],
            DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_description,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(vacancy_conversation)

    application.run_polling()


if __name__ == "__main__":
    main()