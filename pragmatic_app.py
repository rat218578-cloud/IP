# ========== pragmatic_app.py ==========
import requests
import json
import time
import os
import logging
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import urllib.parse

# ========== CONFIGURAÇÕES ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ========== TOKEN TURNSTILE ==========
CAPTCHA_TOKEN = "t2:1.ifdoY2ZRtYg8dM7vqQxdFVRqSeTJogrlF6EqbMrBWFzX9BC_mnw_vjuuhF8_bLUd1tViQrscFD9eTmSshUbuownZ4HOfKF7n61LxFjOsB7QRjk-4K-g67GfTShapvUPBIuoojAMxZzOvMDif2tj29uZsfaJEKuFdRnj6DgFcDiiKyY-HKNy-n0RfwoIs7VE6TzAISk-pMPpKXD6uHFKHR7gWxWNpsksMQLBeIkg7KvgXzTcHUt8VnVEpSsugGkNMV_1AeEN43O9eH91WU2Vef_3iyie6KPgimWq1ly82r1BSvBSs0lt5FgF7LYfzWSkeO3ApOYjWgnQXFYDntAMIioM_MDxGdD48JDNWvpoua3PRsq3Gpoj5BdlJ2qlguGl3NWOUAAYeOL0UMgiB0G9QmpLwFn7SWyoM2GvSDuyqGLMx4B9pJ6ntW0qrXVk2cd5Rm-6eoAVCfbIUoPVtt9nGY_nS7yNTMQg5uOZggTgI8D2ar9aKdFDBD9qtbY3gHQW0Sy3d7iMkalbbLeeIq4oLsqwtGYJgJzsbIR61J1mWA1L34Hosv_qAz4e6bFovRn3efFejTbZmP4eD7zVaacfdufZY9fAC2K5wEXTR7rwVqlGknlwi9-3r9JgwrKpL3tZmRmzwNK5aEpS2DWqNrDt-lv4fsnLJYb7XmfCoYGd7EBMgnvREpViF2HFonRMeP7qmtQnocHJ71gUEMbXtwMIzdQ.ODr74DV1RP4y9w1JfkgYWA.a6b915441ca8df4a77de54d936420e701d16f894798dd9dd54650ddfead9a042"

# ========== SESSÃO ==========
session = requests.Session()
session.headers.update({
    'Content-Type': 'application/json',
    'Origin': 'https://sortenabet.bet.br',
    'Referer': 'https://sortenabet.bet.br/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
})

# ========== LOGIN ==========
def fazer_login():
    """Faz login e retorna access token."""
    logger.info("🔐 FAZENDO LOGIN...")
    
    login_data = {
        "login": "gcriste268@gmail.com",
        "email": "gcriste268@gmail.com",
        "password": "284050",
        "app_source": "web",
        "captcha_token": CAPTCHA_TOKEN
    }

    try:
        response = session.post('https://sortenabet.bet.br/api/auth/login', json=login_data)
        
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            session.headers.update({'Authorization': f'Bearer {access_token}'})
            logger.info("✅ Login OK!")
            return True
        else:
            logger.error(f"❌ Login falhou: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return False

# ========== BUSCAR JOGOS ==========
def buscar_jogos_pragmatic():
    """Busca jogos da Pragmatic Play."""
    logger.info("🎮 BUSCANDO JOGOS DA PRAGMATIC PLAY...")
    
    jogos_pragmatic = [
        'pragmaticplay/mega-roleta',
        'pragmaticplay/gates-of-olympus',
        'pragmaticplay/sweet-bonanza',
        'pragmaticplay/the-dog-house',
        'pragmaticplay/big-bass-splash',
        'pragmaticplay/zeus-vs-hades',
        'pragmaticplay/wolf-gold'
    ]

    urls_pragmatic = []

    for slug in jogos_pragmatic:
        try:
            response = session.get(
                'https://sortenabet.bet.br/api/start-game-v2',
                params={
                    'slug': slug,
                    'platform': 'WEB',
                    'use_demo': 0,
                    'source': 'watchIsAuthenticated'
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                game_url = data.get('iframe_url') or data.get('gameURL')

                if game_url:
                    urls_pragmatic.append({
                        'slug': slug,
                        'nome': slug.split('/')[-1].replace('-', ' ').title(),
                        'url': game_url
                    })
                    logger.info(f"   ✅ {slug}")
                else:
                    logger.warning(f"   ⚠️ {slug} - sem URL")
            else:
                logger.warning(f"   ❌ {slug}: HTTP {response.status_code}")

            time.sleep(0.3)

        except Exception as e:
            logger.error(f"   ❌ {slug}: erro - {str(e)[:40]}")

    return urls_pragmatic

# ========== HTML DO IFRAME ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎰 Pragmatic Play - Mega Roleta Imersiva</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
        }
        .header {
            background: rgba(0,0,0,0.9);
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #e94560;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; color: white; }
        .header h1 span { color: #e94560; }
        .header p { color: #ccc; }
        .container { max-width: 1400px; margin: 20px auto; padding: 0 20px; }
        .jogo-selector {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .jogo-selector h3 { color: white; margin-bottom: 10px; }
        .jogos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }
        .jogo-btn {
            background: rgba(255,255,255,0.1);
            border: none;
            color: white;
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }
        .jogo-btn:hover { background: #e94560; transform: translateY(-2px); }
        .jogo-btn.active { background: #e94560; border: 2px solid white; }
        .game-panel {
            background: #0f0f1a;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .game-header {
            background: #1a1a2e;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e94560;
        }
        .game-title { font-size: 1.2em; font-weight: bold; color: white; }
        .game-status {
            padding: 5px 15px;
            border-radius: 20px;
            background: #27ae60;
            font-size: 0.8em;
            color: white;
        }
        .iframe-container {
            position: relative;
            width: 100%;
            height: 75vh;
            background: #000;
        }
        iframe { width: 100%; height: 100%; border: none; }
        .info {
            background: rgba(0,0,0,0.7);
            padding: 10px;
            margin-top: 10px;
            border-radius: 8px;
            text-align: center;
            color: #ccc;
            font-size: 12px;
        }
        .error-msg {
            color: #e94560;
            text-align: center;
            padding: 50px;
            font-size: 1.5em;
        }
        @media (max-width: 768px) {
            .iframe-container { height: 50vh; }
            .header h1 { font-size: 1.2em; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎰 <span>PRAGMATIC PLAY</span> | Mega Roleta Imersiva</h1>
        <p>Jogos ao vivo com dealer real • Roleta • Slots • Crash Games</p>
    </div>

    <div class="container">
        {% if urls %}
        <div class="jogo-selector">
            <h3>🎮 Selecione o jogo:</h3>
            <div class="jogos-grid">
                {% for jogo in urls %}
                <button class="jogo-btn" onclick="carregarJogo('{{ jogo.url }}', '{{ jogo.nome }}')">🎰 {{ jogo.nome }}</button>
                {% endfor %}
            </div>
        </div>

        <div class="game-panel">
            <div class="game-header">
                <span class="game-title" id="gameTitle">{{ urls[0].nome if urls else 'Nenhum jogo' }}</span>
                <span class="game-status" id="gameStatus">🟢 Conectado</span>
            </div>
            <div class="iframe-container">
                <iframe id="gameFrame" src="{{ urls[0].url if urls else '' }}" allow="autoplay; fullscreen; camera; microphone"></iframe>
            </div>
        </div>

        <div class="info">
            💡 Dica: Os jogos da Pragmatic Play carregam diretamente no seu navegador.
            Certifique-se de estar logado na Sorte na Bet para uma experiência completa.
        </div>
        {% else %}
        <div class="error-msg">
            ❌ Nenhum jogo da Pragmatic Play encontrado.<br>
            <small style="font-size: 0.6em;">Verifique se você está logado e tente novamente.</small>
        </div>
        {% endif %}
    </div>

    <script>
        function carregarJogo(url, nome) {
            const gameFrame = document.getElementById('gameFrame');
            const gameTitle = document.getElementById('gameTitle');
            const gameStatus = document.getElementById('gameStatus');

            gameStatus.textContent = '🟡 Carregando...';
            gameStatus.style.background = '#f39c12';
            gameTitle.textContent = nome;

            setTimeout(() => {
                gameFrame.src = url;
                gameStatus.textContent = '🟢 Conectado';
                gameStatus.style.background = '#27ae60';
            }, 100);

            document.querySelector('.game-panel').scrollIntoView({ behavior: 'smooth' });

            document.querySelectorAll('.jogo-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.includes(nome)) {
                    btn.classList.add('active');
                }
            });
        }

        console.log('🎮 Pragmatic Play carregada!');
        console.log('Jogos disponíveis:', {{ urls|length if urls else 0 }});
    </script>
</body>
</html>
"""

# ========== ROTAS ==========
@app.route('/')
def index():
    """Página principal com os jogos."""
    # Faz login se necessário
    if not fazer_login():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>Erro</title></head>
        <body style="background:#1a1a2e;color:white;text-align:center;padding:50px;">
            <h1>❌ Erro ao fazer login</h1>
            <p>Verifique suas credenciais e tente novamente.</p>
        </body>
        </html>
        """), 401
    
    # Busca jogos
    urls = buscar_jogos_pragmatic()
    
    return render_template_string(HTML_TEMPLATE, urls=urls)

@app.route('/api/jogos', methods=['GET'])
def api_jogos():
    """Retorna lista de jogos em JSON."""
    if not fazer_login():
        return jsonify({'success': False, 'error': 'Login falhou'}), 401
    
    urls = buscar_jogos_pragmatic()
    return jsonify({
        'success': True,
        'total': len(urls),
        'jogos': urls
    })

@app.route('/api/jogar/<slug>', methods=['GET'])
def api_jogar(slug):
    """Retorna URL de um jogo específico."""
    if not fazer_login():
        return jsonify({'success': False, 'error': 'Login falhou'}), 401
    
    try:
        response = session.get(
            'https://sortenabet.bet.br/api/start-game-v2',
            params={
                'slug': slug,
                'platform': 'WEB',
                'use_demo': 0,
                'source': 'watchIsAuthenticated'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            game_url = data.get('iframe_url') or data.get('gameURL')
            return jsonify({
                'success': True,
                'slug': slug,
                'url': game_url
            })
        else:
            return jsonify({'success': False, 'error': f'HTTP {response.status_code}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time()
    })

# ========== MAIN ==========
if __name__ == '__main__':
    print("=" * 60)
    print("🎯 PRAGMATIC PLAY - RAILWAY")
    print("=" * 60)
    print("🌐 Acesse: http://localhost:5000")
    print("=" * 60)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
