"""기업마당·K-Startup 공식 API에서 공고를 받아 data/raw/YYYY-MM-DD.json 으로 저장한다.
판단은 하지 않는다. 판단·캘린더 등록·대시보드 갱신은 평일 9시 Claude 실행이 맡는다.
인증키는 GitHub Secrets(BIZINFO_API_KEY, DATA_GO_KR_API_KEY)에서 읽는다. 키가 없으면 해당 수집처를 건너뛴다."""
import json, os, sys, datetime, urllib.parse, urllib.request

KST = datetime.timezone(datetime.timedelta(hours=9))
today = datetime.datetime.now(KST).strftime("%Y-%m-%d")
out = {"collected_at": datetime.datetime.now(KST).isoformat(timespec="minutes"), "sources": {}}

def get(url, params):
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params, safe="[]:"),
                                 headers={"User-Agent": "gov-support-agent/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

# 1. 기업마당 지원사업정보 API
key = os.environ.get("BIZINFO_API_KEY", "").strip()
if key:
    try:
        d = get("https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do",
                {"crtfcKey": key, "dataType": "json", "searchCnt": "500"})
        items = d.get("jsonArray", d)
        out["sources"]["bizinfo"] = {"ok": True, "count": len(items) if isinstance(items, list) else None, "items": items}
    except Exception as e:
        out["sources"]["bizinfo"] = {"ok": False, "error": str(e)[:300]}
else:
    out["sources"]["bizinfo"] = {"ok": False, "error": "BIZINFO_API_KEY 없음"}

# 2. K-Startup 사업공고 API (공공데이터포털 15125364), 모집 중인 공고만
key = os.environ.get("DATA_GO_KR_API_KEY", "").strip()
if key:
    try:
        items, page = [], 1
        while page <= 10:
            d = get("https://apis.data.go.kr/B552735/kisedKstartupService01/getAnnouncementInformation01",
                    {"serviceKey": key, "page": page, "perPage": 100, "returnType": "json",
                     "cond[rcrt_prgs_yn::EQ]": "Y"})
            batch = d.get("data", [])
            items += batch
            if len(batch) < 100:
                break
            page += 1
        out["sources"]["kstartup"] = {"ok": True, "count": len(items), "items": items}
    except Exception as e:
        out["sources"]["kstartup"] = {"ok": False, "error": str(e)[:300]}
else:
    out["sources"]["kstartup"] = {"ok": False, "error": "DATA_GO_KR_API_KEY 없음"}

os.makedirs("data/raw", exist_ok=True)
path = f"data/raw/{today}.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
for k, v in out["sources"].items():
    print(k, "ok" if v["ok"] else "fail", v.get("count", v.get("error")))
print("saved", path)
