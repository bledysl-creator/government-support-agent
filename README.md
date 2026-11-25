# 정부지원사업 알림 에이전트

서울·경기 의료기기 SW 소기업(2018년 설립)에 맞는 정부지원사업 공고를 매일 찾아 정리합니다. 알림 전용이며 신청은 하지 않습니다.

- 대시보드: `index.html` (GitHub Pages)
- 판단 규칙: [`agent/CLAUDE.md`](agent/CLAUDE.md)
- 평일 08:40 GitHub Actions가 기업마당·K-Startup 공식 API로 원자료를 받아 `data/raw/`에 저장
- 평일 09:00 Claude가 원자료와 웹 공고를 판단해 구글 캘린더, `notices.json`, `data/seen_notices.json`, `data/run_log.md`를 갱신

## 필요한 Secrets (Settings → Secrets and variables → Actions)
- `BIZINFO_API_KEY`: 기업마당 API 인증키
- `DATA_GO_KR_API_KEY`: 공공데이터포털 K-Startup 조회서비스 인증키 (일반 인증키, Decoding)
