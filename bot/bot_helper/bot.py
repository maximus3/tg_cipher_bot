import aiogram

from bot.config import get_settings


_settings = get_settings()
bot = aiogram.Bot(token=_settings.TG_HELPER_BOT_TOKEN)
