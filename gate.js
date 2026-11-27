/* 간단한 로그인 화면. GitHub Pages는 공개 정적 사이트라 진짜 보안은 아니고 가림막 용도다.
   계정 정보는 평문으로 두지 않고 SHA-256 해시로만 비교한다. */
(function(){
  var KEY = "gsaAuth", HASHES = ["da4c25a07e8a0293e4f493d7e12dc56d380d3d604f11fa603eec8db51c436247", "d879c6b2d898f7676d01efae52167c8e0e3a593953a957a9cc8597f2ba5efb44"];
  if (HASHES.indexOf(sessionStorage.getItem(KEY)) >= 0) return;
  document.documentElement.classList.add("locked");
  var css = document.createElement("style");
  css.textContent = [
    "html.locked body>*:not(#gate){display:none!important}",
    "#gate{position:fixed;inset:0;display:grid;place-items:center;padding:20px;background:radial-gradient(1200px 600px at 20% 0%,#1b7a47 0%,transparent 60%),linear-gradient(160deg,#14633a,#0f4d2c);font-family:'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR',-apple-system,sans-serif;z-index:9999}",
    "#gate .box{width:100%;max-width:380px;background:#fff;border-radius:22px;padding:34px 30px 26px;box-shadow:0 20px 60px rgba(0,0,0,.25)}",
    "#gate .logo{width:58px;height:58px;border-radius:16px;background:#eef8e8;display:grid;place-items:center;margin:0 auto 14px}",
    "#gate h1{margin:0;text-align:center;font-size:21px;color:#16251c}",
    "#gate p.sub{margin:6px 0 24px;text-align:center;color:#5b6b61;font-size:13.5px}",
    "#gate label{display:block;font-size:13px;font-weight:600;color:#3d4d43;margin:0 0 6px}",
    "#gate input{width:100%;box-sizing:border-box;border:1px solid #dfe8dc;border-radius:12px;padding:12px 14px;font:inherit;font-size:15px;margin-bottom:14px;background:#f8fbf6;outline:none}",
    "#gate input:focus{border-color:#3fb15f;background:#fff;box-shadow:0 0 0 3px #dff2d3}",
    "#gate button{width:100%;border:0;border-radius:12px;padding:13px;font:inherit;font-size:15px;font-weight:700;color:#fff;background:linear-gradient(135deg,#23944f,#1b7a47);cursor:pointer;margin-top:4px}",
    "#gate button:hover{filter:brightness(1.07)}",
    "#gate .remember{display:flex;align-items:center;gap:8px;font-size:13.5px;color:#3d4d43;margin:-4px 0 14px;cursor:pointer;user-select:none}",
    "#gate .remember input{width:17px;height:17px;margin:0;padding:0;accent-color:#23944f;cursor:pointer;box-shadow:none}",
    "#gate .err{min-height:20px;color:#d64535;font-size:13px;text-align:center;margin-top:10px}",
    "#gate .gh{display:flex;align-items:center;justify-content:center;gap:7px;margin-top:14px;padding-top:16px;border-top:1px solid #eef2ec;color:#8a958e;font-size:13px}"
  ].join("\n");
  document.head.appendChild(css);
  async function sha(s){ var b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s)); return Array.from(new Uint8Array(b)).map(function(x){return x.toString(16).padStart(2,"0")}).join(""); }
  function build(){
    var g = document.createElement("div"); g.id = "gate";
    g.innerHTML = '<form class="box" autocomplete="on">'
      + '<div class="logo"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#23944f" stroke-width="1.8"><path d="M12 2l2.4 6.2L21 10l-6.6 1.8L12 18l-2.4-6.2L3 10l6.6-1.8z"/><path d="M19 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/></svg></div>'
      + '<h1>정부지원사업 통합 대시보드</h1><p class="sub">로그인 후 이용할 수 있어요</p>'
      + '<label for="gId">아이디</label><input id="gId" name="username" autocomplete="username" required>'
      + '<label for="gPw">비밀번호</label><input id="gPw" name="password" type="password" autocomplete="current-password" required>'
      + '<label class="remember"><input type="checkbox" id="gSave">아이디 저장</label>'
      + '<button type="submit">로그인</button><div class="err" id="gErr"></div>'
      + '<div class="gh"><svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>Github</div>'
      + '</form>';
    document.body.appendChild(g);
    g.querySelector("form").addEventListener("submit", async function(e){
      e.preventDefault();
      var h = await sha(document.getElementById("gId").value.trim() + "\n" + document.getElementById("gPw").value);
      if (HASHES.indexOf(h) >= 0){ sessionStorage.setItem(KEY, h);
        if (document.getElementById("gSave").checked) localStorage.setItem("gsaSavedId", document.getElementById("gId").value.trim());   // 아이디만 저장, 비밀번호는 저장하지 않음
        else localStorage.removeItem("gsaSavedId"); document.documentElement.classList.remove("locked"); g.remove(); }
      else { document.getElementById("gErr").textContent = "아이디 또는 비밀번호가 맞지 않아요."; document.getElementById("gPw").value = ""; document.getElementById("gPw").focus(); }
    });
    var savedId = localStorage.getItem("gsaSavedId");
    if (savedId){ document.getElementById("gId").value = savedId; document.getElementById("gSave").checked = true; document.getElementById("gPw").focus(); }
    else document.getElementById("gId").focus();
  }
  if (document.body) build(); else document.addEventListener("DOMContentLoaded", build);
})();
window.gsaLogout = function(){ sessionStorage.removeItem("gsaAuth"); location.reload(); };
