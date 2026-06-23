# test_api_com_captcha.py
import requests

# 1. Primeiro, no navegador, resolva o captcha e pegue o token
# 2. Cole o token aqui
CAPTCHA_TOKEN = "t2:1.6Xoe6pONEhFMJRpieA5JllxXBvQHos1O47vGtOJOBcIt6WurzS9ydKtK9fkY9RoGBkgE2SyP1FpuwHDOnrMSOxfeS6bx7mBTobwLmV6AnU-kfFard-RWuIMlHXxVSinY1qwnSn4B8sC0jwJjY6ejSgXMqTQ4MpkkcH8UrgRvP2lbffKqZJZ8Rv6shkurSXctKzT3N5AWNfXZ3yiid1lDruDDgAGf0R0zkzmRDEgeZFjmurK3q5123TLq6dTLGmW6j8RqIjgm_tBvANr3uM9ZARbMcYOvwDNe1JIBSBMa0AH504zAlam06I7A0HSMyi3HQvCaSYoAnAFzqjrLHe2rmGO4qYKhWjgF6CAxaF3ZdY-OYoI_JR1GqSRTWESrQu_mRYnzvvRp7aNvwNiHi59iLE2gdCutTabY1rnFV7u_4qGxOhhCQ3JMHbqunQjFvsKe4-IZpSFm5LegHDa_TL17GsVqmdBWM3ZCOkoNdQ6wM4OvhHE6vcWXzUc223w1qBFt9-0Pu-zntutOzbrAeb-DBqV3xhUMsEWkuMo1_h_xdhynB0woSoTW4UcG4dcCu0Do8bAnnst9PCJODHjGH4t4XlL0LrS-NWJ4Rj3sw6hQ2FhizI2vYFalM3s2AXn0fYGfRttKy5duJcIzebqZGrCZlx0KFZ1mgKBzooReh6AR-cr-S20NrlJEQiGwXme7pFo63Ijox181l9BjW9SuoKU7qw.LTDOiyU0VwsTVH6Cd-p5Pg.cceecde84a292a1bd8f05feacb6490a4f58d5ee0dbf6a48c68082671ce0c1324"

# 3. Agora faz a requisição
response = requests.post(
    'https://sortenabet.bet.br/api/auth/login',
    headers={
        'Content-Type': 'application/json',
        'Origin': 'https://sortenabet.bet.br',
        'Referer': 'https://sortenabet.bet.br/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    json={
        "login": "gcriste268@gmail.com",
        "email": "gcriste268@gmail.com",
        "password": "284050",
        "app_source": "web",
        "captcha_token": CAPTCHA_TOKEN
    }
)

print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")
