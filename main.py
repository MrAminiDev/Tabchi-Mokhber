# Developed By MrAmini
# Updated By github.com/sanwdp

import os
import json
import re
import logging
import asyncio
from telethon import TelegramClient, events, functions, Button

# ------------------ پیکربندی ------------------
API_ID = 'API ID'  # جایگزین کنید با API ID خودتان
API_HASH = 'YOUR_API_HASH'  # جایگزین کنید با API HASH خودتان
BOT_TOKEN = 'YOUR_BOT_TOKEN'  # جایگزین کنید با توکن ربات خود
BOT_OWNER_ID = 12345678  # جایگزین کنید با آیدی تلگرام شما (ادمین ربات)

# ------------------ مسیر فایل‌ها ------------------
USERS_FILE = 'users.json'
MESSAGE_FILE = 'message.txt'
SETTINGS_FILE = 'settings.json'

# ------------------ تنظیمات لاگینگ ------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ بارگذاری تنظیمات ------------------
if os.path.exists(SETTINGS_FILE):
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        logger.info("تنظیمات با موفقیت بارگذاری شدند.")
    except Exception as e:
        logger.error(f"خطا در بارگذاری تنظیمات: {e}")
        settings = {}
else:
    settings = {
        'auto_join': True,
        'random_bio': False,
        # سایر تنظیمات پیش‌فرض در صورت نیاز
    }

def save_settings(settings_dict):
    """ذخیره تنظیمات در فایل JSON."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, ensure_ascii=False, indent=4)
        logger.info("تنظیمات ذخیره شدند.")
    except Exception as e:
        logger.error(f"خطا در ذخیره تنظیمات: {e}")

# ------------------ توابع کمکی ------------------
async def update_bio():
    """
    به‌روزرسانی بیوگرافی ربات با یک مقدار تصادفی.
    پیاده‌سازی واقعی را برحسب نیاز تغییر دهید.
    """
    logger.info("در حال به‌روزرسانی بیوگرافی...")
    await asyncio.sleep(0.5)
    logger.info("بیوگرافی به‌روزرسانی شد.")

async def check_ban():
    """
    بررسی اینکه آیا ربات مسدود شده است یا خیر.
    منطق واقعی را برحسب نیاز پیاده‌سازی کنید.
    """
    try:
        return "ربات آنلاین است."
    except Exception as e:
        logger.error(f"خطا در check_ban: {e}")
        return "⚠️ ربات بن شده و قادر به ارسال پیام نیست."

# ------------------ راه‌اندازی کلاینت تلگرام ------------------
client = TelegramClient('session', API_ID, API_HASH)

# ------------------ توابع دستوری ربات ------------------
async def join_group_from_message(event):
    """
    اگر در پیام لینک دعوت گروه وجود داشته باشد، ربات به آن گروه می‌پیوندد.
    """
    if settings.get('auto_join', False):
        message_text = event.raw_text
        group_link_pattern = r"(https?:\/\/t\.me\/[a-zA-Z0-9_]+)"
        match = re.search(group_link_pattern, message_text)
        if match:
            group_link = match.group(1)
            invite_hash = group_link.split("/")[-1]
            try:
                await client(functions.messages.ImportChatInviteRequest(invite_hash))
                await event.reply("✅ به گروه جدید پیوستم!")
                logger.info(f"پیوستن به گروه با invite hash: {invite_hash}")
            except Exception as e:
                await event.reply(f"❌ خطا در پیوستن به گروه: {e}")
                logger.error(f"خطا در پیوستن به گروه: {e}")

@client.on(events.NewMessage)
async def message_handler(event):
    """
    هندلر دریافت پیام‌ها و اجرای دستورات.
    """
    # تنها ادمین ربات می‌تواند از آن استفاده کند.
    if event.sender_id != BOT_OWNER_ID:
        await event.reply("شما اجازه استفاده از این ربات را ندارید.")
        return

    sender_id = event.sender_id
    message = event.raw_text.lower()

    # بررسی لینک دعوت گروه
    await join_group_from_message(event)

    # ------------------ مدیریت دستورات ------------------
    if message == 'bot':
        status = await check_ban()
        await event.reply(status)

    elif message == 'sendpm':
        await event.reply("در حال ارسال پیام به کاربران...")
        await send_messages()

    elif message == 'saveuseron':
        settings['save_user'] = True
        save_settings(settings)
        await event.reply("ذخیره کاربران گروه فعال شد.")

    elif message == 'saveuseroff':
        settings['save_user'] = False
        save_settings(settings)
        await event.reply("ذخیره کاربران گروه غیرفعال شد.")

    elif message == 'chatuseron':
        settings['chat_user'] = True
        save_settings(settings)
        await event.reply("ذخیره کاربران پیام‌دهنده فعال شد.")

    elif message == 'chatuseroff':
        settings['chat_user'] = False
        save_settings(settings)
        await event.reply("ذخیره کاربران پیام‌دهنده غیرفعال شد.")

    elif message == 'autojoinon':
        settings['auto_join'] = True
        save_settings(settings)
        await event.reply("ورود خودکار به گروه‌ها از طریق لینک فعال شد.")

    elif message == 'autojoinoff':
        settings['auto_join'] = False
        save_settings(settings)
        await event.reply("ورود خودکار به گروه‌ها از طریق لینک غیرفعال شد.")

    elif message == 'bioon':
        settings['random_bio'] = True
        save_settings(settings)
        await update_bio()
        await update_bio()
        await event.reply("بیوگرافی تصادفی فعال شد.")

    elif message == 'biooff':
        settings['random_bio'] = False
        save_settings(settings)
        await event.reply("بیوگرافی تصادفی غیرفعال شد.")

    elif message == 'info':
        bio_status = "فعال" if settings.get('random_bio') else "غیرفعال"
        info_text = f"اطلاعات ربات:\nAPI ID: {API_ID}\nوضعیت بیو: {bio_status}"
        await event.reply(info_text)

    elif message == 'onlastseen':
        settings['last_seen'] = True
        save_settings(settings)
        await event.reply("ارسال پیام به کاربران فعال در 24 ساعت گذشته فعال شد.")

    elif message == 'offlastseen':
        settings['last_seen'] = False
        save_settings(settings)
        await event.reply("ارسال پیام به تمام کاربران ذخیره‌شده فعال شد.")

    elif message == 'invaliduseron':
        settings['invalid_user'] = True
        save_settings(settings)
        await event.reply("حذف خودکار کاربران نامعتبر فعال شد.")

    elif message == 'invaliduseroff':
        settings['invalid_user'] = False
        save_settings(settings)
        await event.reply("حذف خودکار کاربران نامعتبر غیرفعال شد.")

    elif message == 'sendreport':
        await event.reply("در حال تهیه گزارش ارسال پیام...")

    elif message.startswith('setlimit'):
        try:
            parts = message.split()
            if len(parts) == 2:
                limit = int(parts[1])
                settings['daily_limit'] = limit
                save_settings(settings)
                await event.reply(f"محدودیت ارسال پیام روزانه به {limit} عدد تنظیم شد.")
            else:
                await event.reply("فرمت دستور صحیح نیست. مثال: setlimit 10")
        except ValueError:
            await event.reply("عدد وارد شده صحیح نیست.")

    elif message == 'checkban':
        ban_status = await check_ban()
        await event.reply(ban_status)

    elif message == 'help':
        # استفاده از منوی شیشه‌ای به عنوان پنل دستورات
        help_text = "📌 *منوی دستورات ربات*:\nبرای استفاده از هر دستور، روی دکمه مربوطه کلیک کنید."
        buttons = [
            [Button.inline("وضعیت ربات", data=b'cmd_bot'), Button.inline("اطلاعات ربات", data=b'cmd_info')],
            [Button.inline("ارسال پیام", data=b'cmd_sendpm'), Button.inline("گزارش ارسال", data=b'cmd_sendreport')],
            [Button.inline("فعال‌سازی ذخیره کاربر", data=b'cmd_saveuseron'), Button.inline("غیرفعال‌سازی ذخیره کاربر", data=b'cmd_saveuseroff')],
            [Button.inline("فعال‌سازی پیام‌دهنده", data=b'cmd_chatuseron'), Button.inline("غیرفعال‌سازی پیام‌دهنده", data=b'cmd_chatuseroff')],
            [Button.inline("فعال‌سازی بیو", data=b'cmd_bioon'), Button.inline("غیرفعال‌سازی بیو", data=b'cmd_biooff')],
            [Button.inline("فعال‌سازی ورود خودکار", data=b'cmd_autojoinon'), Button.inline("غیرفعال‌سازی ورود خودکار", data=b'cmd_autojoinoff')],
            [Button.inline("ارسال به کاربران فعال", data=b'cmd_onlastseen'), Button.inline("ارسال به تمام کاربران", data=b'cmd_offlastseen')],
            [Button.inline("فعال‌سازی حذف کاربر نامعتبر", data=b'cmd_invaliduseron'), Button.inline("غیرفعال‌سازی حذف کاربر نامعتبر", data=b'cmd_invaliduseroff')],
            [Button.inline("تنظیم محدودیت", data=b'cmd_setlimit'), Button.inline("بررسی بن", data=b'cmd_checkban')],
            [Button.inline("بستن", data=b'cmd_close')]
        ]
        await event.reply(help_text, buttons=buttons, parse_mode='markdown')

    # در صورت نیاز می‌توانید دستورات دیگری نیز اضافه کنید.

async def send_messages():
    """
    ارسال پیام به کاربران موجود در فایل ذخیره‌شده.
    """
    if os.path.exists(USERS_FILE) and os.path.exists(MESSAGE_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
            with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
                message_content = f.read()
            
            for user_id in users:
                try:
                    await client.send_message(user_id, message_content)
                    logger.info(f"پیام به کاربر {user_id} ارسال شد.")
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"ارسال پیام به {user_id} با خطا مواجه شد: {e}")
        except Exception as e:
            logger.error(f"خطا در send_messages: {e}")
    else:
        logger.warning("فایل‌های کاربران یا پیام وجود ندارند.")

# ------------------ هندلر Callback برای دکمه‌های منوی شیشه‌ای ------------------
@client.on(events.CallbackQuery)
async def callback_handler(event):
    """
    هندلر مدیریت کلیک روی دکمه‌های منوی شیشه‌ای.
    """
    if event.sender_id != BOT_OWNER_ID:
        await event.answer("شما اجازه استفاده از این ربات را ندارید.", alert=True)
        return

    data = event.data
    if data == b'cmd_bot':
        status = await check_ban()
        await event.answer(status, alert=True)
    elif data == b'cmd_info':
        bio_status = "فعال" if settings.get('random_bio') else "غیرفعال"
        info_text = f"اطلاعات ربات:\nAPI ID: {API_ID}\nوضعیت بیو: {bio_status}"
        await event.answer(info_text, alert=True)
    elif data == b'cmd_sendpm':
        await send_messages()
        await event.answer("ارسال پیام به کاربران آغاز شد.", alert=True)
    elif data == b'cmd_sendreport':
        await event.answer("در حال تهیه گزارش ارسال پیام...", alert=True)
    elif data == b'cmd_saveuseron':
        settings['save_user'] = True
        save_settings(settings)
        await event.answer("ذخیره کاربران گروه فعال شد.", alert=True)
    elif data == b'cmd_saveuseroff':
        settings['save_user'] = False
        save_settings(settings)
        await event.answer("ذخیره کاربران گروه غیرفعال شد.", alert=True)
    elif data == b'cmd_chatuseron':
        settings['chat_user'] = True
        save_settings(settings)
        await event.answer("ذخیره کاربران پیام‌دهنده فعال شد.", alert=True)
    elif data == b'cmd_chatuseroff':
        settings['chat_user'] = False
        save_settings(settings)
        await event.answer("ذخیره کاربران پیام‌دهنده غیرفعال شد.", alert=True)
    elif data == b'cmd_bioon':
        settings['random_bio'] = True
        save_settings(settings)
        await update_bio()
        await update_bio()
        await event.answer("بیوگرافی تصادفی فعال شد.", alert=True)
    elif data == b'cmd_biooff':
        settings['random_bio'] = False
        save_settings(settings)
        await event.answer("بیوگرافی تصادفی غیرفعال شد.", alert=True)
    elif data == b'cmd_autojoinon':
        settings['auto_join'] = True
        save_settings(settings)
        await event.answer("ورود خودکار به گروه‌ها از طریق لینک فعال شد.", alert=True)
    elif data == b'cmd_autojoinoff':
        settings['auto_join'] = False
        save_settings(settings)
        await event.answer("ورود خودکار به گروه‌ها از طریق لینک غیرفعال شد.", alert=True)
    elif data == b'cmd_onlastseen':
        settings['last_seen'] = True
        save_settings(settings)
        await event.answer("ارسال پیام به کاربران فعال در 24 ساعت گذشته فعال شد.", alert=True)
    elif data == b'cmd_offlastseen':
        settings['last_seen'] = False
        save_settings(settings)
        await event.answer("ارسال پیام به تمام کاربران ذخیره‌شده فعال شد.", alert=True)
    elif data == b'cmd_invaliduseron':
        settings['invalid_user'] = True
        save_settings(settings)
        await event.answer("حذف خودکار کاربران نامعتبر فعال شد.", alert=True)
    elif data == b'cmd_invaliduseroff':
        settings['invalid_user'] = False
        save_settings(settings)
        await event.answer("حذف خودکار کاربران نامعتبر غیرفعال شد.", alert=True)
    elif data == b'cmd_setlimit':
        await event.answer("برای تنظیم محدودیت، لطفا از دستور متنی استفاده کنید:\nمثال: setlimit 10", alert=True)
    elif data == b'cmd_checkban':
        ban_status = await check_ban()
        await event.answer(ban_status, alert=True)
    elif data == b'cmd_close':
        await event.delete()
    else:
        await event.answer("دستور ناشناخته.", alert=True)

# ------------------ اجرای ربات ------------------
def main():
    """راه‌اندازی ربات تا زمان قطع اتصال."""
    client.start(bot_token=BOT_TOKEN)
    logger.info("ربات با موفقیت استارت شد.")
    client.run_until_disconnected()

if __name__ == '__main__':
    main()
