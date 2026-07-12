# ========== pragmatic_app.py ==========
import requests
import json
import time
import os
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from threading import Lock
from datetime import datetime, timedelta

# ========== CONFIGURAÇÕES ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ========== CACHE ==========
cache_jogos = {}
cache_lock = Lock()
ultimo_login = None
TOKEN_EXPIRATION = timedelta(minutes=5)  # Token expira em 5 minutos

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

# ========== LISTA COMPLETA DE JOGOS ==========
JOGOS_DISPONIVEIS = {
    'spribe': [
        {'slug': 'spribe/aviator', 'nome': '✈️ Aviator'},
    ],
    'evolution': [
        {'slug': 'evolution/football-studio-dice', 'nome': '⚽ Football Studio Dice'},
        {'slug': 'evolution/football-studio', 'nome': '⚽ Football Studio'},
        {'slug': 'evolution/crazy-time', 'nome': '🎡 Crazy Time'},
        {'slug': 'evolution/monopoly-live', 'nome': '🏠 Monopoly Live'},
        {'slug': 'evolution/lightning-roulette', 'nome': '⚡ Lightning Roulette'},
        {'slug': 'evolution/dream-catcher', 'nome': '🎯 Dream Catcher'},
        {'slug': 'evolution/super-andar-bahar', 'nome': '🃏 Super Andar Bahar'},
        {'slug': 'evolution/blackjack-live', 'nome': '♠️ Blackjack Live'},
        {'slug': 'evolution/roulette-live', 'nome': '🎰 Roulette Live'},
        {'slug': 'evolution/baccarat-live', 'nome': '🃏 Baccarat Live'},
    ],
    'pragmaticplay': [
        {'slug': 'pragmaticplay/mega-roleta', 'nome': '🎰 Mega Roleta'},
        {'slug': 'pragmaticplay/gates-of-olympus', 'nome': '🏛️ Gates of Olympus'},
        {'slug': 'pragmaticplay/sweet-bonanza', 'nome': '🍬 Sweet Bonanza'},
        {'slug': 'pragmaticplay/the-dog-house', 'nome': '🐕 The Dog House'},
        {'slug': 'pragmaticplay/big-bass-splash', 'nome': '🐟 Big Bass Splash'},
        {'slug': 'pragmaticplay/wolf-gold', 'nome': '🐺 Wolf Gold'},
        {'slug': 'pragmaticplay/starlight-princess', 'nome': '👸 Starlight Princess'},
    ],
    'pgsoft': [
        {'slug': 'pgsoft/fortune-tiger', 'nome': '🐯 Fortune Tiger'},
        {'slug': 'pgsoft/fortune-ox', 'nome': '🐂 Fortune Ox'},
        {'slug': 'pgsoft/fortune-rabbit', 'nome': '🐰 Fortune Rabbit'},
    ],
    'hacksaw': [
        {'slug': 'hacksaw/sixsixsix', 'nome': '🔥 SixSixSix'},
        {'slug': 'hacksaw/chaos-crew', 'nome': '💥 Chaos Crew'},
    ],
    'netent': [
        {'slug': 'netent/starburst', 'nome': '💫 Starburst'},
    ]
}

# ========== CORES POR PROVEDOR ==========
CORES_PROVEDOR = {
    'spribe': '#FF6B35',
    'evolution': '#6C3CE1',
    'pragmaticplay': '#E94560',
    'pgsoft': '#00B894',
    'hacksaw': '#FD79A8',
    'netent': '#0984E3'
}

# ========== FUNÇÕES DE AUTENTICAÇÃO ==========
def fazer_login():
    """Faz login e retorna access token."""
    global ultimo_login
    
    # Verifica se o login já foi feito recentemente
    if ultimo_login and datetime.now() - ultimo_login < TOKEN_EXPIRATION:
        logger.info("✅ Login ainda válido")
        return True
    
    logger.info("🔐 FAZENDO LOGIN...")
    
    login_data = {
        "login": "gcriste268@gmail.com",
        "email": "gcriste268@gmail.com",
        "password": "284050",
        "app_source": "web",
        "captcha_token": CAPTCHA_TOKEN
    }

    try:
        response = session.post('https://sortenabet.bet.br/api/auth/login', json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            session.headers.update({'Authorization': f'Bearer {access_token}'})
            ultimo_login = datetime.now()
            logger.info("✅ Login OK!")
            return True
        else:
            logger.error(f"❌ Login falhou: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return False

def obter_url_jogo(slug):
    """Obtém a URL de um jogo específico com cache."""
    global cache_jogos
    
    # Verifica cache
    with cache_lock:
        if slug in cache_jogos:
            # Verifica se o cache ainda é válido (5 minutos)
            if datetime.now() - cache_jogos[slug]['timestamp'] < TOKEN_EXPIRATION:
                logger.info(f"📦 Cache hit para {slug}")
                return cache_jogos[slug]['url']
    
    # Se não está no cache ou expirou, busca novamente
    try:
        # Garante que está logado
        if not fazer_login():
            logger.error(f"❌ Não foi possível fazer login para {slug}")
            return None
        
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
                # Guarda no cache
                with cache_lock:
                    cache_jogos[slug] = {
                        'url': game_url,
                        'timestamp': datetime.now()
                    }
                logger.info(f"✅ URL obtida para {slug}")
                return game_url
            else:
                logger.warning(f"⚠️ Sem URL para {slug}")
                return None
        else:
            logger.warning(f"❌ {slug}: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar {slug}: {e}")
        return None

# ========== BUSCAR JOGOS ==========
def buscar_jogos(force_refresh=False):
    """Busca todos os jogos disponíveis."""
    global cache_jogos
    
    logger.info("🎮 BUSCANDO TODOS OS JOGOS...")
    
    # Se force_refresh, limpa cache
    if force_refresh:
        with cache_lock:
            cache_jogos.clear()
    
    jogos_encontrados = []
    
    for provedor, jogos in JOGOS_DISPONIVEIS.items():
        for jogo in jogos:
            url = obter_url_jogo(jogo['slug'])
            
            if url:
                jogos_encontrados.append({
                    'slug': jogo['slug'],
                    'nome': jogo['nome'],
                    'provedor': provedor,
                    'cor': CORES_PROVEDOR.get(provedor, '#FFFFFF'),
                    'url': url
                })
                logger.info(f"   ✅ {jogo['slug']}")
            else:
                logger.warning(f"   ❌ {jogo['slug']} - falhou")

            time.sleep(0.1)  # Pequena pausa para não sobrecarregar

    logger.info(f"✅ Total de jogos encontrados: {len(jogos_encontrados)}")
    return jogos_encontrados

# ========== HTML DO IFRAME ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎰 Sorte na Bet - Todos os Jogos</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a1a;
            min-height: 100vh;
            color: white;
        }
        
        .header {
            background: linear-gradient(135deg, #1a1a2e, #2d1b4e);
            padding: 25px 20px;
            text-align: center;
            border-bottom: 3px solid #e94560;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        .header h1 { 
            font-size: 2.2em; 
            margin-bottom: 5px;
            background: linear-gradient(135deg, #e94560, #f39c12);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header p { color: #aaa; font-size: 0.95em; }
        .header .stats {
            margin-top: 8px;
            color: #666;
            font-size: 0.85em;
        }
        .header .stats span { color: #e94560; font-weight: bold; }

        .filtros {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            position: sticky;
            top: 105px;
            z-index: 99;
            backdrop-filter: blur(10px);
        }
        .filtro-btn {
            padding: 8px 18px;
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 25px;
            background: transparent;
            color: #aaa;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.85em;
        }
        .filtro-btn:hover {
            border-color: #e94560;
            color: white;
        }
        .filtro-btn.active {
            background: #e94560;
            border-color: #e94560;
            color: white;
        }
        .filtro-btn[data-provedor="spribe"]:hover { border-color: #FF6B35; }
        .filtro-btn[data-provedor="spribe"].active { background: #FF6B35; border-color: #FF6B35; }
        .filtro-btn[data-provedor="evolution"]:hover { border-color: #6C3CE1; }
        .filtro-btn[data-provedor="evolution"].active { background: #6C3CE1; border-color: #6C3CE1; }
        .filtro-btn[data-provedor="pragmaticplay"]:hover { border-color: #E94560; }
        .filtro-btn[data-provedor="pragmaticplay"].active { background: #E94560; border-color: #E94560; }
        .filtro-btn[data-provedor="pgsoft"]:hover { border-color: #00B894; }
        .filtro-btn[data-provedor="pgsoft"].active { background: #00B894; border-color: #00B894; }
        .filtro-btn[data-provedor="hacksaw"]:hover { border-color: #FD79A8; }
        .filtro-btn[data-provedor="hacksaw"].active { background: #FD79A8; border-color: #FD79A8; }
        .filtro-btn[data-provedor="netent"]:hover { border-color: #0984E3; }
        .filtro-btn[data-provedor="netent"].active { background: #0984E3; border-color: #0984E3; }

        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }

        .jogos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        .jogo-card {
            background: rgba(255,255,255,0.05);
            border: 2px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 12px 15px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .jogo-card:hover {
            transform: translateY(-3px);
            border-color: rgba(255,255,255,0.3);
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        }
        .jogo-card.active {
            border-color: #e94560;
            background: rgba(233, 69, 96, 0.15);
        }
        .jogo-card .provedor-tag {
            position: absolute;
            top: 5px;
            right: 5px;
            font-size: 0.6em;
            padding: 2px 8px;
            border-radius: 10px;
            background: rgba(0,0,0,0.6);
            color: #aaa;
        }
        .jogo-card .jogo-nome {
            font-size: 0.95em;
            font-weight: 500;
            margin-top: 3px;
        }
        .jogo-card .jogo-emoji {
            font-size: 1.8em;
            display: block;
            margin-bottom: 3px;
        }
        .jogo-card .cor-bar {
            height: 3px;
            width: 100%;
            position: absolute;
            bottom: 0;
            left: 0;
            border-radius: 0 0 12px 12px;
        }

        .game-panel {
            background: #0f0f1a;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.05);
        }
        .game-header {
            background: rgba(0,0,0,0.8);
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            flex-wrap: wrap;
            gap: 10px;
        }
        .game-title { 
            font-size: 1.1em; 
            font-weight: bold; 
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .game-title .provedor-badge {
            font-size: 0.6em;
            padding: 2px 12px;
            border-radius: 12px;
            background: rgba(255,255,255,0.1);
            color: #aaa;
        }
        .game-status {
            padding: 4px 15px;
            border-radius: 20px;
            font-size: 0.75em;
            color: white;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .game-status .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .game-status.online .dot { background: #27ae60; }
        .game-status.loading .dot { background: #f39c12; animation: pulse 0.8s infinite; }
        .game-status.error .dot { background: #e94560; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .iframe-container {
            position: relative;
            width: 100%;
            height: 70vh;
            background: #000;
        }
        iframe { width: 100%; height: 100%; border: none; }

        .info {
            background: rgba(0,0,0,0.5);
            padding: 12px;
            margin-top: 10px;
            border-radius: 8px;
            text-align: center;
            color: #666;
            font-size: 0.8em;
        }
        .info a { color: #e94560; text-decoration: none; }
        .info a:hover { text-decoration: underline; }

        .error-msg {
            color: #e94560;
            text-align: center;
            padding: 50px;
            font-size: 1.5em;
        }

        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 999;
            flex-direction: column;
            gap: 20px;
        }
        .loading-overlay.active { display: flex; }
        .loading-overlay .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255,255,255,0.1);
            border-top-color: #e94560;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .loading-overlay p {
            color: white;
            font-size: 1.2em;
        }

        @media (max-width: 768px) {
            .header h1 { font-size: 1.4em; }
            .header { padding: 15px; }
            .filtros { top: 85px; padding: 10px; gap: 5px; }
            .filtro-btn { padding: 5px 12px; font-size: 0.75em; }
            .jogos-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
            .jogo-card { padding: 10px; }
            .jogo-card .jogo-nome { font-size: 0.8em; }
            .iframe-container { height: 45vh; }
            .game-title { font-size: 0.9em; }
        }
        @media (max-width: 480px) {
            .jogos-grid { grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); }
            .jogo-card .jogo-emoji { font-size: 1.3em; }
            .jogo-card .jogo-nome { font-size: 0.7em; }
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <p>🔄 Carregando jogo...</p>
    </div>

    <div class="header">
        <h1>🎰 SORTE NA BET</h1>
        <p>🎮 Todos os jogos em um só lugar • Ao vivo • Slots • Crash</p>
        <div class="stats">
            📊 <span id="totalJogos">{{ urls|length if urls else 0 }}</span> jogos disponíveis
            • 
            🏷️ <span id="totalProvedores">{{ provedores|length if provedores else 0 }}</span> provedores
        </div>
    </div>

    <div class="filtros" id="filtros">
        <button class="filtro-btn active" data-provedor="todos">🎯 Todos</button>
        {% for provedor in provedores %}
        <button class="filtro-btn" data-provedor="{{ provedor }}">{{ provedor|title }}</button>
        {% endfor %}
    </div>

    <div class="container">
        {% if urls %}
        <div class="jogos-grid" id="jogosGrid">
            {% for jogo in urls %}
            <div class="jogo-card" data-provedor="{{ jogo.provedor }}" data-slug="{{ jogo.slug }}" onclick="carregarJogo('{{ jogo.slug }}', '{{ jogo.nome }}', '{{ jogo.provedor }}', this)">
                <span class="jogo-emoji">{{ jogo.nome.split(' ')[0] }}</span>
                <span class="jogo-nome">{{ jogo.nome.split(' ')[1:]|join(' ') }}</span>
                <span class="provedor-tag">{{ jogo.provedor }}</span>
                <div class="cor-bar" style="background: {{ jogo.cor }};"></div>
            </div>
            {% endfor %}
        </div>

        <div class="game-panel">
            <div class="game-header">
                <div class="game-title">
                    <span id="gameTitle">{{ urls[0].nome if urls else 'Nenhum jogo' }}</span>
                    <span class="provedor-badge" id="gameProvider">{{ urls[0].provedor if urls else '' }}</span>
                </div>
                <div class="game-status online" id="gameStatus">
                    <span class="dot"></span>
                    <span>Conectado</span>
                </div>
            </div>
            <div class="iframe-container">
                <iframe id="gameFrame" src="{{ urls[0].url if urls else '' }}" allow="autoplay; fullscreen; camera; microphone"></iframe>
            </div>
        </div>

        <div class="info">
            💡 Todos os jogos carregam diretamente no seu navegador. 
            Certifique-se de estar logado na Sorte na Bet para uma experiência completa.
            <br>
            🔄 <a href="javascript:location.reload()">Recarregar jogos</a> • 
            🔄 <a href="javascript:recarregarJogoAtual()">Recarregar jogo atual</a>
        </div>
        {% else %}
        <div class="error-msg">
            ❌ Nenhum jogo encontrado.<br>
            <small style="font-size: 0.6em;">Verifique se você está logado e tente novamente.</small>
        </div>
        {% endif %}
    </div>

    <script>
        let jogoAtual = null;
        let provedorAtual = 'todos';
        let currentSlug = '{{ urls[0].slug if urls else "" }}';

        async function carregarJogo(slug, nome, provedor, element) {
            const overlay = document.getElementById('loadingOverlay');
            const gameFrame = document.getElementById('gameFrame');
            const gameTitle = document.getElementById('gameTitle');
            const gameProvider = document.getElementById('gameProvider');
            const gameStatus = document.getElementById('gameStatus');

            // Mostra loading
            overlay.classList.add('active');
            gameStatus.className = 'game-status loading';
            gameStatus.innerHTML = '<span class="dot"></span><span>Carregando...</span>';

            gameTitle.textContent = nome;
            gameProvider.textContent = provedor;
            currentSlug = slug;

            document.querySelectorAll('.jogo-card').forEach(el => el.classList.remove('active'));
            if (element) element.classList.add('active');

            try {
                // Busca a URL via API
                const response = await fetch(`/api/jogar/${slug}`);
                const data = await response.json();

                if (data.success && data.url) {
                    // Carrega o jogo
                    gameFrame.src = data.url;
                    gameStatus.className = 'game-status online';
                    gameStatus.innerHTML = '<span class="dot"></span><span>Conectado</span>';
                } else {
                    // Erro ao obter URL
                    gameStatus.className = 'game-status error';
                    gameStatus.innerHTML = '<span class="dot"></span><span>Erro ao carregar</span>';
                    alert('❌ Não foi possível carregar o jogo. Tente novamente.');
                }
            } catch (error) {
                console.error('Erro ao carregar jogo:', error);
                gameStatus.className = 'game-status error';
                gameStatus.innerHTML = '<span class="dot"></span><span>Erro de conexão</span>';
                alert('❌ Erro de conexão. Verifique sua internet.');
            } finally {
                overlay.classList.remove('active');
            }

            document.querySelector('.game-panel').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        function recarregarJogoAtual() {
            if (currentSlug) {
                const card = document.querySelector(`.jogo-card[data-slug="${currentSlug}"]`);
                if (card) {
                    const nome = card.querySelector('.jogo-nome').textContent;
                    const provedor = card.dataset.provedor;
                    carregarJogo(currentSlug, nome, provedor, card);
                }
            }
        }

        // FILTROS
        document.querySelectorAll('.filtro-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filtro-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                provedorAtual = this.dataset.provedor;
                filtrarJogos();
            });
        });

        function filtrarJogos() {
            const cards = document.querySelectorAll('.jogo-card');
            let visiveis = 0;

            cards.forEach(card => {
                if (provedorAtual === 'todos' || card.dataset.provedor === provedorAtual) {
                    card.style.display = 'block';
                    visiveis++;
                } else {
                    card.style.display = 'none';
                }
            });

            document.getElementById('totalJogos').textContent = visiveis;
        }

        // CARREGAR PRIMEIRO JOGO AUTOMATICAMENTE
        document.addEventListener('DOMContentLoaded', function() {
            const primeiroJogo = document.querySelector('.jogo-card');
            if (primeiroJogo) {
                primeiroJogo.classList.add('active');
            }
            const total = document.querySelectorAll('.jogo-card').length;
            document.getElementById('totalJogos').textContent = total;
        });

        console.log('🎮 Sorte na Bet - Todos os jogos carregados!');
        console.log('Total de jogos:', document.querySelectorAll('.jogo-card').length);
    </script>
</body>
</html>
"""

# ========== ROTAS ==========
@app.route('/')
def index():
    """Página principal com todos os jogos."""
    if not fazer_login():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>Erro</title></head>
        <body style="background:#0a0a1a;color:white;text-align:center;padding:50px;font-family:Segoe UI;">
            <h1 style="color:#e94560;">❌ Erro ao fazer login</h1>
            <p>Verifique suas credenciais e tente novamente.</p>
            <button onclick="location.reload()" style="padding:10px 30px;background:#e94560;border:none;color:white;border-radius:8px;cursor:pointer;font-size:16px;">🔁 Tentar novamente</button>
        </body>
        </html>
        """), 401
    
    urls = buscar_jogos()
    provedores = list(set([jogo['provedor'] for jogo in urls]))
    
    return render_template_string(HTML_TEMPLATE, urls=urls, provedores=provedores)

@app.route('/api/jogos', methods=['GET'])
def api_jogos():
    """Retorna lista de todos os jogos em JSON."""
    if not fazer_login():
        return jsonify({'success': False, 'error': 'Login falhou'}), 401
    
    urls = buscar_jogos(force_refresh=True)
    return jsonify({
        'success': True,
        'total': len(urls),
        'provedores': list(set([jogo['provedor'] for jogo in urls])),
        'jogos': urls
    })

@app.route('/api/jogar/<path:slug>', methods=['GET'])
def api_jogar(slug):
    """Retorna URL de um jogo específico."""
    url = obter_url_jogo(slug)
    
    if url:
        return jsonify({
            'success': True,
            'slug': slug,
            'url': url
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Não foi possível obter a URL do jogo'
        }), 404

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """Força a atualização do cache."""
    global cache_jogos
    with cache_lock:
        cache_jogos.clear()
    return jsonify({'success': True, 'message': 'Cache limpo'})

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'cache_size': len(cache_jogos),
        'logged_in': ultimo_login is not None
    })

# ========== MAIN ==========
if __name__ == '__main__':
    print("=" * 70)
    print("🎯 SORTE NA BET - TODOS OS JOGOS")
    print("=" * 70)
    print(f"📋 Total de jogos cadastrados: {sum(len(jogos) for jogos in JOGOS_DISPONIVEIS.values())}")
    print(f"🏷️ Provedores: {', '.join(JOGOS_DISPONIVEIS.keys())}")
    print("=" * 70)
    print("🌐 Acesse: http://localhost:5000")
    print("=" * 70)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
