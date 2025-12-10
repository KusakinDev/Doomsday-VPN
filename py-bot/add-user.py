#!/usr/bin/env python3
import secrets
import string

chars = string.ascii_letters + string.digits + "+/="
password = ''.join(secrets.choice(chars) for _ in range(32))

# prod
with open('/etc/hysteria/users.txt', 'a') as f:
    f.write(password + '\n')

# # local
# with open('./users.txt', 'a') as f:
#     f.write(password + '\n')


# Вывод результата
print(f"Password: {password}")
print(f"Link: hy2://{password}@senator.giize.com:443#User")