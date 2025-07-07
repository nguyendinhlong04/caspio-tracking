import re, html, requests
from config.settings import STATUS_MAPPING

def scrape_japanpost(no: str) -> str:
    kind = "S004" if re.match(r"^[A-Za-z]{2}\d{9}JP$", no) else "S002"
    url = (
        "https://trackings.post.japanpost.jp/services/srv/search/direct"
        f"?reqCodeNo1={no}&searchKind={kind}&locale=ja"
    )
    r = requests.get(url, timeout=20); r.raise_for_status()
    tbl = re.search(r'<table[^>]*summary="履歴情報"[^>]*>(.*?)</table>', r.text, re.DOTALL)
    if not tbl: return ""
    sts = re.findall(r'<td[^>]*class="w_150"[^>]*>(.*?)</td>', tbl.group(1), re.DOTALL)
    clean = [re.sub(r"<[^>]+>", "", s).strip() for s in sts]
    
    if not clean:
        return ""
    
    original_status = clean[-1]
    return STATUS_MAPPING.get(original_status, original_status)

def scrape_yamato(no: str) -> str:
    r = requests.post("https://toi.kuronekoyamato.co.jp/cgi-bin/tneko",
                      data={"number01": no}, timeout=20)
    r.raise_for_status()
    m = re.search(r'<h4[^>]*class="tracking-invoice-block-state-title"[^>]*>(.*?)</h4>',
                  r.text, re.DOTALL)
    
    if not m:
        return ""
    
    original_status = m.group(1).strip()
    return STATUS_MAPPING.get(original_status, original_status)

def scrape_sagawa(no: str) -> str:
    r = requests.get(
        f"https://k2k.sagawa-exp.co.jp/p/web/okurijosearch.do?okurijoNo={no}",
        timeout=20
    )
    r.encoding = "cp932"
    m = re.search(r'<span class="state">([^<]+)', r.text)
    
    if not m:
        return ""
    
    original_status = html.unescape(m.group(1).strip())
    return STATUS_MAPPING.get(original_status, original_status)
