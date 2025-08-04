import re, html, requests
from config.settings import STATUS_MAPPING

# Helper function để tránh lặp code
def _make_request(url, method='get', **kwargs):
    print(f"  🔗 Requesting URL: {url}")
    try:
        if method == 'post':
            response = requests.post(url, timeout=20, **kwargs)
        else:
            response = requests.get(url, timeout=20, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request failed: {e}")
        return None

def scrape_japanpost(no: str) -> str:
    print(f"   scraping Japan Post...")
    kind = "S004" if re.match(r"^[A-Za-z]{2}\d{9}JP$", no) else "S002"
    url = f"https://trackings.post.japanpost.jp/services/srv/search/direct?reqCodeNo1={no}&searchKind={kind}&locale=ja"
    
    r = _make_request(url)
    if not r: return "Không tìm thấy mã vận đơn này"

    tbl = re.search(r'<table[^>]*summary="履歴情報"[^>]*>(.*?)</table>', r.text, re.DOTALL)
    if not tbl:
        print("  ❌ Could not find status table on page.")
        return "Không tìm thấy mã vận đơn này"

    sts = re.findall(r'<td[^>]*class="w_150"[^>]*>(.*?)</td>', tbl.group(1), re.DOTALL)
    clean = [re.sub(r"<[^>]+>", "", s).strip() for s in sts]
    
    if not clean:
        print("  ❌ Found table, but no status entries inside.")
        return "Không tìm thấy mã vận đơn này"
    
    original_status = clean[-1]
    print(f"  ✅ Found raw status: '{original_status}'")
    return STATUS_MAPPING.get(original_status, original_status)

def scrape_yamato(no: str) -> str:
    print(f"  scraping Yamato...")
    url = "https://toi.kuronekoyamato.co.jp/cgi-bin/tneko"
    
    r = _make_request(url, method='post', data={"number01": no})
    if not r: return "Lỗi kết nối"

    m = re.search(r'<h4[^>]*class="tracking-invoice-block-state-title"[^>]*>(.*?)</h4>', r.text, re.DOTALL)
    if not m:
        print("  ❌ Could not find status element on page.")
        return "Sai mã bưu điện"
    
    original_status = m.group(1).strip()
    print(f"  ✅ Found raw status: '{original_status}'")
    return STATUS_MAPPING.get(original_status, original_status)

def scrape_sagawa(no: str) -> str:
    print(f"  scraping Sagawa...")
    url = f"https://k2k.sagawa-exp.co.jp/p/web/okurijosearch.do?okurijoNo={no}"

    r = _make_request(url)
    if not r: return "Lỗi kết nối"
    
    r.encoding = "cp932"
    m = re.search(r'<span class="state">([^<]+)', r.text)
    
    if not m:
        print("  ❌ Could not find status element on page.")
        return "Sai mã bưu điện"
    
    original_status = html.unescape(m.group(1).strip())
    print(f"  ✅ Found raw status: '{original_status}'")
    return STATUS_MAPPING.get(original_status, original_status)
