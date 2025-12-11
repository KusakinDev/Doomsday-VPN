import logging
import asyncio
import subprocess
import sys
import os
import tempfile
import html
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


TOKEN = "8231605061:AAEVY_3h43jswZWDtkN8SzdZAgsZEGFfLVo"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Админские и разрешённые пользователи
ADMIN_IDS = [814944449]
ALLOWED_USER_IDS = []

# Путь к файлу с разрешёнными user_id (по одному в строке)
DATA_DIR = os.path.dirname(__file__)
ALLOWED_USERS_FILE = os.path.join(DATA_DIR, 'allowed_users.txt')
VPN_TYPE_FILE = os.path.join(DATA_DIR, 'vpn_type.txt')

def read_vpn_type() -> str:
    """Read vpn_type.txt and return 'obfs' or 'masq' or 'unknown'."""
    try:
        with open(VPN_TYPE_FILE, 'r', encoding='utf-8') as f:
            v = f.read().strip().lower()
            if v in ('obfs', 'masq'):
                return v
            return 'unknown'
    except FileNotFoundError:
        return 'unknown'
    except Exception:
        logger.exception('Failed to read vpn_type file')
        return 'unknown'


async def broadcast_vpn_type(app: Application):
    """Send current vpn type to all allowed users and admins."""
    vpn = read_vpn_type()
    if vpn == 'unknown':
        text = 'Текущий тип VPN: неизвестен'
    else:
        text = f'Текущий тип VPN: {vpn}'

    recipients = set(ALLOWED_USER_IDS) | set(ADMIN_IDS)
    if not recipients:
        return
    for uid in recipients:
        try:
            await app.bot.send_message(chat_id=int(uid), text=text)
        except Exception:
            logger.exception('Failed to send vpn_type to %s', uid)

def load_allowed_users(path: str):
    ids = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    ids.append(int(s))
                except ValueError:
                    continue
    except FileNotFoundError:
        return []
    except Exception:
        return []
    return ids


def save_allowed_users(path: str, ids):
    # atomic write
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            pass
    fd, tmp = tempfile.mkstemp(dir=d if d else None)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            for uid in ids:
                f.write(str(int(uid)) + '\n')
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except Exception:
            pass

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        await update.message.reply_text('deny')
        return
    vpn = read_vpn_type()
    vpn_text = vpn if vpn != 'unknown' else 'неизвестен'
    await update.message.reply_text(f'Доступные команды: /start, /get_conf\nТекущий тип VPN: {vpn_text}')

# Обработчик текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        await update.message.reply_text('deny')
        return
    await update.message.reply_text(f'Вы написали: {update.message.text}')


def is_admin(user_id: int) -> bool:
    try:
        return int(user_id) in ADMIN_IDS
    except Exception:
        return False


def is_allowed(user_id: int) -> bool:
    try:
        uid = int(user_id)
    except Exception:
        return False
    return uid in ALLOWED_USER_IDS or uid in ADMIN_IDS


async def register_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run add-user.py and return output to the user (allowed users only)."""
    user = update.effective_user
    if not is_allowed(user.id):
        await update.message.reply_text('deny')
        return

    script_path = os.path.join(os.path.dirname(__file__), 'add-user.py')
    if not os.path.isfile(script_path):
        await update.message.reply_text('Registration script not found on server.')
        return

    try:
        # execute the script with the same python interpreter
        proc = await asyncio.create_subprocess_exec(
            sys.executable, script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        out_text = stdout.decode('utf-8').strip()
        err_text = stderr.decode('utf-8').strip()
        if proc.returncode != 0:
            #msg = err_text or out_text or 'Unknown error'
            #await update.message.reply_text(f'<pre>{html.escape(msg)}</pre>', parse_mode=ParseMode.HTML)
            return
        # send output back to user (preformatted)
        password = "algFNdE82VhJulMxov+JMdg5"
        password2 = "Zpov2bBbv7h916kp2/z2Cw=="
        msg1 = f"hy2://{password}@senator.giize.com:443?sni=www.github.com#MasqueradeVPN"
        msg2 = f"hy2://{password}@senator.giize.com:443?obfs-password={password2}#ObfsVPN"
        msg3 = (
            "Copy and create both connections in your Hysteria client.\n\n"
            "ANDROID: https://play.google.com/store/apps/details?id=app.hiddify.com\n"
            "WINDOWS: https://hiddify.com\n"
            "iOS: https://apps.apple.com/us/app/hiddify-proxy-vpn/id6596777532\n"
        )
        await update.message.reply_text(msg3)
        await update.message.reply_text(f'<pre>{html.escape(msg1)}</pre>', parse_mode=ParseMode.HTML)
        await update.message.reply_text(f'<pre>{html.escape(msg2)}</pre>', parse_mode=ParseMode.HTML)
        # # After successful registration, run update-config.py to refresh Hysteria config
        # update_script = os.path.join(os.path.dirname(__file__), 'update-config.py')
        # if os.path.isfile(update_script):
        #     try:
        #         proc2 = await asyncio.create_subprocess_exec(
        #             sys.executable, update_script,
        #             stdout=asyncio.subprocess.PIPE,
        #             stderr=asyncio.subprocess.PIPE
        #         )
        #         out2, err2 = await proc2.communicate()
        #         out2_text = out2.decode('utf-8').strip()
        #         err2_text = err2.decode('utf-8').strip()
        #         if proc2.returncode != 0:
        #             msg = err2_text or out2_text or f'Exit code {proc2.returncode}'
        #             await update.message.reply_text(f'<pre>{html.escape(msg)}</pre>', parse_mode=ParseMode.HTML)
        #         else:
        #             # send update-config output (shorten if very long)
        #             msg = out2_text if len(out2_text) < 1500 else out2_text[:1497] + '...'
        #             await update.message.reply_text(f'<pre>{html.escape(msg)}</pre>', parse_mode=ParseMode.HTML)
        #     except Exception:
        #         logger.exception('Failed to run update-config.py')
        #         await update.message.reply_text('Failed to run config update')
    except Exception as e:
        logger.exception('Failed to run add-user.py')
        await update.message.reply_text(f'Failed to register: {e}')


async def allow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить user_id в ALLOWED_USER_IDS (только админ). Usage: /allow 12345678"""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text('deny')
        return
    if not context.args:
        await update.message.reply_text('Usage: /allow <user_id>')
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text('user_id должен быть числом')
        return
    if uid in ALLOWED_USER_IDS:
        await update.message.reply_text(f'{uid} уже в списке разрешённых')
        return
    ALLOWED_USER_IDS.append(uid)
    # persist
    try:
        save_allowed_users(ALLOWED_USERS_FILE, ALLOWED_USER_IDS)
    except Exception:
        logger.exception('Failed to save allowed users')
    await update.message.reply_text(f'Добавлен: {uid}')


async def disallow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить user_id из ALLOWED_USER_IDS (только админ). Usage: /disallow 12345678"""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text('deny')
        return
    if not context.args:
        await update.message.reply_text('Usage: /disallow <user_id>')
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text('user_id должен быть числом')
        return
    if uid not in ALLOWED_USER_IDS:
        await update.message.reply_text(f'{uid} не в списке разрешённых')
        return
    ALLOWED_USER_IDS.remove(uid)
    # persist
    try:
        save_allowed_users(ALLOWED_USERS_FILE, ALLOWED_USER_IDS)
    except Exception:
        logger.exception('Failed to save allowed users')
    await update.message.reply_text(f'Удалён: {uid}')


async def list_allowed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список разрешённых пользователей (только админ)."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text('deny')
        return
    if not ALLOWED_USER_IDS:
        await update.message.reply_text('Список разрешённых пуст')
        return
    await update.message.reply_text('Разрешённые user_ids:\n' + '\n'.join(str(x) for x in ALLOWED_USER_IDS))

def main():
    # Создаем приложение
    # Load allowed users from file
    try:
        loaded = load_allowed_users(ALLOWED_USERS_FILE)
        ALLOWED_USER_IDS.clear()
        ALLOWED_USER_IDS.extend(loaded)
        logger.info('Loaded %d allowed users from %s', len(ALLOWED_USER_IDS), ALLOWED_USERS_FILE)
    except Exception:
        logger.exception('Failed to load allowed users')

    async def _on_startup(app: Application):
        try:
            await broadcast_vpn_type(app)
        except Exception:
            logger.exception('broadcast_vpn_type failed on startup')

    application = Application.builder().token(TOKEN).post_init(_on_startup).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", help_command))
    # Админские команды
    application.add_handler(CommandHandler("allow", allow_command))
    application.add_handler(CommandHandler("disallow", disallow_command))
    application.add_handler(CommandHandler("list_allowed", list_allowed_command))
    # Self-registration
    application.add_handler(CommandHandler("get_conf", register_me))
    # broadcast is scheduled via post_init when application starts
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()