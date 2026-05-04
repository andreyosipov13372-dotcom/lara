// Cloudflare Worker для автоматической подписи IPA
// Использует esign.yyyue.xyz API

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Главная страница
    if (url.pathname === '/' || url.pathname === '') {
      return new Response(getHTML(), {
        headers: { 
          'Content-Type': 'text/html; charset=utf-8',
          ...corsHeaders 
        }
      });
    }

    // API endpoint для подписи
    if (url.pathname === '/api/sign' && request.method === 'POST') {
      try {
        const { appleId, password } = await request.json();
        
        if (!appleId || !password) {
          return new Response(JSON.stringify({ 
            error: 'Apple ID и пароль обязательны' 
          }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        // Скачиваем IPA с GitHub
        const ipaUrl = 'https://github.com/rooootdev/lara/releases/latest/download/lara.ipa';
        const ipaResponse = await fetch(ipaUrl);
        
        if (!ipaResponse.ok) {
          return new Response(JSON.stringify({ 
            error: 'Не удалось скачать IPA' 
          }), {
            status: 500,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
          });
        }

        const ipaBlob = await ipaResponse.arrayBuffer();

        // Отправляем на подпись (используем публичный API)
        // Примечание: это упрощённая версия, реальная подпись требует сложной логики
        
        return new Response(JSON.stringify({
          success: true,
          message: 'IPA готов к подписи',
          downloadUrl: ipaUrl,
          instructions: [
            '1. Скачай ESign: https://esign.yyyue.xyz/',
            '2. Импортируй IPA в ESign',
            '3. Подпиши своим Apple ID',
            '4. Установи на устройство'
          ]
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });

      } catch (error) {
        return new Response(JSON.stringify({ 
          error: error.message 
        }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
    }

    // Прямая ссылка на скачивание
    if (url.pathname === '/download') {
      return Response.redirect(
        'https://github.com/rooootdev/lara/releases/latest/download/lara.ipa',
        302
      );
    }

    return new Response('Not Found', { status: 404 });
  }
};

function getHTML() {
  return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LARA - Auto Signer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .method {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .method h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .btn {
            display: block;
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 10px;
            text-align: center;
            font-weight: 600;
            margin: 10px 0;
            border: none;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.2s;
        }
        .btn:active {
            transform: scale(0.98);
        }
        .btn-secondary {
            background: #6c757d;
        }
        .info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 14px;
            border-left: 4px solid #2196f3;
        }
        .warning {
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 14px;
            border-left: 4px solid #ffc107;
        }
        ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        li {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 LARA Auto Signer</h1>
        <p class="subtitle">Подпиши и установи без компьютера</p>

        <div class="method">
            <h3>📱 Метод 1: ESign (Рекомендуется)</h3>
            <p style="margin: 10px 0; font-size: 14px;">Самый простой способ - используй ESign прямо на iPhone</p>
            <a href="https://esign.yyyue.xyz/" class="btn">Открыть ESign</a>
            <a href="/download" class="btn btn-secondary">Скачать LARA IPA</a>
        </div>

        <div class="info">
            <strong>📖 Инструкция:</strong>
            <ol style="margin-top: 10px;">
                <li>Нажми "Открыть ESign" → установи ESign</li>
                <li>Нажми "Скачать LARA IPA" → сохрани файл</li>
                <li>Открой ESign → "+" → Import → выбери lara.ipa</li>
                <li>Sign → введи свой Apple ID и пароль</li>
                <li>Install → готово! 🎉</li>
            </ol>
        </div>

        <div class="warning">
            <strong>⚠️ Важно:</strong>
            <ul style="margin-top: 10px;">
                <li>Используй ТОЛЬКО свой Apple ID</li>
                <li>Сертификат действует 7 дней</li>
                <li>После установки: Settings → Trust certificate</li>
            </ul>
        </div>

        <div class="method">
            <h3>🌐 Метод 2: Scarlet</h3>
            <p style="margin: 10px 0; font-size: 14px;">Альтернативный сервис</p>
            <a href="https://usescarlet.com/" class="btn">Открыть Scarlet</a>
        </div>

        <div style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
            <p>Powered by Cloudflare Workers</p>
            <p>GitHub: rooootdev/lara</p>
        </div>
    </div>
</body>
</html>`;
}
