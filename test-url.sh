#!/bin/bash

# @todo Add real link
URLS=(
  "клик.раша.рф"
  "маил.раша.рф"
  "яндекс.раша.рф"
  "госуслуги.рф"
  "www.youtube.com"
)

echo "Проверяем какие сайты лучше маскироваться..."
for url in "${URLS[@]}"; do
  echo -n "Пинг $url: "
  ping -c 2 $url 2>/dev/null | grep "time=" | head -1 || echo "Нет ответа"
done

echo ""
echo "Проверка HTTPS доступности:"
for url in "${URLS[@]}"; do
  echo -n "HTTPS $url: "
  curl -sI https://$url --connect-timeout 3 | grep "HTTP" || echo "Недоступен"
done
