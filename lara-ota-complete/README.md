# 🚀 LARA OTA Installer

Автоматическая установка LARA без компьютера и без настоящего Developer аккаунта.

## 📱 Как установить LARA (БЕЗ Developer аккаунта)

### Открой в Safari на iPhone:
**https://liver-vintage-marco-thus.trycloudflare.com**

### Выбери способ установки:

#### 🔴 Через Scarlet (Рекомендуется)
1. Установи Scarlet: https://usescarlet.com
2. Нажми "Установить через Scarlet"
3. Scarlet автоматически подпишет и установит LARA

#### 🛒 Через TrollStore
1. Если у тебя уже установлен TrollStore
2. Нажми "Установить через TrollStore"
3. LARA установится навсегда без подписи

#### ✍️ Через ESign
1. Установи ESign: https://esign.yyyue.xyz
2. Нажми "Установить через ESign"
3. ESign подпишет с твоим сертификатом

#### 📥 Прямая загрузка
1. Нажми "Скачать IPA напрямую"
2. Установи через AltStore/Sideloadly (требуется компьютер)

## 🔗 Прямые ссылки

- **Web Installer**: https://liver-vintage-marco-thus.trycloudflare.com
- **Прямая ссылка на IPA**: https://github.com/rooootdev/lara/releases/latest/download/lara.ipa
- **Scarlet URL**: `scarlet://install=https://github.com/rooootdev/lara/releases/latest/download/lara.ipa`
- **TrollStore URL**: `apple-magnifier://install?url=https://github.com/rooootdev/lara/releases/latest/download/lara.ipa`
- **ESign URL**: `esign://import?url=https://github.com/rooootdev/lara/releases/latest/download/lara.ipa`

## ✨ Что умеет LARA

- ✅ Установка TrollStore на iOS 17.0 - 17.6.1
- ✅ Поддержка iPhone X и новее (A11+)
- ✅ DarkSword exploit (IOSurface race condition)
- ✅ AMFI bypass для A12+ устройств
- ✅ installd patching для постоянной установки
- ✅ Полное логирование процесса

## 📋 Поддерживаемые устройства

- iPhone X и новее
- iOS 17.0 - 17.6.1
- Протестировано на iPhone 11 Pro (iOS 17.6.1)

## 🛠️ Технические детали

### Архитектура OTA сервера
- **Сервер**: Oracle Cloud Free Tier (79.72.18.198)
- **Туннель**: Cloudflare Tunnel (HTTPS)
- **Backend**: Flask + Gunicorn
- **Автозапуск**: systemd service

### URL Schemes
- `scarlet://install={url}` - Scarlet
- `apple-magnifier://install?url={url}` - TrollStore
- `esign://import?url={url}` - ESign

## 🔧 Деплой на свой сервер

### Автоматический деплой
```bash
cd lara-ota-complete
chmod +x deploy-webclip.sh
./deploy-webclip.sh
```

### Ручной деплой
См. [MANUAL_DEPLOY.md](MANUAL_DEPLOY.md)

## 📊 Статус сервисов

Проверить статус:
```bash
# На сервере
sudo systemctl status lara-ota
sudo systemctl status cloudflared

# Логи
sudo journalctl -u lara-ota -f
sudo journalctl -u cloudflared -f
```

## 🐛 Решенные проблемы

1. ✅ Kernel panic на A13 - AMFI bypass возвращает success на PPL
2. ✅ RemoteCall не работал - исправлена инициализация
3. ✅ installd patches не применялись - исправлена запись в память
4. ✅ GitHub Actions permissions - добавлен `contents: write`
5. ✅ OTA без Developer аккаунта - используем URL schemes

## 📝 Changelog

### 2026-05-04
- ✅ Создан webclip-installer.py с URL schemes
- ✅ Добавлена поддержка Scarlet/TrollStore/ESign
- ✅ Убрана зависимость от Apple Developer сертификата
- ✅ Cloudflare Tunnel настроен и работает

### 2026-05-03
- ✅ Настроен Oracle Cloud сервер
- ✅ Настроен Cloudflare Tunnel
- ✅ Создан auto-signer.py

### 2026-05-02
- ✅ Исправлен AMFI bypass для PPL устройств
- ✅ Исправлен installd patching
- ✅ Добавлены GitHub Releases

## 🔒 Безопасность

- Сервер не хранит данные пользователей
- IPA скачивается напрямую с GitHub
- URL schemes открывают установленные приложения
- Нет передачи Apple ID на сервер

## 📞 Поддержка

- GitHub Issues: https://github.com/rooootdev/lara/issues
- GitHub Repo: https://github.com/rooootdev/lara

## ⚖️ Лицензия

Этот проект создан для исследования безопасности iOS.
Используй только на своих устройствах с юридическим разрешением.
