from flask import Flask, request, render_template_string, jsonify
import requests
import json
import time

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Palz-Coder ☠️ Proxy Generator (Data Impulse Advanced)</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a0a; color: #00ffcc; font-family: 'Courier New', monospace; padding: 20px; }
        h1 { text-align: center; color: #ff0040; text-shadow: 0 0 10px #ff0040; margin-bottom: 5px; }
        .sub { text-align: center; color: #666; margin-bottom: 20px; }
        .container { max-width: 1000px; margin: 0 auto; background: #111; padding: 25px; border-radius: 10px; border: 1px solid #ff0040; }
        .section-title { color: #ff0040; font-size: 1.2em; margin: 20px 0 10px 0; border-bottom: 1px solid #ff0040; padding-bottom: 5px; }
        .row { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 12px; align-items: center; }
        .row label { min-width: 140px; color: #00ffcc; }
        .row input, .row select { flex: 1; padding: 8px; background: #222; color: #0f0; border: 1px solid #00ffcc; border-radius: 4px; font-family: monospace; }
        .row input[type="checkbox"] { flex: 0; width: auto; margin-right: 10px; }
        .row .checkbox-group { display: flex; align-items: center; gap: 5px; }
        .row .count-hint { color: #888; font-size: 0.9em; margin-left: 5px; }
        .btn { padding: 8px 25px; background: #ff0040; color: #fff; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
        .btn:hover { background: #cc0033; }
        .btn-secondary { background: #333; }
        .btn-secondary:hover { background: #555; }
        .output-area { background: #0a0a0a; padding: 15px; border: 1px solid #00ffcc; border-radius: 4px; margin-top: 15px; max-height: 400px; overflow-y: auto; }
        .output-area pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; color: #0f0; }
        .action-buttons { display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap; }
        .copy-btn { background: #333; color: #0f0; border: 1px solid #00ffcc; }
        .copy-btn:hover { background: #00ffcc; color: #000; }
        .footer { text-align: center; margin-top: 20px; color: #444; }
        .inline-flex { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
        .error { color: #ff5555; }
        .success { color: #55ff55; }
        .example-box { background: #222; padding: 10px; border-radius: 4px; margin-top: 10px; border: 1px solid #444; }
        .example-box code { color: #ffcc00; }
        .coeff { color: #ffaa00; font-size: 0.9em; }
        .detect-box { border:1px solid #ff0040; padding:10px; border-radius:5px; background:#1a1a1a; }
    </style>
</head>
<body>
    <h1>☠️ PALZ-CODER PROXY GENERATOR ☠️</h1>
    <div class="sub">-- Advanced Data Impulse Clone --</div>
    <div class="container">
        <form id="proxyForm" method="POST" action="/generate">

            <!-- Auto-detect from IP -->
            <div class="section-title">📡 Auto-Detect from IP</div>
            <div class="row detect-box">
                <label>IP Address</label>
                <input type="text" id="detectIpInput" placeholder="e.g. 103.157.193.70" style="flex:2;">
                <button type="button" class="btn btn-secondary" onclick="detectIP()" style="flex:0;">🔍 Detect</button>
                <span id="detectStatus" style="color:#ffaa00; margin-left:10px;"></span>
            </div>

            <!-- Target Filters Section -->
            <div class="section-title">🎯 Target Filters</div>

            <!-- Country -->
            <div class="row">
                <label>Country</label>
                <select name="country" id="countrySelect">
                    <option value="">All Countries</option>
                    {% for c in countries %}
                        <option value="{{ c }}">{{ c }}</option>
                    {% endfor %}
                </select>
                <span class="count-hint" id="countryCount">(0 IP's)</span>
            </div>
            <div class="row" style="color:#888; font-size:0.9em; margin-top:-10px;">
                <span class="coeff">⚡ The usage traffic with these parameters will be counted at a coefficient of x2</span>
            </div>

            <!-- State -->
            <div class="row">
                <label>State</label>
                <input type="text" name="state" placeholder="e.g. Lampung">
                <span class="count-hint" id="stateCount">(~0 IP's)</span>
            </div>

            <!-- City -->
            <div class="row">
                <label>City</label>
                <input type="text" name="city" placeholder="e.g. Bandar Lampung">
                <span class="count-hint" id="cityCount">(~0 IP's)</span>
            </div>

            <!-- Zip code -->
            <div class="row">
                <label>Zip code</label>
                <input type="text" name="zip" placeholder="All zipcodes" value="All zipcodes">
                <span class="count-hint">(not used in free API, goblok!)</span>
            </div>

            <!-- ASN -->
            <div class="row">
                <label>ASN</label>
                <input type="text" name="asn" placeholder="e.g. 23693">
                <span class="count-hint" id="asnCount">(~0 IP's)</span>
            </div>

            <!-- Rotation interval -->
            <div class="row">
                <label>Rotation interval</label>
                <input type="number" name="rotation_interval" min="0" max="120" value="0" style="flex:0 0 100px;">
                <span class="count-hint">(0-120 seconds)</span>
            </div>

            <!-- Anonymous filter & Exclude ASN -->
            <div class="row">
                <label>Anonymous filter</label>
                <div class="checkbox-group">
                    <input type="checkbox" name="anonymous_filter" id="anonFilter">
                    <label for="anonFilter" style="min-width:auto;">Enable</label>
                </div>
            </div>
            <div class="row">
                <label>Exclude ASN</label>
                <div class="checkbox-group">
                    <input type="checkbox" name="exclude_asn_enable" id="excludeAsn">
                    <label for="excludeAsn" style="min-width:auto;">Enable</label>
                </div>
                <input type="text" name="exclude_asn_list" placeholder="AS Numbers to exclude (comma separated)" style="flex:2;">
            </div>

            <!-- End of Target Filters -->

            <!-- Configuration & Output settings -->
            <div class="section-title" style="margin-top:30px;">⚙️ Configuration</div>
            <div class="row">
                <label>Hostname</label>
                <input type="text" name="hostname" placeholder="e.g. proxy.mycompany.com">
            </div>
            <div class="row">
                <label>DNS hostname</label>
                <input type="text" name="dns_hostname" placeholder="e.g. dns.proxy.com">
            </div>
            <!-- TAMBAHAN: PROXY HOST & PASSWORD -->
            <div class="row">
                <label>Proxy Host</label>
                <input type="text" name="proxy_host" placeholder="e.g. gw.dataimpulse.com">
            </div>
            <div class="row">
                <label>Password</label>
                <input type="text" name="proxy_password" placeholder="e.g. ee2b2f208af0dde6">
            </div>
            <!-- END TAMBAHAN -->
            <div class="row">
                <label>Type</label>
                <div class="inline-flex">
                    <label><input type="radio" name="proxy_type" value="rotating" checked> Rotating</label>
                    <label><input type="radio" name="proxy_type" value="sticky"> Sticky</label>
                </div>
            </div>
            <div class="row">
                <label>Protocol</label>
                <div class="inline-flex">
                    <label><input type="radio" name="protocol" value="http" checked> HTTP/HTTPS</label>
                    <label><input type="radio" name="protocol" value="socks5"> SOCKS5</label>
                </div>
            </div>

            <!-- Basic URL example -->
            <div class="row">
                <label>Basic URL example</label>
                <div class="example-box">
                    <code id="curlExample">curl -x "http://proxy.example:8080" https://api.ipify.org</code>
                </div>
            </div>

            <!-- Quantity & Format -->
            <div class="row">
                <label>Quantity</label>
                <input type="number" name="quantity" value="10" min="1" max="100" style="flex:0 0 100px;">
                <label style="min-width:auto; margin-left:20px;">Format</label>
                <select name="format" style="flex:0 0 150px;">
                    <option value="plain">Plain Text</option>
                    <option value="json">JSON</option>
                </select>
            </div>

            <!-- Generate Button -->
            <div class="row" style="justify-content:center; margin-top:10px;">
                <button type="submit" class="btn">🔍 GENERATE PROXIES</button>
                <button type="button" class="btn btn-secondary" onclick="clearConfig()">Clear configuration</button>
                <button type="button" class="btn btn-secondary" onclick="saveConfig()">Save configuration</button>
            </div>
        </form>

        <!-- Proxy List Output -->
        <div id="outputContainer" style="margin-top:20px;">
            <div class="output-area" id="proxyOutput">
                <pre id="outputText">Proxy list will appear here, goblok!</pre>
            </div>
            <div class="action-buttons">
                <button class="btn btn-secondary copy-btn" onclick="copyOutput()">📋 Copy</button>
                <button class="btn btn-secondary" onclick="downloadOutput()">⬇️ Download</button>
                <span id="statusMsg" style="color:#00ffcc; margin-left:10px;"></span>
            </div>
        </div>
    </div>
    <div class="footer">☠️ Powered by Palz-Coder | Resiko penggunaan tanggung sendiri, kontol!</div>

    <script>
        // ========== DETECT IP ==========
        function detectIP() {
            var ip = document.getElementById('detectIpInput').value.trim();
            if (!ip) {
                document.getElementById('detectStatus').innerText = '❌ Masukkan IP dulu, tai!';
                return;
            }
            document.getElementById('detectStatus').innerText = '⏳ Detecting...';
            fetch('/detect_ip', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ip: ip})
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('detectStatus').innerText = '❌ ' + data.error;
                    return;
                }
                var countrySelect = document.querySelector('select[name="country"]');
                var countryOpts = countrySelect.options;
                for (var i=0; i<countryOpts.length; i++) {
                    if (countryOpts[i].value === data.country) {
                        countrySelect.selectedIndex = i;
                        break;
                    }
                }
                document.querySelector('input[name="state"]').value = data.region;
                document.querySelector('input[name="city"]').value = data.city;
                document.querySelector('input[name="asn"]').value = data.asn;
                document.getElementById('detectStatus').innerText = '✅ Detected: ' + data.country + ', ' + data.region + ', ' + data.city + ', AS' + data.asn;
                document.getElementById('countryCount').innerText = '(~' + data.ip_count + ' IP\'s)';
            })
            .catch(err => {
                document.getElementById('detectStatus').innerText = '❌ Error: ' + err;
            });
        }

        // ========== COPY & DOWNLOAD ==========
        function copyOutput() {
            var text = document.getElementById('outputText').innerText;
            if (text && text !== 'Proxy list will appear here, goblok!') {
                navigator.clipboard.writeText(text).then(function() {
                    document.getElementById('statusMsg').innerText = '✅ Copied!';
                }, function() {
                    document.getElementById('statusMsg').innerText = '❌ Failed to copy';
                });
            } else {
                document.getElementById('statusMsg').innerText = '⚠️ Nothing to copy, generate first!';
            }
        }

        function downloadOutput() {
            var text = document.getElementById('outputText').innerText;
            if (text && text !== 'Proxy list will appear here, goblok!') {
                var blob = new Blob([text], {type: 'text/plain'});
                var a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = 'proxies.txt';
                a.click();
                document.getElementById('statusMsg').innerText = '⬇️ Downloaded!';
            } else {
                document.getElementById('statusMsg').innerText = '⚠️ Nothing to download, generate first!';
            }
        }

        // ========== CLEAR & SAVE CONFIG ==========
        function clearConfig() {
            document.querySelectorAll('input, select').forEach(el => {
                if (el.type === 'checkbox') el.checked = false;
                else if (el.type === 'text' || el.type === 'number') el.value = '';
                else if (el.tagName === 'SELECT') el.selectedIndex = 0;
            });
            document.getElementById('outputText').innerText = 'Configuration cleared, goblok!';
            document.getElementById('statusMsg').innerText = '';
            document.getElementById('countryCount').innerText = '(0 IP\'s)';
            document.getElementById('stateCount').innerText = '(~0 IP\'s)';
            document.getElementById('cityCount').innerText = '(~0 IP\'s)';
            document.getElementById('asnCount').innerText = '(~0 IP\'s)';
        }

        function saveConfig() {
            var form = document.getElementById('proxyForm');
            var data = new FormData(form);
            var config = {};
            for (var [key, val] of data.entries()) {
                config[key] = val;
            }
            localStorage.setItem('proxyConfig', JSON.stringify(config));
            document.getElementById('statusMsg').innerText = '✅ Configuration saved locally!';
        }

        // ========== LOAD SAVED CONFIG ==========
        window.onload = function() {
            var saved = localStorage.getItem('proxyConfig');
            if (saved) {
                var config = JSON.parse(saved);
                for (var key in config) {
                    var el = document.querySelector('[name="' + key + '"]');
                    if (el) {
                        if (el.type === 'checkbox') el.checked = config[key] === 'on';
                        else if (el.type === 'radio') {
                            var radio = document.querySelector('[name="' + key + '"][value="' + config[key] + '"]');
                            if (radio) radio.checked = true;
                        } else el.value = config[key];
                    }
                }
                document.getElementById('statusMsg').innerText = '🔄 Loaded saved config!';
            }
        };
    </script>
</body>
</html>
'''

COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
    "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia",
    "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon",
    "Canada", "Cape Verde", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo",
    "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominican Republic", "Ecuador",
    "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France",
    "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Guatemala", "Guinea", "Guyana", "Haiti", "Honduras",
    "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Ivory Coast", "Jamaica",
    "Japan", "Jordan", "Kazakhstan", "Kenya", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Liberia", "Libya",
    "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta",
    "Mauritania", "Mauritius", "Mexico", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique",
    "Myanmar", "Namibia", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia",
    "Norway", "Oman", "Pakistan", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
    "Qatar", "Romania", "Russia", "Rwanda", "Saudi Arabia", "Senegal", "Serbia", "Sierra Leone", "Singapore", "Slovakia",
    "Slovenia", "South Africa", "South Korea", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland",
    "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Trinidad and Tobago", "Tunisia", "Turkey",
    "Turkmenistan", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay",
    "Uzbekistan", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
]

def get_proxies(protocol='http', anonymous=False):
    if protocol == 'socks5':
        base = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all&ssl=all"
    else:
        base = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all"
    if anonymous:
        base += "&anonymity=anonymous"
    try:
        resp = requests.get(base, timeout=10)
        if resp.status_code == 200:
            lines = resp.text.strip().splitlines()
            return [line.strip() for line in lines if line.strip()][:300]
        return []
    except:
        return []

def get_ip_info_batch(ips):
    if not ips:
        return []
    try:
        payload = json.dumps(ips)
        resp = requests.post("http://ip-api.com/batch", data=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            result = []
            for item in data:
                if item.get('status') == 'success':
                    result.append({
                        'ip': item.get('query'),
                        'country': item.get('country', ''),
                        'countryCode': item.get('countryCode', ''),
                        'region': item.get('regionName', ''),
                        'city': item.get('city', ''),
                        'as': item.get('as', '')
                    })
                else:
                    result.append({'ip': item.get('query'), 'error': True})
            return result
        return []
    except:
        return []

@app.route('/')
def index():
    return render_template_string(HTML, countries=COUNTRIES)

@app.route('/generate', methods=['POST'])
def generate():
    country = request.form.get('country', '').strip()
    state = request.form.get('state', '').strip().lower()
    city = request.form.get('city', '').strip().lower()
    asn_input = request.form.get('asn', '').strip()
    anonymous = request.form.get('anonymous_filter') == 'on'
    exclude_asn_enable = request.form.get('exclude_asn_enable') == 'on'
    exclude_asn_list = request.form.get('exclude_asn_list', '').strip()
    protocol = request.form.get('protocol', 'http')
    quantity = int(request.form.get('quantity', 10))
    fmt = request.form.get('format', 'plain')
    
    # Ambil nilai Proxy Host & Password
    proxy_host = request.form.get('proxy_host', '').strip()
    proxy_password = request.form.get('proxy_password', '').strip()

    proxy_list = get_proxies(protocol, anonymous)
    if not proxy_list:
        return render_template_string(HTML, countries=COUNTRIES, error="Gagal ambil proxy, coba lagi nanti.", result=None)

    ip_ports = [p.split(':') for p in proxy_list if ':' in p]
    if not ip_ports:
        return render_template_string(HTML, countries=COUNTRIES, error="Format proxy invalid, kontol!", result=None)

    ips = list(set([p[0] for p in ip_ports]))
    all_info = []
    for i in range(0, len(ips), 100):
        batch = ips[i:i+100]
        info = get_ip_info_batch(batch)
        all_info.extend(info)
        time.sleep(0.3)

    filtered = []
    for ip_port in ip_ports:
        ip = ip_port[0]
        port = ip_port[1] if len(ip_port) > 1 else '8080'
        info = next((i for i in all_info if i.get('ip') == ip), None)
        if not info or info.get('error'):
            continue

        if country and info.get('country', '').lower() != country.lower():
            continue
        if state and state not in info.get('region', '').lower():
            continue
        if city and city not in info.get('city', '').lower():
            continue
        if asn_input:
            asn_str = info.get('as', '')
            asn_num = asn_str.split(' ')[0] if asn_str else ''
            if asn_num != asn_input.upper():
                continue
        if exclude_asn_enable and exclude_asn_list:
            exclude_asns = [a.strip().upper() for a in exclude_asn_list.split(',') if a.strip()]
            asn_str = info.get('as', '')
            asn_num = asn_str.split(' ')[0] if asn_str else ''
            if asn_num in exclude_asns:
                continue

        filtered.append({
            'ip': ip,
            'port': port,
            'country': info.get('country', ''),
            'countryCode': info.get('countryCode', ''),
            'region': info.get('region', ''),
            'city': info.get('city', ''),
            'asn': info.get('as', '')
        })

    filtered = filtered[:quantity]

    # Format output
    proxy_lines = []
    for item in filtered:
        line = f"{item['ip']}:{item['port']}__cr.{item['countryCode']};state.{item['region']};city.{item['city']};asn.{item['asn']}"
        proxy_lines.append(line)

    if fmt == 'json':
        output_text = json.dumps(proxy_lines, indent=2)
    else:
        output_text = "\n".join(proxy_lines)

    # Tambahkan informasi Proxy Host & Password di atas output
    if proxy_host or proxy_password:
        info_text = f"Proxy Host: {proxy_host}\nPassword: {proxy_password}\n\n"
        output_text = info_text + output_text

    return render_template_string(HTML, countries=COUNTRIES, result=output_text, error=None)

@app.route('/detect_ip', methods=['POST'])
def detect_ip():
    data = request.get_json()
    ip = data.get('ip', '').strip()
    if not ip:
        return jsonify({'error': 'IP kosong, kontol!'})
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if resp.status_code == 200:
            info = resp.json()
            if info.get('status') == 'success':
                asn_raw = info.get('as', '')
                asn_num = asn_raw.split(' ')[0].replace('AS', '') if asn_raw else ''
                return jsonify({
                    'country': info.get('country', ''),
                    'region': info.get('regionName', ''),
                    'city': info.get('city', ''),
                    'asn': asn_num,
                    'ip_count': 10
                })
            else:
                return jsonify({'error': 'IP ga valid atau private'})
        else:
            return jsonify({'error': 'Gagal query API'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
