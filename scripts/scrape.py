"""API가 없거나 화면이 스크립트로 그려지는 기관 공고 게시판을 실제 브라우저(Playwright)로 열어
목록의 링크와 본문 텍스트를 data/raw/YYYY-MM-DD-web.json 으로 저장한다. 판단은 하지 않는다.
GitHub Actions(해외 GitHub 서버)에서 실행된다."""
import json, os, datetime, sys
from playwright.sync_api import sync_playwright

KST = datetime.timezone(datetime.timedelta(hours=9))
today = datetime.datetime.now(KST).strftime("%Y-%m-%d")

# 수집처: 공고 목록 페이지 (앞에서부터 시도, 첫 성공만 사용)
SOURCES = {
    "기업마당":       ["https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do"],
    "중소벤처기업부": ["https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=310"],
    "경기도":         ["https://www.gg.go.kr/bbs/board.do?bsIdx=469&menuId=1547", "https://www.gg.go.kr/"],
    "GBSA":           ["https://www.gbsa.or.kr/board/bbs_list.do?code=notice", "https://www.gbsa.or.kr/"],
    "경기테크노파크": ["https://pms.gtp.or.kr/web/business/webBusinessList.do", "https://www.gtp.or.kr/"],
    "고용노동부":     ["https://www.moel.go.kr/news/notice/noticeList.do"],
    "고용24":         ["https://www.work24.go.kr/cm/e/a/0110/selectOpenNoticeList.do", "https://www.work24.go.kr/"],
    "KHIDI":          ["https://www.khidi.or.kr/board?menuId=MENU01108", "https://www.khidi.or.kr/main"],
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
            page = ctx.new_page()
            try:
                r = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass
                links = page.eval_on_selector_all("a", "els => els.map(a => ({t: (a.innerText||'').trim().replace(/\\s+/g,' '), h: a.href})).filter(x => x.t.length >= 8)")
                text = page.inner_text("body")[:30000]
                status = r.status if r else None
                res["tried"].append({"url": url, "status": status, "links": len(links)})
                if status and status < 400 and len(links) >= 5:
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
