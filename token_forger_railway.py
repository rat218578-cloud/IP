import requests
import json
import time
import urllib.parse

print("=" * 60)
print("🎯 PRAGMATIC PLAY - MEGA ROLETA IMERSIVA")
print("=" * 60)

# ========== CONFIGURAÇÕES ==========
CAPTCHA_TOKEN = "t2:1.ifdoY2ZRtYg8dM7vqQxdFVRqSeTJogrlF6EqbMrBWFzX9BC_mnw_vjuuhF8_bLUd1tViQrscFD9eTmSshUbuownZ4HOfKF7n61LxFjOsB7QRjk-4K-g67GfTShapvUPBIuoojAMxZzOvMDif2tj29uZsfaJEKuFdRnj6DgFcDiiKyY-HKNy-n0RfwoIs7VE6TzAISk-pMPpKXD6uHFKHR7gWxWNpsksMQLBeIkg7KvgXzTcHUt8VnVEpSsugGkNMV_1AeEN43O9eH91WU2Vef_3iyie6KPgimWq1ly82r1BSvBSs0lt5FgF7LYfzWSkeO3ApOYjWgnQXFYDntAMIioM_MDxGdD48JDNWvpoua3PRsq3Gpoj5BdlJ2qlguGl3NWOUAAYeOL0UMgiB0G9QmpLwFn7SWyoM2GvSDuyqGLMx4B9pJ6ntW0qrXVk2cd5Rm-6eoAVCfbIUoPVtt9nGY_nS7yNTMQg5uOZggTgI8D2ar9aKdFDBD9qtbY3gHQW0Sy3d7iMkalbbLeeIq4oLsqwtGYJgJzsbIR61J1mWA1L34Hosv_qAz4e6bFovRn3efFejTbZmP4eD7zVaacfdufZY9fAC2K5wEXTR7rwVqlGknlwi9-3r9JgwrKpL3tZmRmzwNK5aEpS2DWqNrDt-lv4fsnLJYb7XmfCoYGd7EBMgnvREpViF2HFonRMeP7qmtQnocHJ71gUEMbXtwMIzdQ.ODr74DV1RP4y9w1JfkgYWA.a6b915441ca8df4a77de54d936420e701d16f894798dd9dd54650ddfead9a042"

session = requests.Session()

headers = {
    'Content-Type': 'application/json',
    'Origin': 'https://sortenabet.bet.br',
    'Referer': 'https://sortenabet.bet.br/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

session.headers.update(headers)

# ========== 1. LOGIN ==========
print("\n🔐 FAZENDO LOGIN...")

login_data = {
    "login": "gcriste268@gmail.com",
    "email": "gcriste268@gmail.com",
    "password": "284050",
    "app_source": "web",
    "captcha_token": CAPTCHA_TOKEN
}

response = session.post('https://sortenabet.bet.br/api/auth/login', json=login_data)

if response.status_code == 200:
    access_token = response.json().get('access_token')
    session.headers.update({'Authorization': f'Bearer {access_token}'})
    print(f"✅ Login OK!")
else:
    print(f"❌ Login falhou: {response.text}")
    exit()

# ========== 2. PEGAR URL DA PRAGMATIC PLAY ==========
print("\n🎮 BUSCANDO JOGOS DA PRAGMATIC PLAY...")

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
                print(f"   ✅ {slug}")
            else:
                print(f"   ⚠️ {slug} - sem URL")
        else:
            print(f"   ❌ {slug}: HTTP {response.status_code}")

        time.sleep(0.3)

    except Exception as e:
        print(f"   ❌ {slug}: erro - {str(e)[:40]}")

# ========== 3. GERAR HTML COM IFRAME DA PRAGMATIC ==========
print("\n" + "=" * 60)
print("📄 GERANDO HTML COM IFRAME PRAGMATIC PLAY...")

if urls_pragmatic:
    # Pega a primeira URL (Mega Roleta)
    primeiro_jogo = urls_pragmatic[0]

    html_content = f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎰 Pragmatic Play - Mega Roleta Imersiva</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
        }}

        .header {{
            background: rgba(0,0,0,0.9);
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #e94560;
        }}

        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
            color: white;
        }}

        .header h1 span {{
            color: #e94560;
        }}

        .header p {{
            color: #ccc;
        }}

        .container {{
            max-width: 1400px;
            margin: 20px auto;
            padding: 0 20px;
        }}

        .jogo-selector {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }}

        .jogo-selector h3 {{
            color: white;
            margin-bottom: 10px;
        }}

        .jogos-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }}

        .jogo-btn {{
            background: rgba(255,255,255,0.1);
            border: none;
            color: white;
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }}

        .jogo-btn:hover {{
            background: #e94560;
            transform: translateY(-2px);
        }}

        .jogo-btn.active {{
            background: #e94560;
            border: 2px solid white;
        }}

        .game-panel {{
            background: #0f0f1a;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}

        .game-header {{
            background: #1a1a2e;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e94560;
        }}

        .game-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: white;
        }}

        .game-status {{
            padding: 5px 15px;
            border-radius: 20px;
            background: #27ae60;
            font-size: 0.8em;
            color: white;
        }}

        .iframe-container {{
            position: relative;
            width: 100%;
            height: 75vh;
            background: #000;
        }}

        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}

        .info {{
            background: rgba(0,0,0,0.7);
            padding: 10px;
            margin-top: 10px;
            border-radius: 8px;
            text-align: center;
            color: #ccc;
            font-size: 12px;
        }}

        @media (max-width: 768px) {{
            .iframe-container {{
                height: 50vh;
            }}
            .header h1 {{
                font-size: 1.2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎰 <span>PRAGMATIC PLAY</span> | Mega Roleta Imersiva</h1>
        <p>Jogos ao vivo com dealer real • Roleta • Slots • Crash Games</p>
    </div>

    <div class="container">
        <div class="jogo-selector">
            <h3>🎮 Selecione o jogo:</h3>
            <div class="jogos-grid" id="jogosGrid">
'''

    for jogo in urls_pragmatic:
        html_content += f'                <button class="jogo-btn" onclick="carregarJogo(\'{jogo["url"]}\', \'{jogo["nome"]}\')">🎰 {jogo["nome"]}</button>\n'

    html_content += f'''            </div>
        </div>

        <div class="game-panel">
            <div class="game-header">
                <span class="game-title" id="gameTitle">{primeiro_jogo["nome"]}</span>
                <span class="game-status" id="gameStatus">🟢 Conectado</span>
            </div>
            <div class="iframe-container">
                <iframe id="gameFrame" src="{primeiro_jogo["url"]}" allow="autoplay; fullscreen; camera; microphone"></iframe>
            </div>
        </div>

        <div class="info">
            💡 Dica: Os jogos da Pragmatic Play carregam diretamente no seu navegador.
            Certifique-se de estar logado na Sorte na Bet para uma experiência completa.
        </div>
    </div>

    <script>
        function carregarJogo(url, nome) {{
            const gameFrame = document.getElementById('gameFrame');
            const gameTitle = document.getElementById('gameTitle');
            const gameStatus = document.getElementById('gameStatus');

            gameStatus.textContent = '🟡 Carregando...';
            gameStatus.style.background = '#f39c12';
            gameTitle.textContent = nome;

            // Pequeno delay para dar efeito de carregamento
            setTimeout(() => {{
                gameFrame.src = url;
                gameStatus.textContent = '🟢 Conectado';
                gameStatus.style.background = '#27ae60';
            }}, 100);

            // Scroll suave para o iframe
            document.querySelector('.game-panel').scrollIntoView({{ behavior: 'smooth' }});

            // Marca o botão ativo
            document.querySelectorAll('.jogo-btn').forEach(btn => {{
                btn.classList.remove('active');
                if (btn.textContent.includes(nome)) {{
                    btn.classList.add('active');
                }}
            }});
        }}

        console.log('🎮 Pragmatic Play carregada!');
        console.log('Jogos disponíveis:', {len(urls_pragmatic)});
    </script>
</body>
</html>
'''

    with open('pragmatic_play.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Página gerada: pragmatic_play.html")
    print(f"   📊 Total de jogos: {len(urls_pragmatic)}")

    # ========== 4. SALVAR URLs EM TXT ==========
    with open('pragmatic_urls.txt', 'w') as f:
        for jogo in urls_pragmatic:
            f.write(f"{jogo['nome']}:\n{jogo['url']}\n\n")

    print(f"   💾 URLs salvas em pragmatic_urls.txt")

    # ========== 5. MOSTRAR URL PRINCIPAL ==========
    print("\n" + "=" * 60)
    print("🎯 URL DO IFRAME PRAGMATIC PLAY:")
    print("=" * 60)
    print(f"\n{primeiro_jogo['url']}\n")
    print("=" * 60)
    print("📋 COMO USAR:")
    print("   1. Abra o arquivo 'pragmatic_play.html' no seu navegador")
    print("   2. Ou copie a URL acima e cole no navegador")
    print("   3. O jogo vai carregar normalmente!")
    print("=" * 60)

else:
    print("❌ Nenhum jogo da Pragmatic Play encontrado!")

    # Tenta um slug específico
    print("\n🔄 Tentando slug alternativo...")
    slugs_alternativos = [
        'pragmatic/mega-roleta',
        'pragmaticplay/roulette',
        'pragmatic/roulette',
        'mega-roleta'
    ]

    for slug in slugs_alternativos:
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
            print(f"   Testando '{slug}': {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Encontrado! Resposta: {json.dumps(data, indent=2)[:500]}")
                break
        except:
            pass
