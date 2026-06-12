from telegram.ext import ApplicationBuilder, CommandHandler

from config import TELEGRAM_TOKEN
from bot.commands import (
    start,
    help_command,
    tipps,
    api_status,
    spiele,
    wmspiele,
    debugwm,
    wmalle,
    wmspiel,
    wmtipp,
    wmtipps,
    update_stats,
    refresh,
    evaluate,
)


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tipps", tipps))
    app.add_handler(CommandHandler("api", api_status))
    app.add_handler(CommandHandler("spiele", spiele))
    app.add_handler(CommandHandler("wmspiele", wmspiele))
    app.add_handler(CommandHandler("debugwm", debugwm))
    app.add_handler(CommandHandler("wmalle", wmalle))
    app.add_handler(CommandHandler("wmspiel", wmspiel))
    app.add_handler(CommandHandler("wmtipp", wmtipp))
    app.add_handler(CommandHandler("wmtipps", wmtipps))
    app.add_handler(CommandHandler("update_stats", update_stats))
    app.add_handler(CommandHandler("refresh", refresh))
    app.add_handler(CommandHandler("evaluate", evaluate))

    print("Bot läuft...")
    app.run_polling()


if __name__ == "__main__":
    main()