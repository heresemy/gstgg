#!/usr/bin/env python3
"""
RISHANT X EXECUTOR — API VERSION
Same logic as executor | Flask API | Guest Gen + Activator
"""

import os, sys, json, time, random, string, hashlib, hmac, uuid, re, base64
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from flask import Flask, request, jsonify

import requests, urllib3
from requests.adapters import HTTPAdapter
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

try:
    import blackboxprotobuf
except ImportError:
    os.system("pip install blackboxprotobuf -q")
    import blackboxprotobuf

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ============================================================
# URLS
# ============================================================
URL_GUEST_REGISTER = "https://ffmconnect.live.gop.garenanow.com/api/v2/oauth/guest:register"
URL_TOKEN_GRANT    = "https://ffmconnect.live.gop.garenanow.com/api/v2/oauth/guest/token:grant"
URL_MAJOR_LOGIN    = "https://loginbp.ppmainecoonghj.com/MajorLogin"
URL_MAJOR_REGISTER = "https://loginbp.ppmainecoonghj.com/MajorRegister"
URL_NEWBIE_CHOICE  = "https://loginbp.ppmainecoonghj.com/ChooseNewbieChoice"

CLIENT_URLS = {
    "IND": "https://client.ind.freefiremobile.com/",
    "ID":  "https://clientbp.ggblueshark.com/",
    "BR":  "https://client.us.freefiremobile.com/",
    "ME":  "https://clientbp.common.ggbluefox.com/",
    "VN":  "https://clientbp.ggblueshark.com/",
    "TH":  "https://clientbp.common.ggbluefox.com/",
    "RU":  "https://clientbp.ggblueshark.com/",
    "BD":  "https://clientbp.ggblueshark.com/",
    "PK":  "https://clientbp.ggblueshark.com/",
    "NA":  "https://client.us.freefiremobile.com/",
    "SAC": "https://client.us.freefiremobile.com/",
    "EU":  "https://clientbp.ggblueshark.com/",
    "TW":  "https://clientbp.ggblueshark.com/",
}

# ============================================================
# CONSTANTS
# ============================================================
MAIN_KEY = bytes.fromhex(
    '326565343438313965396234353938383435313431303637'
    '6232383136323138373464306435643761663964386637653030'
    '6331653534373135623764316533'
)
AES_KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
AES_IV  = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
APP_ID        = 100067
RELEASE_VER   = "OB55"
GAME_VERSION  = "2.132.4"

# ============================================================
# TUNING
# ============================================================
HTTP_TIMEOUT  = (5, 15)
FAIL_WAIT     = 0.3
MAX_RETRIES   = 3
POOL_CONN     = 100
POOL_MAX      = 200
PACE_PER_PROXY = 0.3
PROXY_COOLDOWN_429 = 20
PROXY_COOLDOWN_503 = 45

# ============================================================
# RANDOM IP POOL
# ============================================================
INDIAN_IPS = [
    "49.36.180.10", "49.36.180.22", "49.36.181.15", "49.36.182.45",
    "103.87.24.10", "103.87.24.25", "103.87.25.14", "103.87.25.30",
    "115.99.10.20", "115.99.10.35", "115.99.11.40", "115.99.11.55",
    "49.36.83.10", "49.36.83.22", "49.36.84.15", "49.36.84.30",
    "103.25.12.10", "103.25.12.25", "103.25.13.14", "103.25.13.30",
    "115.99.20.10", "115.99.20.22", "115.99.21.15", "115.99.21.30",
    "49.36.100.10", "49.36.100.22", "49.36.101.15", "49.36.101.30",
    "103.56.12.10", "103.56.12.25", "103.56.13.14", "103.56.13.30",
    "49.36.120.10", "49.36.120.22", "49.36.121.15", "49.36.121.30",
    "49.36.140.10", "49.36.140.22", "49.36.141.15", "49.36.141.30",
    "49.36.160.10", "49.36.160.22", "49.36.161.15", "49.36.161.30",
    "49.36.200.10", "49.36.200.22", "49.36.201.15", "49.36.201.30",
]

DEVICES = [
    ("Asus ASUS_AI2501_B", "Android OS 12 / API-31 (SP1A.210812.016.C2/user.dxu.20260701.180839)", "Adreno (TM) 640", "OpenGL ES 3.2"),
    ("Redmi Note 12 Pro",  "Android OS 13 / API-33 (TP1A.220624.014)", "Adreno (TM) 618", "OpenGL ES 3.2"),
    ("Samsung SM-M135F",   "Android OS 13 / API-33 (TP1A.220624.014)", "Mali-G68", "OpenGL ES 3.2"),
    ("Realme RMX3630",     "Android OS 12 / API-31 (SP1A.210812.016)", "Adreno (TM) 610", "OpenGL ES 3.2"),
    ("Vivo V2149",         "Android OS 13 / API-33 (TP1A.220624.014)", "Adreno (TM) 642L", "OpenGL ES 3.2"),
    ("OnePlus CPH2411",    "Android OS 13 / API-33 (TP1A.220624.014)", "Adreno (TM) 730", "OpenGL ES 3.2"),
    ("Poco M4 Pro 5G",     "Android OS 12 / API-31 (SP1A.210812.016)", "Mali-G57 MC2", "OpenGL ES 3.2"),
    ("iQOO I2012",         "Android OS 13 / API-33 (TP1A.220624.014)", "Adreno (TM) 650", "OpenGL ES 3.2"),
    ("Oppo CPH2477",       "Android OS 13 / API-33 (TP1A.220624.014)", "Adreno (TM) 619", "OpenGL ES 3.2"),
    ("Tecno KI8",          "Android OS 13 / API-33 (TP1A.220624.014)", "Mali-G57", "OpenGL ES 3.2"),
    ("Infinix X6819",      "Android OS 12 / API-31 (SP1A.210812.016)", "Mali-G52 MC2", "OpenGL ES 3.2"),
    ("Motorola moto g73 5G","Android OS 13 / API-33 (TP1A.220624.014)", "Adreno (TM) 619", "OpenGL ES 3.2"),
]

# ============================================================
# GLOBALS
# ============================================================
PROXIES = []
PROXY_COOLDOWN = {}
CURRENT_PROXY = None
PROXY_LOCK = threading.Lock()
PACE_LOCK = {}
LAST_PACE = {}

# ============================================================
# PROXY
# ============================================================
def load_proxies():
    global PROXIES, CURRENT_PROXY
    PROXIES = []
    pf = "working_proxies.txt"
    if not os.path.exists(pf):
        PROXIES = [None]; CURRENT_PROXY = None
        return
    with open(pf, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                PROXIES.append({"http": line, "https": line})
    if not PROXIES:
        PROXIES = [None]; CURRENT_PROXY = None
    else:
        CURRENT_PROXY = PROXIES[0]

def _pk(p):
    if p is None: return "__direct__"
    return p.get("http", "?")

def get_proxy():
    global CURRENT_PROXY
    if len(PROXIES) <= 1:
        return PROXIES[0] if PROXIES else None
    if CURRENT_PROXY is not None:
        with PROXY_LOCK:
            if time.time() >= PROXY_COOLDOWN.get(_pk(CURRENT_PROXY), 0):
                return CURRENT_PROXY
    now = time.time()
    with PROXY_LOCK:
        healthy = [p for p in PROXIES if now >= PROXY_COOLDOWN.get(_pk(p), 0)]
        if healthy: return random.choice(healthy)
        return random.choice(PROXIES)

def cooldown(p, sec):
    if p is None: return
    with PROXY_LOCK:
        k = _pk(p)
        PROXY_COOLDOWN[k] = max(PROXY_COOLDOWN.get(k, 0), time.time() + sec)

def pace_proxy(p):
    k = _pk(p)
    if k not in PACE_LOCK:
        PACE_LOCK[k] = threading.Lock()
    with PACE_LOCK[k]:
        now = time.time()
        el = now - LAST_PACE.get(k, 0)
        if el < PACE_PER_PROXY:
            time.sleep(PACE_PER_PROXY - el)
        LAST_PACE[k] = time.time()

# ============================================================
# PASSWORD
# ============================================================
def gen_password():
    return hashlib.sha256(
        ''.join(random.choice(string.ascii_letters + string.digits)
                for _ in range(32)).encode()
    ).hexdigest().upper()

# ============================================================
# NICKNAME
# ============================================================
def gen_nickname(prefix="FF", max_len=12):
    avail = max_len - len(prefix)
    if avail < 1:
        return prefix[:max_len].encode()
    digits = "".join(random.choice("0123456789") for _ in range(avail))
    return f"{prefix}{digits}".encode()

# ============================================================
# CRYPTO
# ============================================================
def enc_aes(data):
    return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(data, AES.block_size))

def encode_f14(s):
    ks = [0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,
          0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,
          0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,
          0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30]
    return bytes(ord(c) ^ ks[i % len(ks)] for i, c in enumerate(s))

# ============================================================
# TYPEDEFS
# ============================================================
def _tf(t): return {'type': t, 'name': ''}

typedef_login = {
    '3':_tf('bytes'),'4':_tf('bytes'),'5':_tf('int'),
    '7':_tf('bytes'),'8':_tf('bytes'),'9':_tf('bytes'),
    '10':_tf('bytes'),'11':_tf('bytes'),'12':_tf('int'),
    '13':_tf('int'),'14':_tf('bytes'),'15':_tf('bytes'),
    '16':_tf('int'),'17':_tf('bytes'),'18':_tf('bytes'),
    '19':_tf('bytes'),'20':_tf('bytes'),'21':_tf('bytes'),
    '22':_tf('bytes'),'23':_tf('bytes'),'24':_tf('bytes'),
    '25':_tf('bytes'),'26':_tf('bytes'),'29':_tf('bytes'),
    '30':_tf('int'),'41':_tf('bytes'),'42':_tf('bytes'),
    '57':_tf('bytes'),'60':_tf('int'),'61':_tf('int'),
    '62':_tf('int'),'63':_tf('int'),'64':_tf('int'),
    '65':_tf('int'),'66':_tf('int'),'67':_tf('int'),
    '73':_tf('int'),'74':_tf('bytes'),'76':_tf('int'),
    '77':_tf('bytes'),'78':_tf('int'),'79':_tf('int'),
    '81':_tf('bytes'),'83':_tf('bytes'),'85':_tf('int'),
    '86':_tf('bytes'),'87':_tf('int'),'88':_tf('int'),
    '92':_tf('int'),'93':_tf('bytes'),'94':_tf('bytes'),
    '96':_tf('bytes'),'97':_tf('int'),'98':_tf('int'),
    '99':_tf('bytes'),'100':_tf('bytes'),'102':_tf('bytes'),
    '104':_tf('int'),'105':_tf('int'),'106':_tf('bytes'),
    '107':_tf('bytes'),
}
typedef_reg = {
    '1':_tf('bytes'),'2':_tf('bytes'),'3':_tf('bytes'),
    '5':_tf('int'),'6':_tf('int'),'7':_tf('int'),
    '13':_tf('int'),'14':_tf('bytes'),'15':_tf('bytes'),
    '16':_tf('int'),'20':_tf('bytes'),'21':_tf('int'),
    '22':_tf('bytes'),
}
typedef_newbie = {'1':_tf('int'),'2':_tf('int'),'3':_tf('int')}

FIELD_22 = bytes.fromhex(
    "4747524501010100620200001052aa0d669c6a368f08338060d2ee0690053af84a41edcd3558556ec10f24f4"
    "6c93ac64ca41a16732c46a2cb071246a79b8929032f9e1b6f4ef331bd53cabf29b09b97349a46e9863c0314e"
    "1a0d80819fef8aabf03876b3d037db354a7ccb5c1bce96411fb3753f6f50e44c69c4ed617fa30efb8ffc0517"
    "ff2f636739be1f304d999cfd6fd48bf69454199794c3dc88f55a4bdbd66534d5a061359cdfd1fb680cd37918"
    "df9fdb3cf7d80067b0a3506c90063cf62b2ccec11e23913a2fd7c4ef091331967bb518a5ad1e551146b90821"
    "be800883abadde39d6c80a5d798611466c748f075481806c5842ce45e6bd4e3368ec08fe2ec41ceb880cd862"
    "49eb71693f79f0bccf9e590c3fae12519fe08c7a1905d0927690109e0df28574bb14847225db1a59230e6662"
    "ed7730e15ff9a6c815cb41b420edeada735a4b03e181037c37c2c850257311df2f07b0a56e759372cbd0268e"
    "3f13a292ee4373e38ab5096e0342a5e0d7fec6da2bbc265d74baadd2b24ee4f74862f82c21d6694bac53f8ce"
    "80312a30068a6276a641c19b11d0305c6fe2f531ac7de578b29f543697f5c73663e6f23aa15277b6122dcd4d"
    "4171e38f9ac0b173f39c58416a16c5c1f4a35acd065ce78f449cf538a249339e763272d458e4ed86c976591a"
    "9c066b3a37111e44091eb6b5a795249f3e5145db022a6055f2cc675936391312f688f89627845df222a91156"
    "555225be36f9714a0ba50246d0f003bda3c9c1292ab73b4f79635ddd023218eda93a302d79e023404c143965"
    "44a930b98ed54771aca7fec10d095587685b473e81a9619764fad9256529dcd6e911f4f4629612287d4ee3ec"
    "5389f6ec4ec020b0e2aac017232a9197be9e46239ce690fe5d4872b2e98e651510c971667f3aca8b59f3e9d5"
    "0e43"
)

# ============================================================
# HEADERS
# ============================================================
HEADERS_MSDK = {
    "User-Agent": "GarenaMSDK/4.0.44(ASUS_AI2501_B ;Android 12;en;US;app 2.132.1 2019118525;)",
    "Content-Type": "application/json; charset=utf-8",
    "Connection": "keep-alive",
}
HEADERS_LOGINBP = {
    'Host': 'loginbp.ppmainecoonghj.com',
    'User-Agent': 'UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
    'Accept': '*/*', 'Accept-Encoding': 'deflate, gzip',
    'Authorization': 'Bearer', 'X-GA': 'v1 1',
    'ReleaseVersion': RELEASE_VER,
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Unity-Version': '2018.4.12f1',
}

# ============================================================
# SESSION
# ============================================================
_tl = threading.local()

def get_session():
    s = getattr(_tl, "s", None)
    if s: return s
    s = requests.Session()
    a = HTTPAdapter(pool_connections=POOL_CONN, pool_maxsize=POOL_MAX, max_retries=0)
    s.mount("https://", a); s.mount("http://", a)
    _tl.s = s
    return s

# ============================================================
# LOGIN META
# ============================================================
def _build_login_meta(open_id, access_token):
    ip = random.choice(INDIAN_IPS)
    model, os_str, gpu, gpu_full = random.choice(DEVICES)

    return {
        '3': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S').encode(),
        '4': b'free fire', '5': 1, '7': GAME_VERSION.encode(),
        '8': os_str.encode(),
        '9': b'Handheld', '10': b'Jio', '11': b'WIFI',
        '12': 1280, '13': 720, '14': b'240',
        '15': b'x86-64 SSE3 SSE4.1 SSE4.2 AVX AVX2 | 2400 | 4',
        '16': random.choice([5951, 6000, 6100, 5500]),
        '17': gpu.encode(),
        '18': gpu_full.encode(),
        '19': f'Google|{uuid.uuid4()}'.encode(),
        '20': ip.encode(),
        '21': b'en', '22': open_id.encode(),
        '23': b'4', '24': b'Handheld',
        '25': model.encode(),
        '26': b'IND',
        '29': access_token.encode(), '30': 1,
        '41': b'Jio', '42': b'WIFI',
        '57': b'1ac4b80ecf0478a44203bf8fac6120f5',
        '60': 30000, '61': 30000, '62': 2519, '63': 243,
        '64': 32357, '65': 34308, '66': 32357, '67': 34308, '73': 1,
        '74': b'/data/app/~~iw-K-GR3srU7dLE-UxJ4bg==/com.dts.freefiremax-kbPhw3SUYautW0I_oayB_A==/lib/arm',
        '76': 2,
        '77': b'428775ab8c8845bd341b5357ec61d15e|/data/app/~~iw-K-GR3srU7dLE-UxJ4bg==/com.dts.freefiremax-kbPhw3SUYautW0I_oayB_A==/base.apk',
        '78': 2, '79': 1, '81': b'32', '83': b'2019118525', '85': 3,
        '86': b'OpenGLES3', '87': 4095, '88': 4,
        '92': random.choice([19788, 20000, 21000]),
        '93': b'android_max',
        '94': b'KqsHT2gyPt7vUCc9SCjv2ioi3WEZSEL86ErvXB38suVVK/Z4IVt78ESl/r2S15C1pqu/j6ZmgFL7HbwoFiiVconX08ooKiisQffvEAPCo/C+Lahr',
        '96': b'{"cur_rate":null,"support_etc2":true}',
        '97': 1, '98': 1, '99': b'4', '100': b'4', '102': b'',
        '104': 77149, '105': 1,
        '106': b'https://dl.cdn.freefiremobile.com/live/ABHotUpdates/|https://dl-core.cdn.freefiremobile.com/live/ABHotUpdates/|6b2078db9d22dd98f8e9386a39af8462',
        '107': b'c8e41b7a93f02d56e1a94c7b8203f5d1',
    }

# ============================================================
# ==============  ACTIVATOR  =================================
# ============================================================
def _extract_jwt(resp_text):
    try:
        idx = resp_text.find("eyJhbGci")
        if idx == -1:
            return None
        token = resp_text[idx:]
        dot2 = token.find(".", token.find(".") + 1)
        if dot2 != -1:
            token = token[:dot2 + 44]
        return token
    except Exception:
        return None

def _build_final_payload(jwt, access_token):
    try:
        tp = jwt.split('.')[1]
        tp += '=' * ((4 - len(tp) % 4) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(tp).decode('utf-8'))
        external_id = decoded.get('external_id', '')
        signature_md5 = decoded.get('signature_md5', '')
        now = str(datetime.now())[:len(str(datetime.now())) - 7]

        PAYLOAD = b':\x071.111.2\xaa\x01\x02ar\xb2\x01 55ed759fcf94f85813e57b2ec8492f5c\xba\x01\x014\xea\x01@6fb7fdef8658fd03174ed551e82b71b21db8187fa0612c8eaf1b63aa687f1eae\x9a\x06\x014\xa2\x06\x014'
        PAYLOAD = PAYLOAD.replace(b"2023-12-24 04:21:34", str(now).encode())
        PAYLOAD = PAYLOAD.replace(
            b"15f5ba1de5234a2e73cc65b6f34ce4b299db1af616dd1dd8a6f31b147230e5b6",
            access_token.encode()
        )
        PAYLOAD = PAYLOAD.replace(
            b"4666ecda0003f1809655a7a8698573d0",
            external_id.encode()
        )
        PAYLOAD = PAYLOAD.replace(
            b"7428b253defc164018c604a1ebbfebdf",
            signature_md5.encode()
        )

        encrypted = AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(
            pad(PAYLOAD, AES.block_size)
        )
        return encrypted
    except Exception:
        return None

def _get_login_data(jwt, payload, region, session, proxy):
    link = CLIENT_URLS.get(region.upper(), "https://clientbp.ggblueshark.com/")
    url = f"{link}GetLoginData"

    headers = {
        'Expect': '100-continue',
        'Authorization': f'Bearer {jwt}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB55',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; G011A Build/PI)',
        'Connection': 'close',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    for _ in range(3):
        try:
            r = session.post(url, headers=headers, data=payload,
                             verify=False, proxies=proxy, timeout=20)
            if r.status_code == 200 and len(r.content) > 0:
                return r.content
        except requests.RequestException:
            time.sleep(1.5)
    return None

def activate_account(access_token, open_id, region, session, proxy):
    try:
        lang_map = {"IND":"hi","BD":"bn","PK":"ur","ID":"id","ME":"ar",
                    "TH":"th","VN":"vi","RU":"ru","TW":"zh","BR":"pt","SAC":"es"}
        lang = lang_map.get(region.upper(), "en")

        # --- Step 1: MajorLogin ---
        payload_parts = [
            b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02',
            lang.encode("ascii"),
            b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118693\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
        ]
        raw = b''.join(payload_parts)
        raw = raw.replace(
            b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390',
            access_token.encode()
        )
        raw = raw.replace(
            b'1d8ec0240ede109973f3321b9354b44d',
            open_id.encode()
        )

        enc = enc_aes(raw)

        login_headers = {
            'User-Agent': "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            'Accept-Encoding': "deflate, gzip",
            'X-GA-SV': str(int(time.time())),
            'Authorization': "Bearer",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB55",
            'Content-Type': "application/x-www-form-urlencoded",
            'X-Unity-Version': "2018.4.12f1",
            'Host': "loginbp.ppmainecoonghj.com",
        }

        r = session.post(URL_MAJOR_LOGIN, headers=login_headers, data=enc,
                         verify=False, proxies=proxy, timeout=15)

        if r.status_code != 200 or len(r.text) < 10:
            return None

        jwt = _extract_jwt(r.text)
        if not jwt:
            return None

        final_payload = _build_final_payload(jwt, access_token)
        if not final_payload:
            return None

        gld = _get_login_data(jwt, final_payload, region, session, proxy)
        if not gld:
            return None

        return {"jwt_token": jwt, "status": "full_login"}

    except Exception:
        return None

# ============================================================
# REGISTER ONE (same as executor)
# ============================================================
def register_one(worker_id, nick_prefix="FF", nick_max_len=12, region="IND", do_activate=True):
    session = get_session()
    proxy = get_proxy()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            pace_proxy(proxy)

            # 1. GUEST REGISTER
            password = gen_password()
            reg_body = json.dumps(
                {"app_id": APP_ID, "client_type": 2, "password": password, "source": 2},
                separators=(",", ":")
            )
            reg_sig = hmac.new(MAIN_KEY, reg_body.encode(), hashlib.sha256).hexdigest()

            r = session.post(URL_GUEST_REGISTER,
                             headers={**HEADERS_MSDK, "Authorization": "Signature " + reg_sig},
                             data=reg_body, verify=False, proxies=proxy,
                             timeout=HTTP_TIMEOUT)

            if r.status_code == 429:
                cooldown(proxy, PROXY_COOLDOWN_429); proxy = get_proxy(); continue
            if r.status_code == 503:
                cooldown(proxy, PROXY_COOLDOWN_503); proxy = get_proxy(); continue
            if r.status_code != 200:
                raise Exception(f"reg HTTP {r.status_code}")

            uid = r.json()["data"]["uid"]

            # 2. TOKEN GRANT
            dev_id = f"02-{uuid.uuid4()}"
            grant_body = {
                "client_id": APP_ID, "client_secret": CLIENT_SECRET,
                "client_type": 2, "device_id": dev_id, "password": password,
                "response_type": "token", "uid": int(uid),
            }
            r2 = session.post(URL_TOKEN_GRANT, headers=HEADERS_MSDK,
                              json=grant_body, verify=False, proxies=proxy,
                              timeout=HTTP_TIMEOUT)
            if r2.status_code != 200:
                raise Exception(f"grant HTTP {r2.status_code}")
            gd = r2.json()["data"]
            access_token = gd["access_token"]
            open_id      = gd["open_id"]

            # 3. MAJOR LOGIN #1
            hdr = dict(HEADERS_LOGINBP)
            hdr["X-GA-SV"] = str(int(time.time()))
            login_meta = _build_login_meta(open_id, access_token)
            try:
                session.post(URL_MAJOR_LOGIN, headers=hdr,
                             data=enc_aes(blackboxprotobuf.encode_message(login_meta, typedef_login)),
                             verify=False, proxies=proxy, timeout=HTTP_TIMEOUT)
            except Exception:
                pass

            # 4. NICKNAME
            nick = gen_nickname(nick_prefix, nick_max_len)

            # 5. MAJOR REGISTER
            reg_msg = {
                '1': nick, '2': access_token.encode(), '3': open_id.encode(),
                '5': 102000007, '6': 4, '7': 1, '13': 1,
                '14': encode_f14(open_id), '15': b'en', '16': 2,
                '20': GAME_VERSION.encode(), '21': 1, '22': FIELD_22,
            }
            rr = session.post(URL_MAJOR_REGISTER, headers=hdr,
                              data=enc_aes(blackboxprotobuf.encode_message(reg_msg, typedef_reg)),
                              verify=False, proxies=proxy, timeout=HTTP_TIMEOUT)

            if rr.status_code != 200:
                raise Exception(f"majorreg HTTP {rr.status_code}: {rr.text[:100]}")

            res, _ = blackboxprotobuf.decode_message(rr.content)
            account_id = None
            if isinstance(res, dict):
                account_id = res.get('3') or res.get(b'3')
            if not account_id:
                raise Exception("no account_id")

            # 6. NEWBIE
            try:
                session.post(URL_NEWBIE_CHOICE, headers=hdr,
                             data=enc_aes(blackboxprotobuf.encode_message(
                                 {'1': int(account_id), '2': 2, '3': 3}, typedef_newbie)),
                             verify=False, proxies=proxy, timeout=HTTP_TIMEOUT)
            except Exception:
                pass

            # 7. ACTIVATOR
            activated = None
            if do_activate:
                activated = activate_account(access_token, open_id,
                                             region, session, proxy)

            nick_str = nick.decode('utf-8', errors='ignore')

            if activated:
                return {
                    "uid":        str(uid),
                    "password":   str(password),
                    "name":       nick_str,
                    "account_id": str(account_id),
                    "region":     region,
                    "status":     "full_login",
                    "jwt_token":  activated.get("jwt_token", ""),
                }
            else:
                return {
                    "uid":        str(uid),
                    "password":   str(password),
                    "name":       nick_str,
                    "account_id": str(account_id),
                    "region":     region,
                    "status":     "registered",
                    "jwt_token":  "",
                }

        except requests.exceptions.Timeout:
            time.sleep(FAIL_WAIT)
        except requests.exceptions.ProxyError:
            cooldown(proxy, 30); proxy = get_proxy()
        except Exception:
            time.sleep(FAIL_WAIT)

    return None

# ============================================================
# FLASK API ENDPOINTS
# ============================================================
@app.route('/')
def home():
    return jsonify({
        "name": "RISHANT X EXECUTOR API",
        "version": "1.0",
        "endpoints": {
            "/gen": "Generate accounts. Params: count, threads, name, region, activate, max_len",
            "/health": "Health check"
        },
        "regions": list(CLIENT_URLS.keys()),
        "max_count": 50,
        "max_threads": 50,
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "time": datetime.now().isoformat()})

@app.route('/gen', methods=['GET', 'POST'])
def generate():
    """
    GET /gen?count=10&threads=10&name=FF&region=IND&activate=y&max_len=12
    POST /gen  { "count": 10, "threads": 10, "name": "FF", "region": "IND", "activate": true, "max_len": 12 }
    """
    # ---- Parse params ----
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        args = {**request.args.to_dict(), **data}
    else:
        args = request.args.to_dict()

    try:
        count = int(args.get('count', 1))
        count = max(1, min(count, 50))
    except Exception:
        count = 1

    try:
        threads = int(args.get('threads', 5))
        threads = max(1, min(threads, 50))
    except Exception:
        threads = 5

    nick_prefix = str(args.get('name', 'FF'))[:8] or 'FF'

    try:
        max_len = int(args.get('max_len', 12))
        max_len = max(4, min(max_len, 12))
    except Exception:
        max_len = 12

    region = str(args.get('region', 'IND')).upper()
    if region not in CLIENT_URLS:
        region = "IND"

    activate_raw = args.get('activate', 'y')
    if isinstance(activate_raw, bool):
        do_activate = activate_raw
    else:
        do_activate = str(activate_raw).lower() in ('y', 'yes', 'true', '1', 'on')

    # ---- Load proxies (per request) ----
    load_proxies()

    start = time.time()
    results = []
    full_login_count = 0
    reg_only_count = 0

    # ---- Run with ThreadPoolExecutor ----
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(register_one, i + 1, nick_prefix, max_len, region, do_activate): i
                   for i in range(count)}
        for fut in as_completed(futures):
            try:
                r = fut.result()
                if r:
                    results.append(r)
                    if r.get("status") == "full_login":
                        full_login_count += 1
                    else:
                        reg_only_count += 1
            except Exception:
                pass

    elapsed = round(time.time() - start, 2)
    rate = round(len(results) / max(elapsed, 0.01) * 60, 1)

    return jsonify({
        "success": True,
        "requested": count,
        "created": len(results),
        "full_login": full_login_count,
        "registered_only": reg_only_count,
        "threads": threads,
        "region": region,
        "activate": do_activate,
        "elapsed_seconds": elapsed,
        "rate_per_min": rate,
        "accounts": results,
    })

# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("  RISHANT X EXECUTOR — API SERVER")
    print("=" * 60)
    print("  GET  /gen?count=10&threads=10&name=FF&region=IND&activate=y")
    print("  POST /gen   (JSON body same params)")
    print("=" * 60)
    app.run(host='0.0.0.0', port=3000, debug=False, threaded=True)
