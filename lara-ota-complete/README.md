# LARA OTA Server - Полный готовый сервер

Полностью автоматизированный OTA сервер для подписи и установки LARA через Safari.

## 🚀 Быстрый запуск (одна команда)

```bash
cd lara-ota-complete
chmod +x upload.sh
./upload.sh
```

Скрипт автоматически:
- ✅ Подключится к Oracle Cloud серверу
- ✅ Загрузит все файлы
- ✅ Установит все зависимости (Python, nginx, zsign, Cloudflare Tunnel)
- ✅ Настроит systemd сервис
- ✅ Запустит сервер

## 📋 Что делать после деплоя

### 1. Загрузить сертификат Apple ID

```bash
# Замени пути на свои файлы
scp -i "/home/orkenlk/Загрузки/ssh-key-2026-04-29 (1).key" \
    cert.p12 ubuntu@79.72.18.198:/opt/lara-ota/certs/

scp -i "/home/orkenlk/Загрузки/ssh-key-2026-04-29 (1).key" \
    profile.mobileprovision ubuntu@79.72.18.198:/opt/lara-ota/certs/
```

**Как получить cert.p12 и profile.mobileprovision:**
- Открой Xcode → Preferences → Accounts
- Выбери свой Apple ID → Manage Certificates
- Экспортируй сертификат как .p12
- Скачай provisioning profile с developer.apple.com

### 2. Настроить Cloudflare Tunnel

```bash
# Подключись к серверу
ssh -i "/home/orkenlk/Загрузки/ssh-key-2026-04-29 (1).key" ubuntu@79.72.18.198

# Залогинься в Cloudflare (откроется браузер)
cloudflared tunnel login

# Создай туннель
cloudflared tunnel create lara-ota

# Настрой DNS (замени на свой домен)
cloudflared tunnel route dns lara-ota lara.yourdomain.com

# Создай конфиг
sudo mkdir -p /etc/cloudflared
sudo nano /etc/cloudflared/config.yml
```

**Содержимое config.yml:**
```yaml
tunnel: <TUNNEL-ID из вывода команды create>
credentials-file: /root/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: lara.yourdomain.com
    service: http://localhost:80
  - service: http_status:404
```

**Запусти туннель:**
```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### 3. Проверить работу

```bash
# Статус сервера
sudo systemctl status lara-ota

# Логи в реальном времени
sudo journalctl -u lara-ota -f

# Проверка здоровья
curl http://localhost/health

# Статус туннеля
sudo systemctl status cloudflared
```

## 🌐 Использование

После настройки:

1. Открой в Safari на iPhone: `https://lara.yourdomain.com`
2. Нажми **"Подписать и скачать IPA"**
3. Дождись подписи (~30 секунд)
4. Нажми **"Установить через OTA"**
5. Подтверди установку в iOS

## 📁 Структура файлов

```
lara-ota-complete/
├── server.py           # Flask сервер с веб-интерфейсом
├── deploy.sh          # Скрипт установки на сервер
├── upload.sh          # Автоматическая загрузка и деплой
├── requirements.txt   # Python зависимости
└── README.md         # Эта инструкция
```

## 🔧 Что установлено на сервере

- **Python 3** + Flask + Gunicorn
- **nginx** - reverse proxy
- **zsign** - подпись IPA
- **Cloudflare Tunnel** - HTTPS без сертификатов
- **systemd service** - автозапуск

## 📊 Полезные команды

```bash
# Подключиться к серверу
ssh -i "/home/orkenlk/Загрузки/ssh-key-2026-04-29 (1).key" ubuntu@79.72.18.198

# Перезапустить сервер
sudo systemctl restart lara-ota

# Посмотреть логи
sudo journalctl -u lara-ota -n 100

# Проверить nginx
sudo systemctl status nginx
sudo nginx -t

# Проверить Cloudflare Tunnel
sudo systemctl status cloudflared
cloudflared tunnel list
```

## 🔐 Безопасность

- Сертификаты хранятся в `/opt/lara-ota/certs/` (только владелец)
- HTTPS через Cloudflare Tunnel
- nginx как reverse proxy
- Подписанные IPA автоматически перезаписываются
- Логи не содержат credentials

## 🐛 Решение проблем

**Сервер не запускается:**
```bash
sudo journalctl -u lara-ota -n 50
```

**Ошибка подписи:**
```bash
# Проверь наличие сертификатов
ls -la /opt/lara-ota/certs/

# Проверь zsign
zsign --version
```

**Cloudflare Tunnel не работает:**
```bash
sudo journalctl -u cloudflared -n 50
cloudflared tunnel list
```

**nginx ошибки:**
```bash
sudo nginx -t
sudo systemctl status nginx
```

## 📱 Поддержка

- iOS 17.0 - 17.6.1
- iPhone X и новее
- Подпись действует 7 дней
- После истечения - переподписать через сайт

## 🎯 Как это работает

1. **Пользователь открывает сайт** → Flask отдает HTML
2. **Нажимает "Подписать"** → Сервер скачивает IPA из GitHub
3. **zsign подписывает** → С твоим Apple ID сертификатом
4. **Генерируется manifest.plist** → Для iOS OTA
5. **iOS устанавливает** → Через itms-services://

## 🔄 Обновление сервера

```bash
cd lara-ota-complete
# Измени server.py если нужно
./upload.sh
ssh -i "/home/orkenlk/Загрузки/ssh-key-2026-04-29 (1).key" ubuntu@79.72.18.198
sudo systemctl restart lara-ota
```

## 💡 Советы

- Используй бесплатный домен от Cloudflare
- Сертификат можно экспортировать из Keychain Access
- Provisioning profile скачивается с developer.apple.com
- Логи сохраняются в `/opt/lara-ota/logs/`
- Можно использовать бесплатный Apple Developer аккаунт

---

**Готово к использованию! Просто запусти `./upload.sh` и следуй инструкциям.**
