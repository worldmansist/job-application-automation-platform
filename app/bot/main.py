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
        "/edit_vacancy - edit an existing application\n"
        "/cancel - cancel the current dialogue\n"
        "/status - check the status of your applications"
    )


COMPANY, POSITION, URL, DESCRIPTION = range(4)
EDIT_ID, EDIT_FIELD, EDIT_VALUE = range(3)

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


async def edit_vacancy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Enter the application ID to edit:")
    return EDIT_ID


async def get_edit_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        application_id = int(update.message.text.strip())
        if application_id < 1:
            raise ValueError
    except ValueError:
        await update.message.reply_text("The ID must be a positive number.")
        return EDIT_ID

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.api_base_url}/applications/{application_id}"
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 404:
            await update.message.reply_text(
                "Application with this ID was not found. Enter another ID:"
            )
            return EDIT_ID
        await update.message.reply_text("Could not check the application ID.")
        return ConversationHandler.END
    except httpx.HTTPError:
        await update.message.reply_text(
            "Could not check the application ID. Make sure FastAPI is running."
        )
        return ConversationHandler.END

    context.user_data["application_id"] = application_id
    await update.message.reply_text(
        "Which field do you want to edit? Choose one:\n"
        "company, position, url, description, status"
    )
    return EDIT_FIELD


async def get_edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    field = update.message.text.strip().lower()
    allowed_fields = {"company", "position", "url", "description", "status"}
    if field not in allowed_fields:
        await update.message.reply_text(
            "Unknown field. Choose: company, position, url, description, status."
        )
        return EDIT_FIELD

    context.user_data["field"] = field
    await update.message.reply_text(f"Enter a new value for {field}:")
    return EDIT_VALUE


async def get_edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = update.message.text.strip()
    if not value:
        await update.message.reply_text("The new value cannot be empty.")
        return EDIT_VALUE

    application_id = context.user_data["application_id"]
    field = context.user_data["field"]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{settings.api_base_url}/applications/{application_id}",
                json={field: value},
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 404:
            message = "Application with this ID was not found."
        else:
            message = "Could not update the application."
        await update.message.reply_text(message)
        context.user_data.clear()
        return ConversationHandler.END
    except httpx.HTTPError:
        await update.message.reply_text(
            "Could not update the application. Make sure FastAPI is running."
        )
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text(
        f"Application {application_id} was updated: {field}."
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Editing the application was cancelled.")
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

    edit_conversation = ConversationHandler(
        entry_points=[CommandHandler("edit_vacancy", edit_vacancy)],
        states={
            EDIT_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_edit_id)
            ],
            EDIT_FIELD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_edit_field)
            ],
            EDIT_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_edit_value)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_edit)],
    )
    application.add_handler(edit_conversation)

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