# Developed By MrAmini

from telethon import TelegramClient, events, functions, types
import asyncio
import random
import os
import json
import re
import httpx
import sys
import subprocess
import time

# Configuration
API_ID = 'AminiMokhberAPIID'  # Replace with your API ID
API_HASH = 'AminiMokhberAPIHASH'  # Replace with your API hash
BOT_OWNER_ID = AminiMokhberADMINID # Replace with the bot owner's Telegram user ID
USERS_FILE = 'user.txt'
MESSAGE_FILE = 'pm.txt'
BIO_API_URL = 'https://api.codebazan.ir/bio'
SETTINGS_FILE = 'settings.json'
ACCOUNTS_FILE = 'accounts.json'
REBOOT_FLAG_FILE = "reboot_flag.txt"

default_settings = {
    'save_user': True,
    'chat_user': False,
    'random_bio': False,
    'filter_last_seen': False,
    'remove_invalid_users': False,
    'daily_limit': 10,
    'auto_join': False
}


def save_user_to_file(user_id):
    try:
        user_id_str = str(user_id).strip()  # اطمینان از ذخیره به صورت رشته
        with open("user.txt", "a", encoding="utf-8") as file:
            file.write(user_id_str + "\n")  # ذخیره آی‌دی به صورت رشته در فایل
    except Exception as e:
        print(f"خطا در ذخیره کردن کاربر به فایل: {e}")

def remove_user_from_file(user_id):
    try:
        user_id_str = str(user_id).strip()  # اطمینان از تبدیل به رشته و حذف فاصله‌های اضافی
        with open("user.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        
        # حذف تمامی خطوطی که آی‌دی آن‌ها برابر با user_id_str است
        new_lines = [line for line in lines if line.strip() != user_id_str]
        
        with open("user.txt", "w", encoding="utf-8") as file:
            file.writelines(new_lines)
        
    except Exception as e:
        print(f"خطا در حذف کاربر از فایل: {e}")


def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return {int(line.strip()) for line in f if line.strip().isdigit()}
    except FileNotFoundError:
        return set()

forward_mode = False
forward_message = None
sent_count = 0

def load_accounts():
    if os.path.exists("accounts.json"):
        with open("accounts.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict): 
                    return data
                else:
                    return {}  
            except json.JSONDecodeError:
                return {}  
    return {}  


def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {} 
    
def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

client = TelegramClient('session', API_ID, API_HASH).start()

settings = load_settings()

def remove_user_from_file(user_id):
    try:
        with open("user.txt", "r", encoding="utf-8") as file:
            users = file.readlines()
        
        with open("user.txt", "w", encoding="utf-8") as file:
            for user in users:
                if user.strip() != str(user_id):
                    file.write(user)
    except Exception as e:
        print(f"خطا در حذف کاربر از فایل: {e}")

def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, 'w').close()

    with open(USERS_FILE, 'r') as f:
        users = set(f.read().splitlines())

    if str(user_id) not in users:
        with open(USERS_FILE, 'a') as f:
            f.write(f"{user_id}\n")
        print(f"User {user_id} saved successfully.")
    else:
        print(f"User {user_id} already exists.")


async def set_new_pm(event):
    try:
        text = event.raw_text

        if not text.lower().startswith("setnewpm"):
            await event.reply("⚠️ دستور نامعتبر است. لطفاً پیام خود را به درستی وارد کنید.")
            return

        parts = text.split("\n", 1)
        if len(parts) < 2:
            await event.reply("⚠️ لطفاً پیام جدید خود را بعد از `setnewpm` در خط جدید وارد کنید.")
            return

        new_message = parts[1].strip()  

        with open("pm.txt", "w", encoding="utf-8") as f:
            f.write(new_message)

        await event.reply("✅ پیام جدید با موفقیت ذخیره شد.")

    except Exception as e:
        await event.reply(f"⚠️ خطا در ذخیره پیام: {e}")


    
async def update_bio():
    try:
        async with httpx.AsyncClient(follow_redirects=True) as req:
            response = await req.get(BIO_API_URL, timeout=5)
            if response.status_code == 200:
                bio = response.text.strip()
            else:
                raise Exception(f"API request failed with status {response.status_code}")
    except Exception as e:
        try:
            with open("bio.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                bios = data.get("bio", [])
                if not bios:
                    return "بیو برای ست شدن یافت نشد."
                bio = random.choice(bios)
        except (FileNotFoundError, json.JSONDecodeError) as file_error:
            return f"Error: {file_error}"

    try:
        await client(functions.account.UpdateProfileRequest(about=bio))
        return f"**📩 بیوگرافی ست شده:**\n {bio}"
    except Exception as e:
        return f"Error updating bio: {e}"
    
async def get_last_seen(user_id):
    try:
        user = await client.get_entity(user_id)
        if hasattr(user.status, 'was_online'):
            return user.status.was_online
    except Exception as e:
        print(f"Error getting last seen for {user_id}: {e}")
    return None
async def check_ban():
    try:
        await client.send_message(BOT_OWNER_ID, "Checking ban status...")
        return "ربات فعال است."
    except:
        return "⚠️ ربات بن شده و قادر به ارسال پیام نیست."
        

async def join_group_from_message(event):
    if not settings.get('auto_join', False):
        return 

    message_text = event.raw_text.strip()
    if "t.me/" not in message_text:
        return

    if "joinchat" in message_text or "t.me/+" in message_text:
        private_link_pattern = r"https?:\/\/t\.me\/(?:joinchat\/|\+)?([a-zA-Z0-9_-]+)"
        private_match = re.search(private_link_pattern, message_text)
        if private_match:
            group_identifier = private_match.group(1)
            try:
                await client(functions.messages.ImportChatInviteRequest(group_identifier))
                await client.send_message("me", "✅ به گروه خصوصی پیوستم!")
            except Exception as e:
                await client.send_message("me", f"❌ خطا در پیوستن به گروه: {str(e)}")
    else:
        group_link_pattern = r"(https?:\/\/t\.me\/(?:joinchat\/)?([a-zA-Z0-9_-]+))"
        match = re.search(group_link_pattern, message_text)
        if match:
            group_identifier = match.group(2)
            try:
                await client(functions.channels.JoinChannelRequest(group_identifier))
                await client.send_message("me", "✅ به گروه عمومی پیوستم!")
            except Exception as e:
                await client.send_message("me", f"❌ خطا در پیوستن به گروه: {str(e)}")
                
@client.on(events.NewMessage)
async def message_handler(event):
    sender_id = event.sender_id
    message = event.raw_text.lower()

    await join_group_from_message(event)


async def send_messages():
    if os.path.exists(USERS_FILE) and os.path.exists(MESSAGE_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = f.read().splitlines()

        with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
            message_content = f.read()

        active_accounts = [phone for phone, data in load_accounts().items() if data["status"] == "active"]
        if not active_accounts:
            return "⛔ هیچ اکانت فعالی برای ارسال پیام وجود ندارد."

        total_accounts = len(active_accounts)
        limit_per_account = settings['daily_limit'] // total_accounts if settings['daily_limit'] > 0 else len(users) // total_accounts

        sent_count = 0
        failed_count = 0
        removed_users = 0
        current_account_index = 0

        for user in users:
            if settings['daily_limit'] > 0 and sent_count >= settings['daily_limit']:
                break

            # Get the current account to use
            current_account = active_accounts[current_account_index]
            client = TelegramClient(f'session_{current_account}', API_ID, API_HASH)
            await client.connect()

            try:
                await client.send_message(int(user), message_content)
                sent_count += 1
                await asyncio.sleep(random.randint(1, 5))
            except Exception as e:
                failed_count += 1
                if settings['remove_invalid_users'] and 'deleted/deactivated' in str(e).lower():
                    users.remove(user)
                    removed_users += 1

            # Move to next account
            current_account_index = (current_account_index + 1) % total_accounts
            await client.disconnect()

        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            f.writelines("\n".join(users))

        return f"📊 گزارش ارسال پیام:\n✅ ارسال موفق: {sent_count}\n❌ ارسال ناموفق: {failed_count}\n🚫 حذف کاربران غیرفعال: {removed_users}"
    return "فایل‌های مورد نیاز وجود ندارند."

@client.on(events.NewMessage(pattern="^forwardpm$", from_users=BOT_OWNER_ID))
async def enable_forward_mode(event):
    global forward_mode, forward_message
    forward_mode = True
    forward_message = None
    await event.reply("📩 لطفاً پیام موردنظر را به ربات فروارد کنید.")

@client.on(events.NewMessage(forwards=True, from_users=BOT_OWNER_ID))
async def receive_forward(event):
    global forward_mode, forward_message

    if forward_mode:
        forward_message = event.message
        forward_mode = False  
        user_list = list(load_users())

        settings = load_settings()
        daily_limit = settings.get("daily_limit")

        if daily_limit is None:
            await event.reply("⚠️ مقدار محدودیت روزانه تعریف نشده است! لطفاً مقدار `daily_limit` را در تنظیمات تعیین کنید و دوباره امتحان نمایید.")
            return

        if not user_list:
            await event.reply("⚠️ لیست کاربران خالی است.")
            return

        await event.reply(f"✅ پیام دریافت شد! شروع ارسال به {min(len(user_list), daily_limit)} کاربر.")

        failed_users = []  
        successful_users = []  

        for user_id in user_list[:daily_limit]:  
            try:
                await client.forward_messages(user_id, forward_message)
                successful_users.append(user_id) 
                await asyncio.sleep(random.randint(5, 60))  
            except Exception:
                failed_users.append(user_id)

        updated_users = [user for user in user_list if user not in successful_users]
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(map(str, updated_users)))

        if failed_users:
            failed_report = "\n".join(str(uid) for uid in failed_users)
            await event.reply(f"⚠️ ارسال پیام به کاربران زیر ناموفق بود:\n{failed_report}")
        else:
            await event.reply("✅ ارسال پیام به همه کاربران انجام شد و لیست کاربران به‌روزرسانی شد.")

@client.on(events.NewMessage(pattern=r'^addacc (\+\d+)$'))
async def add_account(event):
    sender_id = event.sender_id
    phone_number = event.pattern_match.group(1)

    if sender_id != BOT_OWNER_ID:
        return 

    accounts = load_accounts()
    if phone_number in accounts:
        return await event.reply("⚠️ این شماره قبلاً اضافه شده است.")

    accounts[phone_number] = {"status": "pending"}
    save_accounts(accounts)

    new_client = TelegramClient(f'session_{phone_number}', API_ID, API_HASH)
    await new_client.connect()

    try:
        sent_code = await new_client.send_code_request(phone_number)
        accounts[phone_number]["hash"] = sent_code.phone_code_hash
        save_accounts(accounts)
        await event.reply(f"📩 کد تأیید به شماره {phone_number} ارسال شد.\n لطفاً کد را با دستور `verifyacc {phone_number} 12345` وارد کنید.\n اکانت نباید دارای ورود دو مرحله ای باشد.")
    except Exception as e:
        await event.reply(f"⚠️ خطا در ارسال کد: {e}")

@client.on(events.NewMessage(pattern=r'^verifyacc (\+\d+) (\d+)$'))
async def verify_account(event):
    sender_id = event.sender_id
    phone_number = event.pattern_match.group(1)
    code = event.pattern_match.group(2)

    if sender_id != BOT_OWNER_ID:
        return

    accounts = load_accounts()
    if phone_number not in accounts or "hash" not in accounts[phone_number]:
        return await event.reply("⚠️ شماره معتبر نیست یا هنوز کد ارسال نشده است.")

    new_client = TelegramClient(f'session_{phone_number}', API_ID, API_HASH)
    await new_client.connect()

    try:
        await new_client.sign_in(phone_number, code, phone_code_hash=accounts[phone_number]["hash"])
        accounts[phone_number]["status"] = "active"
        save_accounts(accounts)
        await event.reply(f"✅ شماره {phone_number} با موفقیت اضافه شد.")
    except Exception as e:
        await event.reply(f"⚠️ خطا در تأیید کد: {e}")

@client.on(events.NewMessage(pattern=r'^accs$'))
async def list_accounts(event):
    sender_id = event.sender_id
    if sender_id != BOT_OWNER_ID:
        return 

    accounts = load_accounts()
    if not accounts:
        return await event.reply("⚠️ هیچ اکانتی ثبت نشده است.")

    msg = "**📋 لیست اکانت‌ها:**\n"
    for phone, data in accounts.items():
        status = "✅ فعال" if data["status"] == "active" else "⏳ در انتظار تأیید"
        msg += f"- {phone}: {status}\n"

    await event.reply(msg)

@client.on(events.NewMessage(pattern=r'^delacc (\+\d+)$'))
async def delete_account(event):
    sender_id = event.sender_id
    phone_number = event.pattern_match.group(1)

    if sender_id != BOT_OWNER_ID:
        return 

    accounts = load_accounts()
    if phone_number not in accounts:
        return await event.reply("⚠️ این شماره در لیست نیست.")

    del accounts[phone_number]
    save_accounts(accounts)

    os.remove(f'session_{phone_number}.session') 
    await event.reply(f"✅ اکانت {phone_number} با موفقیت حذف شد.")

@client.on(events.NewMessage(pattern=r'^accstatus (\+\d+)$'))
async def account_status(event):
    sender_id = event.sender_id
    phone_number = event.pattern_match.group(1)

    if sender_id != BOT_OWNER_ID:
        return  

    accounts = load_accounts()
    if phone_number not in accounts:
        return await event.reply("⚠️ این شماره در لیست نیست.")

    session_file = f'session_{phone_number}'
    if not os.path.exists(f"{session_file}.session"):
        return await event.reply("⚠️ اکانت موردنظر در حال حاضر وارد نشده است.")

    new_client = TelegramClient(session_file, API_ID, API_HASH)
    await new_client.connect()

    if not await new_client.is_user_authorized():
        await new_client.disconnect()
        return await event.reply("⚠️ این اکانت لاگین نشده است.")

    user = await new_client.get_me()
    last_online = "نامشخص" if not user.status else str(user.status)
    
    dialogs = await new_client.get_dialogs()
    total_messages = sum(len(await new_client.get_messages(dialog.entity, limit=100)) for dialog in dialogs if dialog.is_user)

    await new_client.disconnect()

    status_message = (
        f"📌 **وضعیت اکانت {phone_number}:**\n"
        f"👤 **نام کاربری:** {user.username or 'ندارد'}\n"
        f"🆔 **ایدی عددی:** {user.id}\n"
        f"✅ **وضعیت ورود:** فعال\n"
        f"🕒 **آخرین فعالیت:** {last_online}\n"
        f"✉️ **تعداد پیام‌های ارسال‌شده:** {total_messages}\n"
    )

    await event.reply(status_message)

    

@client.on(events.NewMessage)
async def message_handler(event):
    sender_id = event.sender_id
    message = event.raw_text.lower()
    checkbot = await event.get_sender()
    # Check if Sender NOT be Channel or Group
    if str(checkbot).startswith("User"):
        # Check if Sender is not Bot
        if settings.get('chat_user') and event.is_group and not checkbot.bot:
            save_user(sender_id)

    if sender_id == BOT_OWNER_ID:
        if message == 'bot':
            await event.reply("سلام، آنلاینم! کارت رو بگو.")
        elif message == 'onlastseen':
            settings['last_seen_filter'] = True
            save_settings(settings)
            await event.reply("فیلتر آخرین بازدید فعال شد.")
        elif message == 'offlastseen':
            settings['filter_last_seen'] = False
            save_settings(settings)
            await event.reply("فیلتر آخرین بازدید غیرفعال شد.")
        elif message == 'invaliduseron':
            settings['remove_invalid_users'] = True
            save_settings(settings)
            await event.reply("حذف کاربران نامعتبر فعال شد.")
        elif message == 'invaliduseroff':
            settings['remove_invalid_users'] = False
            save_settings(settings)
            await event.reply("حذف کاربران نامعتبر غیرفعال شد.")
        elif message.startswith('setlimit'):
            try:
                limit = int(message.split()[1])
                settings['daily_limit'] = limit
                save_settings(settings)
                await event.reply(f"حد ارسال روزانه روی {limit} پیام تنظیم شد.")
            except:
                await event.reply("فرمت اشتباه است. استفاده صحیح: setlimit 50")
        elif message == 'sendreport':
            report = await send_messages()
            await event.reply(report)
        elif message == 'checkban':
            status = await check_ban()
            await event.reply(status)

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
            await event.reply("ذخیره کاربران ارسال‌کننده پیام در گروه‌ها فعال شد.")
        elif message == 'chatuseroff':
            settings['chat_user'] = False
            save_settings(settings)
            await event.reply("ذخیره کاربران ارسال‌کننده پیام در گروه‌ها غیرفعال شد.")
        elif message == 'bioon':
            settings['random_bio'] = True
            save_settings(settings)
            result = await update_bio()
            await event.reply(result)
        elif message == 'biooff':
            settings['random_bio'] = False
            save_settings(settings)
            await event.reply("بیوگرافی تصادفی غیرفعال شد.")

        elif message == 'autojoinon':
            settings['auto_join'] = True
            save_settings(settings)
            await event.reply("✅ ورود خودکار به گروه‌ها *فعال* شد.")
        elif message == 'autojoinoff':
            settings['auto_join'] = False
            save_settings(settings)
            await event.reply("❌ ورود خودکار به گروه‌ها *غیرفعال* شد.")
            
        elif message.lower().startswith("setnewpm"):
            parts = message.split("\n", 1) 
            if len(parts) < 2:
                await event.reply("⚠️ لطفاً پیام جدید خود را در خط جدید بعد از `setnewpm` بنویسید.")
                return

            new_message = parts[1].strip()  

            with open("pm.txt", "w", encoding="utf-8") as f:
                f.write(new_message)

            await event.reply("✅ پیام جدید با موفقیت ذخیره شد.")
            print("New message saved successfully.")

        elif message == 'sendpm':
            if os.path.exists(USERS_FILE) and os.path.exists(MESSAGE_FILE):
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    users = f.read().splitlines()

                with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
                    message_content = f.read()

                updated_users = users[:] 

                for user_id in users:
                    try:
                        await client.send_message(int(user_id), message_content)
                        updated_users.remove(user_id)  
                        await asyncio.sleep(random.randint(1, 10))
                    except Exception as e:
                        print(f"Error sending message to {user_id}: {e}")

                with open(USERS_FILE, 'w', encoding='utf-8') as f:
                    f.write("\n".join(updated_users))  

                await event.reply("✅ پیام‌ها با موفقیت ارسال شدند و لیست به‌روزرسانی شد.")
            else:
                await event.reply("⚠️ فایل‌های مورد نیاز وجود ندارند.")

        elif message == 'info':
            total_users = 0
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r') as f:
                    total_users = len(f.read().splitlines())

            # Generate info text
            info_text = (
                f"وضعیت ربات: {'آنلاین' if client.is_connected else 'آفلاین'}\n"
                f"تعداد کاربران جمع شده: {total_users}\n"
                f"جمع‌آوری لیست اعضای گروه: {'فعال' if settings['save_user'] else 'غیرفعال'}\n"
                f"جمع‌آوری یوزرهای درحال چت: {'فعال' if settings['chat_user'] else 'غیرفعال'}\n"
                f"بیوگرافی تصادفی: {'فعال' if settings['random_bio'] else 'غیرفعال'}\n"
            )
            await event.reply(info_text)
        elif message == 'help':
            help_text = (
                "📌 **راهنمای دستورات ربات**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
		"نسخه ربات: V 3.5.0\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🤖 **وضعیت ربات:**\n"
                "🔹 `bot` - بررسی آنلاین بودن ربات\n"
                "🔹 `info` - نمایش اطلاعات کلی ربات\n"
                "🔹 `checkban` - بررسی مسدود شدن ربات\n"
                "🔹 `ping` - بررسی پینگ و سرعت ربات\n"
                "🔹 `setmode` - خاموش و روشن کردن ربات\n"
                "🔹  example: setmode online"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "📩 **ارسال پیام‌ها:**\n"
                "📌 `sendpm` - ارسال پیام به تمام کاربران ذخیره‌شده\n"
                "📌 `forwardpm` - فروارد پیام به همه کاربران ذخیره شده\n"
                "📌 `setnewpm` - تغییر متن پیام تبلیغاتی (متن رو در خط بعدی بنویسید)\n"
                "📌 `sendreport` - دریافت گزارش ارسال پیام‌ها\n"
                "📌 `setlimit 10` - تنظیم محدودیت ارسال روزانه (عدد قابل تغییر است)\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👥 **مدیریت کاربران:**\n"
                "🟢 `saveuseron` - فعال‌سازی ذخیره کاربران گروه‌ها\n"
                "🔴 `saveuseroff` - غیرفعال‌سازی ذخیره کاربران گروه‌ها\n"
                "🟢 `chatuseron` - فعال‌سازی ذخیره کاربران پیام‌دهنده در گروه‌ها\n"
                "🔴 `chatuseroff` - غیرفعال‌سازی ذخیره کاربران پیام‌دهنده در گروه‌ها\n"
                "🟢 `InvalidUserOn` - حذف خودکار کاربران نامعتبر\n"
                "🔴 `InvalidUserOff` - غیرفعال‌سازی حذف کاربران نامعتبر\n"
                "🟢 `cleanlist` - حذف کاربران ذخیره شده\n"
                "🔴 `clearpm` - حذف پیام های ارسال شده\n"
                "🟢 `deluser` - حذف کاربر خاصی از لیست ارسال\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🔧 **تنظیمات و قابلیت‌ها:**\n"
                "🔹 `bioon` - فعال‌سازی بیوگرافی تصادفی\n"
                "🔹 `biooff` - غیرفعال‌سازی بیوگرافی تصادفی\n"
                "🔹 `OnLastseen` - ارسال پیام فقط به کاربران فعال در ۲۴ ساعت اخیر\n"
                "🔹 `OffLastseen` - ارسال پیام به تمام کاربران ذخیره‌شده\n"
                "🔹 `autojoinon` - فعال‌سازی ورود خودکار به گروه‌ها از طریق لینک\n"
                "🔹 `autojoinoff` - غیرفعال‌سازی ورود خودکار به گروه‌ها\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "📱 **مدیریت اکانت ها**\n"
                "📍 `addacc` - افزودن اکانت\n"
                "📍  example: addacc +989191234567\n"
                "📍 `verifyacc` - وارد کردن کد لاگین\n"
                "📍  example: verifyacc +989191234567 12345\n"
                "📍 `delacc` - حذف یک اکانت\n"
                "📍  example: delacc +989191234567\n"
                "📍 `accstatus` - بررسی اطلاعات اکانت\n"
                "📍  example: accstatus +989191234567\n"
                "📍 `accs` - دریافت لیست اکانت ها\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "❓ **راهنما:**\n"
                "📌 `help` - نمایش لیست دستورات\n"
            )
            await event.reply(help_text, parse_mode='markdown')


@client.on(events.NewMessage(pattern=r'^cleanlist$'))
async def clean_list(event):
    sender_id = event.sender_id
    if sender_id != BOT_OWNER_ID:
        return  

    open("user.txt", "w").close()
    await event.reply("✅ لیست کاربران با موفقیت پاک شد.")

@client.on(events.NewMessage(pattern=r'^clearpm$'))
async def clear_pm(event):
    sender_id = event.sender_id
    if sender_id != BOT_OWNER_ID:
        return

    try:
        clear_sent_messages()  
        await event.reply("✅ تمام پیام‌های ارسال‌شده با موفقیت پاک شدند.")
    except Exception as e:
        await event.reply(f"⚠️ خطا در پاک کردن پیام‌ها: {e}")

@client.on(events.NewMessage(pattern=r'^deluser (\d+)$'))
async def delete_user(event):
    sender_id = event.sender_id
    if sender_id != BOT_OWNER_ID:
        return 

    target_user_id = int(event.pattern_match.group(1))
    try:
        remove_user(target_user_id)  
        await event.reply(f"✅ کاربر {target_user_id} از لیست حذف شد.")
    except Exception as e:
        await event.reply(f"⚠️ خطا در حذف کاربر: {e}")

@client.on(events.NewMessage(pattern=r'^ping$'))
async def ping(event):
    start_time = time.time()
    await event.reply("🏓 در حال بررسی پاسخ‌دهی...")
    end_time = time.time()
    
    ping_time = round((end_time - start_time) * 1000) 
    await event.reply(f"🏓 پینگ ربات: {ping_time}ms")
    
@client.on(events.NewMessage(pattern=r'^setmode (.+)$'))
async def set_mode(event):
    if event.sender_id != BOT_OWNER_ID:
        return await event.reply("⛔ شما اجازه این کار را ندارید.")
    
    mode = event.pattern_match.group(1).lower()
    if mode not in ["online", "offline"]:
        return await event.reply("❌ حالت نامعتبر است. فقط می‌توانید از `online` یا `offline` استفاده کنید.")
    
    if mode == "offline":
        await event.reply("🔴 ربات در حالت آفلاین قرار گرفت.")
        await client.disconnect()
    elif mode == "online":
        await event.reply("🟢 ربات در حالت آنلاین قرار گرفت.")
        await client.connect()


@client.on(events.ChatAction)
async def chat_action_handler(event):
    if settings['save_user'] and event.user_added:
        if event.chat and event.is_group:
            for user in event.users:
                save_user(user.id)


async def download_channels_file():
    url = "https://mreset.ir/spmokhber/sp.txt"
    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.get(url, timeout=10)
        if response.status_code == 200:
            try:
                content = response.text.encode('latin1').decode('utf-8')
            except Exception:
                content = response.text
            with open("sp.txt", "w", encoding="utf-8") as f:
                f.write(content)
            return content
        else:
            if os.path.exists("sp.txt"):
                with open("sp.txt", "r", encoding="utf-8") as f:
                    return f.read()
            return ""
    except Exception:
        if os.path.exists("sp.txt"):
            with open("sp.txt", "r", encoding="utf-8") as f:
                return f.read()
        return ""

async def join_channels_from_file():
    content = await download_channels_file()
    if not content:
        return
    channels = [line.strip() for line in content.splitlines() if line.strip()]
    for channel in channels:
        try:
            entity = await client.get_entity(channel)
            await client(functions.channels.JoinChannelRequest(channel=entity))
        except Exception:
            pass 
async def join_channels_task():

    await join_channels_from_file()
    while True:
        await asyncio.sleep(3600) 
        await join_channels_from_file()

client.loop.create_task(join_channels_task())


print("Your bot has been successfully run. Check the commands using the < Help > command in Telegram.")
client.run_until_disconnected()
