#!/usr/bin/env python3
import yaml
import subprocess
import sys

# prod
CONFIG_FILE = '/etc/hysteria/config.yaml'
USERS_FILE = '/etc/hysteria/users.txt'

# # local
# CONFIG_FILE = './config.yaml'
# USERS_FILE = './users.txt'

def read_passwords():
    """Чтение паролей из файла"""
    try:
        with open(USERS_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def update_config(passwords):
    """Обновление конфига Hysteria"""
    # Читаем текущий конфиг
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f) or {}

    # Обновляем пароли в конфиге простым присваиванием
    if 'auth' in config and isinstance(config['auth'], dict):
        config['auth']['password'] = passwords
    else:
        # если секции auth нет, создаём базовую
        config['auth'] = {'type': 'password', 'password': passwords}

    # Записываем обновленный конфиг — не сортировать ключи, чтобы сохранить порядок
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"Config updated: {len(passwords)} passwords")
    return True

def restart_hysteria():
    """Перезапуск Hysteria"""
    result = subprocess.run(
        ['systemctl', 'restart', 'hysteria-server'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("Hysteria restarted")
        return True
    else:
        print(f"Restart error: {result.stderr.strip()}")
        return False

def main():
    # Читаем пароли
    passwords = read_passwords()
    if not passwords:
        print("No passwords to update")
        sys.exit(1)

    print(f"Found {len(passwords)} passwords")

    if update_config(passwords):
        print("Complete to update config")
        if restart_hysteria():
            print("Config updated and hysteria restarted")
        else:
            print("Config updated but restart failed")
    else:
        print("Failed to update config")

if __name__ == "__main__":
    main()