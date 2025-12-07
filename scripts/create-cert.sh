#!/bin/sh
set -eu

DOMAIN=${1:-api.yandex.ru}
CERT_DIR=/etc/hysteria/certs
KEY_FILE="$CERT_DIR/key.pem"
CERT_FILE="$CERT_DIR/cert.pem"

mkdir -p "$CERT_DIR"

# Create temporary openssl config
TMP_CONF=$(mktemp)
trap 'rm -f "$TMP_CONF"' EXIT

cat > "$TMP_CONF" <<EOF
[req]
distinguished_name = req_distinguished_name
prompt = no
x509_extensions = v3_req
req_extensions = v3_req

[req_distinguished_name]
C = RU
ST = Moscow
L = Moscow
O = YANDEX LLC
CN = $DOMAIN

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = www.$DOMAIN
EOF

# Generate key + self-signed cert
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout "$KEY_FILE" -out "$CERT_FILE" \
  -config "$TMP_CONF" -extensions v3_req

# Set safe permissions
chmod 640 "$KEY_FILE" 2>/dev/null || true
chmod 644 "$CERT_FILE" 2>/dev/null || true
chown root:root "$KEY_FILE" "$CERT_FILE" 2>/dev/null || true

echo "✅ Сертификат создан: $CERT_FILE"
echo "🔑 Приватный ключ: $KEY_FILE"
echo ""
echo "📋 Данные сертификата:"
openssl x509 -in "$CERT_FILE" -noout -subject -issuer -dates
echo ""
echo "⚠️  Это самоподписанный сертификат"
echo "📱 В клиентах используйте: insecure=1"