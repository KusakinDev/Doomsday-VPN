#!/usr/bin/env python3
import secrets
import string

chars = string.ascii_letters + string.digits + "+/="
password = ''.join(secrets.choice(chars) for _ in range(32))

# # prod
# with open('/etc/hysteria/users.txt', 'a') as f:
#     f.write(password + '\n')

# # local
# with open('./users.txt', 'a') as f:
#     f.write(password + '\n')


# Вывод результата
password = "algFNdE82VhJulMxov+JMdg5"
password2 = "Zpov2bBbv7h916kp2/z2Cw=="
print(f"hy2://{password}@senator.giize.com:443?sni=www.github.com#MasqueradeVPN")
print("----")
print(f"hy2://{password}@senator.giize.com:443?obfs-password={password2}#ObfsVPN")