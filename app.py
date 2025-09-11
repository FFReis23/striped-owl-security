from flask import Flask, render_template, request
import re
import tldextract
import requests
import socket
import ssl
from datetime import datetime
import whois

app = Flask(__name__)

# Contadores globais
stats = {
    "total": 0,
    "safe": 0,
    "suspicious": 0,
    "malicious": 0
}

# Função aprimorada para verificar URL
def is_suspicious(url):
    reasons = []
    details = []
    ext = tldextract.extract(url)

    # HTTPS e SSL
    if not url.startswith("https://"):
        reasons.append("URL não utiliza HTTPS")
    else:
        try:
            hostname = ext.domain + "." + ext.suffix
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                s.settimeout(3)
                s.connect((hostname, 443))
                cert = s.getpeercert()
                exp_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
                if exp_date < datetime.utcnow():
                    reasons.append("Certificado SSL expirado")
        except:
            reasons.append("Erro ao verificar SSL/TLS")

    # IP na URL
    if re.match(r"^https?:\/\/\d+\.\d+\.\d+\.\d+", url):
        reasons.append("Uso de IP no lugar de domínio")

    # Subdomínios
    if len(ext.subdomain.split('.')) > 2:
        reasons.append("Muitos subdomínios")

    # Palavras suspeitas
    palavras_suspeitas = ["login", "secure", "update", "verify", "account", "bank", "confirm", "payment"]
    if any(p in url.lower() for p in palavras_suspeitas):
        reasons.append("Contém palavras suspeitas")

    # Lista negra
    blacklist = ["malicious-site.com", "phishing-domain.net"]
    if ext.domain in blacklist:
        reasons.append(f"Domínio na lista negra: {ext.domain}")

    # WHOIS (idade do domínio)
    try:
        w = whois.whois(url)
        if hasattr(w, "creation_date") and w.creation_date:
            if isinstance(w.creation_date, list):
                creation_date = w.creation_date[0]
            else:
                creation_date = w.creation_date
            age_days = (datetime.now() - creation_date).days
            if age_days < 30:
                reasons.append("Domínio muito recente")
            details.append(f"Idade do domínio: {age_days} dias")
    except:
        details.append("Não foi possível obter informações WHOIS")

    # Redirecionamentos
    try:
        resp = requests.head(url, allow_redirects=True, timeout=3)
        if len(resp.history) > 0:
            details.append(f"Redirecionamentos detectados ({len(resp.history)} etapas)")
    except:
        details.append("Não foi possível checar redirecionamentos")

    # Google Safe Browsing
    api_key = "SUA_API_KEY"  # Substitua pela sua chave
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload = {
        "client": {"clientId": "url-checker", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        result = response.json()
        if result.get("matches"):
            reasons.append("⚠️ URL maliciosa detectada pelo Google Safe Browsing")
    except:
        details.append("Não foi possível checar Google Safe Browsing")

    # Resultado final
    result_text = ""
    if reasons:
        result_text += "⚠️ URL suspeita: " + ", ".join(reasons) + "\n"
    else:
        result_text += "✅ URL parece segura\n"

    if details:
        result_text += "\n".join(details)

    return result_text

@app.route("/ataques")
def ataques():
    return render_template("ataques.html")

# Rota principal
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            result = is_suspicious(url)
            stats["total"] += 1
            if "maliciosa" in result:
                stats["malicious"] += 1
            elif "suspeita" in result:
                stats["suspicious"] += 1
            else:
                stats["safe"] += 1
    return render_template("index.html", result=result, stats=stats)

if __name__ == "__main__":
    app.run(debug=True)
