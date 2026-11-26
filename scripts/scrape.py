"""API가 없거나 화면이 스크립트로 그려지는 기관 공고 게시판을 실제 브라우저(Playwright)로 열어
목록의 링크와 본문 텍스트를 data/raw/YYYY-MM-DD-web.json 으로 저장한다. 판단은 하지 않는다.
GitHub Actions(해외 GitHub 서버)에서 실행된다."""
import json, os, datetime, sys
from playwright.sync_api import sync_playwright
from html.parser import HTMLParser
from urllib.parse import urljoin


class LinkParser(HTMLParser):
    """페이지 스크립트가 브라우저 기본 기능을 덮어써서 evaluate가 실패할 때 HTML에서 직접 링크를 뽑는다."""
    def __init__(self, base):
        super().__init__(); self.base = base; self.links = []; self.text = []; self.cur = None
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.cur = {"h": urljoin(self.base, dict(attrs).get("href") or ""), "t": ""}
    def handle_endtag(self, tag):
        if tag == "a" and self.cur is not None:
            self.cur["t"] = " ".join(self.cur["t"].split())
            if len(self.cur["t"]) >= 8:
                self.links.append(self.cur)
            self.cur = None
    def handle_data(self, data):
        if self.cur is not None:
            self.cur["t"] += data
        if data.strip():
            self.text.append(data.strip())

KST = datetime.timezone(datetime.timedelta(hours=9))
today = datetime.datetime.now(KST).strftime("%Y-%m-%d")

# 수집처: 공고 목록 페이지 (앞에서부터 시도, 첫 성공만 사용)
SOURCES = {
    "기업마당":       ["https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do?rows=100&cpage=1", "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do"],
    "중소벤처기업부": ["https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=310"],
    "경기도":         ["https://www.gg.go.kr/bbs/board.do?bsIdx=469&menuId=1547", "https://www.gg.go.kr/"],
    "GBSA":           ["https://www.gbsa.or.kr/board/notice.do", "https://www.egbiz.or.kr/", "https://www.gbsa.or.kr/"],
    "경기테크노파크": ["https://pms.gtp.or.kr/web/business/webBusinessList.do", "https://www.gtp.or.kr/"],
    "고용노동부":     ["https://www.moel.go.kr/news/notice/noticeList.do"],
    "고용24":         ["https://m.work24.go.kr/cm/c/b/1100/selectBbttList.do?currentPageNo=1", "https://m.work24.go.kr/cm/main.do"],
    "고용노동부_지원제도": ["https://www.moel.go.kr/info/govsupport/govsupportcon/govSupportConList.do"],
    "KHIDI":          ["https://www.khidi.or.kr/board?menuId=MENU01108", "https://www.khidi.or.kr/main"],
    # 교육 분야 (임직원·중소기업 교육, 사업주훈련, 의료기기 규제·인허가 교육)
    "중진공_연수원":   ["https://www.kosmes.or.kr/nsh/SH/NTS/SHNTS001M0.do", "https://hrd.kosmes.or.kr/", "https://www.kosmes.or.kr/"],
    "한국산업인력공단": ["https://www.hrdkorea.or.kr/1/3/1", "https://www.hrdkorea.or.kr/"],
    "의료기기안전정보원": ["https://www.nids.or.kr/board/list.do?bbsId=notice", "https://www.nids.or.kr/"],
    "의료기기산업협회": ["https://www.kmdia.or.kr/kor/board/list.do?bbsId=notice", "https://www.kmdia.or.kr/kor/main.do", "http://www.kmdia.or.kr/", "https://www.kmdia.or.kr/"],
    "의료기기안전정보원_교육": [("https://edu.nids.or.kr/common/greeting.do", "https://www.nids.or.kr/"), ("https://edu.nids.or.kr/", "https://www.nids.or.kr/"), "http://edu.nids.or.kr/", "https://edu.nids.or.kr/main.do"],
    # 서울시·SBA: 본 사이트가 막히거나 목록이 늦게 그려져서, 서울시 경제분야 누리집의 공고·SBA 태그도 함께 시도
    "서울시":         ["https://news.seoul.go.kr/economy/archives/tag/%ea%b3%b5%ea%b3%a0", "https://www.seoul.go.kr/news/news_notice.do?bbsNo=277", "https://www.seoul.go.kr/news/news_notice.do"],
    "SBA":            ["https://www.sba.seoul.kr/Pages/ContentsMenu/Company_Support.aspx?C=6FA70790-6677-EC11-80E8-9418827691E2", "https://news.seoul.go.kr/economy/archives/tag/sba", "https://www.sba.seoul.kr/"],
}
only = set(sys.argv[1:])  # 인자로 특정 수집처만 돌릴 수 있음

out = {"collected_at": datetime.datetime.now(KST).isoformat(timespec="minutes"), "sources": {}}
with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(locale="ko-KR", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36")
    for name, urls in SOURCES.items():
        if only and name not in only:
            continue
        res = {"ok": False, "tried": []}
        for url in urls:
            url, referer = (url if isinstance(url, tuple) else (url, None))
            page = ctx.new_page()
            try:
                r = page.goto(url, wait_until="domcontentloaded", timeout=45000, referer=referer)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass
                page.wait_for_timeout(3000)  # 목록을 늦게 그리는 사이트 대비
                links = []
                for fr in page.frames:  # 프레임 안에 목록이 있는 사이트 대비
                    try:
                        links += fr.evaluate("() => Array.from(document.querySelectorAll('a')).map(a => ({t: (a.innerText||'').trim().replace(/\\s+/g,' '), h: a.href})).filter(x => x.t.length >= 8)")
                    except Exception:
                        pass
                links = links or None
                try:
                    text = page.evaluate("() => document.body ? document.body.innerText : ''")
                except Exception:
                    text = None
                if not links or not text:
                    lp = LinkParser(page.url); lp.feed(page.content())
                    links = links or lp.links
                    text = text or "\n".join(lp.text)
                text = (text or "")[:30000]
                status = r.status if r else None
                res["tried"].append({"url": url, "status": status, "links": len(links)})
                last = urls[-1] if not isinstance(urls[-1], tuple) else urls[-1][0]
                if status and status < 400 and len(links) >= 5 and not url.rstrip("/").endswith((".or.kr", ".go.kr")) or (status and status < 400 and url == last and len(links) >= 5):
                    res.update({"ok": True, "url": page.url, "title": page.title(), "links": links[:300], "text": text})
                    break
            except Exception as e:
                res["tried"].append({"url": url, "error": str(e)[:200]})
            finally:
                page.close()
        out["sources"][name] = res
        print(f"[{name}] {'OK' if res['ok'] else 'FAIL'} {res['tried']}")
        if res["ok"]:
            for l in res["links"][:25]:
                print("   -", l["t"][:70], "|", l["h"][:120])
    browser.close()

os.makedirs("data/raw", exist_ok=True)
with open(f"data/raw/{today}-web.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved", f"data/raw/{today}-web.json")
