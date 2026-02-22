#!/bin/bash
# =====================================================
# Скрипт для деплоя MapChap в Yandex Cloud
# =====================================================
# Выполняет все три шага:
# 1. Обновление API Gateway с новыми endpoints
# 2. Деплой фронтенда в Object Storage
# 3. Настройка Telegram Bot Webhook
# =====================================================

set -e

# Конфигурация
FOLDER_ID="b1gfh042gbr60ukjqqi0"
OAUTH_TOKEN="y0__xCsvOOMBxjB3RMglZzIzBUwzeSv9AfE-WbeKbZrpJEUOq6s_fxhlD-TEg"
TELEGRAM_BOT_TOKEN="8254063277:AAG9TklbhiLxUBbW2M2uq5aoyw7MA6RLnUQ"

# ID существующих ресурсов
API_GATEWAY_ID="d5djdb4t6ohnfrpfaaic"
FUNCTION_ID="d4ekri024dh40qmoh0m5"

# Для Object Storage
BUCKET_NAME="mapchap-frontend"
WEBSITE_ENDPOINT="${BUCKET_NAME}.website.yandexcloud.net"

# API Gateway URL
API_URL="https://${API_GATEWAY_ID}.apigw.yandexcloud.net"

echo "========================================"
echo "MapChap Yandex Cloud Deployment"
echo "========================================"
echo ""

# Проверка YC CLI
if ! command -v yc &> /dev/null; then
    echo "Installing Yandex Cloud CLI..."
    curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
    export PATH=$PATH:$HOME/yandex-cloud/bin
fi

# Авторизация
echo "=== Step 0: Authentication ==="
yc config set token $OAUTH_TOKEN
yc config set folder-id $FOLDER_ID
echo "✅ Authenticated with Yandex Cloud"
echo ""

# =====================================================
# ШАГ 1: Обновление API Gateway
# =====================================================
echo "=== Step 1: Updating API Gateway ==="
echo "Adding endpoints: verification, favorites, analytics, telegram webhook..."

yc serverless api-gateway update $API_GATEWAY_ID \
    --spec=/app/yandex-cloud-function/openapi.yaml \
    --folder-id=$FOLDER_ID

echo "✅ API Gateway updated with all endpoints"
echo "   URL: $API_URL"
echo ""

# =====================================================
# ШАГ 2: Деплой фронтенда в Object Storage
# =====================================================
echo "=== Step 2: Deploying Frontend to Object Storage ==="

# Создаём bucket если не существует
echo "Creating bucket: $BUCKET_NAME..."
yc storage bucket create \
    --name $BUCKET_NAME \
    --folder-id $FOLDER_ID \
    --default-storage-class standard \
    --max-size 1073741824 \
    2>/dev/null || echo "Bucket already exists or error creating"

# Настраиваем bucket как веб-сайт
echo "Configuring bucket as static website..."
yc storage bucket update $BUCKET_NAME \
    --website-settings='{"index": "index.html", "error": "index.html"}' \
    --folder-id $FOLDER_ID \
    2>/dev/null || echo "Website settings may already be configured"

# Делаем bucket публичным для чтения
echo "Setting bucket ACL to public-read..."
yc storage bucket update $BUCKET_NAME \
    --acl public-read \
    --folder-id $FOLDER_ID \
    2>/dev/null || echo "ACL may already be set"

echo "✅ Object Storage bucket configured"
echo "   Website URL: http://$WEBSITE_ENDPOINT"
echo ""

# Билд фронтенда
echo "Building frontend..."
cd /app/frontend

# Обновляем API URL на Yandex Cloud
echo "VITE_API_URL=$API_URL" > .env.production

yarn build

echo "✅ Frontend built successfully"
echo ""

# Загрузка файлов (используем s3cmd или aws cli)
echo "Uploading files to Object Storage..."

# Устанавливаем s3cmd если нет
if ! command -v s3cmd &> /dev/null; then
    pip install s3cmd -q
fi

# Получаем credentials для S3
echo "Getting S3 credentials..."

# Создаём service account для S3 если нет
SA_NAME="mapchap-s3-uploader"
SA_ID=$(yc iam service-account get $SA_NAME --folder-id $FOLDER_ID --format json 2>/dev/null | grep -o '"id": "[^"]*"' | head -1 | cut -d'"' -f4 || echo "")

if [ -z "$SA_ID" ]; then
    echo "Creating service account..."
    yc iam service-account create --name $SA_NAME --folder-id $FOLDER_ID
    SA_ID=$(yc iam service-account get $SA_NAME --folder-id $FOLDER_ID --format json | grep -o '"id": "[^"]*"' | head -1 | cut -d'"' -f4)
    
    # Назначаем роль storage.editor
    yc resource-manager folder add-access-binding $FOLDER_ID \
        --role storage.editor \
        --subject serviceAccount:$SA_ID
fi

# Создаём статический ключ
echo "Creating static access key..."
KEY_OUTPUT=$(yc iam access-key create --service-account-name $SA_NAME --folder-id $FOLDER_ID --format json 2>/dev/null || echo "")

if [ -n "$KEY_OUTPUT" ]; then
    ACCESS_KEY=$(echo $KEY_OUTPUT | grep -o '"key_id": "[^"]*"' | cut -d'"' -f4)
    SECRET_KEY=$(echo $KEY_OUTPUT | grep -o '"secret": "[^"]*"' | cut -d'"' -f4)
    
    # Конфигурируем s3cmd
    cat > ~/.s3cfg << EOF
[default]
access_key = $ACCESS_KEY
secret_key = $SECRET_KEY
host_base = storage.yandexcloud.net
host_bucket = %(bucket)s.storage.yandexcloud.net
use_https = True
EOF
    
    # Загружаем файлы
    echo "Uploading dist folder..."
    s3cmd sync --acl-public --no-mime-magic --guess-mime-type \
        /app/frontend/dist/ s3://$BUCKET_NAME/
    
    echo "✅ Frontend uploaded to Object Storage"
else
    echo "⚠️ Could not create access key. Manual upload required."
    echo "   Files are built in /app/frontend/dist/"
fi

echo ""

# =====================================================
# ШАГ 3: Настройка Telegram Bot Webhook
# =====================================================
echo "=== Step 3: Setting up Telegram Bot Webhook ==="

WEBHOOK_URL="${API_URL}/api/telegram/webhook"
echo "Setting webhook to: $WEBHOOK_URL"

WEBHOOK_RESULT=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"${WEBHOOK_URL}\"}")

echo "Response: $WEBHOOK_RESULT"

if echo "$WEBHOOK_RESULT" | grep -q '"ok":true'; then
    echo "✅ Telegram webhook configured successfully"
else
    echo "⚠️ Telegram webhook may have issues. Check the response above."
fi

echo ""

# =====================================================
# Итоги
# =====================================================
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""
echo "URLs:"
echo "  API Gateway: $API_URL"
echo "  Frontend:    http://$WEBSITE_ENDPOINT"
echo ""
echo "Available Endpoints:"
echo "  GET  /api/health"
echo "  GET  /api/db-test"
echo "  GET  /api/categories"
echo "  POST /api/auth/telegram"
echo "  POST /api/verification/inn"
echo "  POST /api/verification/manual"
echo "  GET  /api/users/{telegram_id}"
echo "  PUT  /api/users/{telegram_id}"
echo "  GET  /api/users/{telegram_id}/favorites"
echo "  PUT  /api/users/{telegram_id}/favorites"
echo "  GET  /api/offers"
echo "  POST /api/offers"
echo "  GET  /api/offers/{offer_id}"
echo "  PUT  /api/offers/{offer_id}"
echo "  DELETE /api/offers/{offer_id}"
echo "  GET  /api/offers/user/{telegram_id}"
echo "  POST /api/offers/{offer_id}/boost"
echo "  GET  /api/analytics/dashboard/{telegram_id}"
echo "  GET  /api/analytics/offer/{offer_id}"
echo "  GET  /api/boosts/plans"
echo "  GET  /api/articles"
echo "  POST /api/telegram/webhook"
echo ""
echo "Telegram Bot: @mapchap_bot"
echo "========================================"
