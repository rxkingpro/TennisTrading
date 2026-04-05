import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import re

st.set_page_config(page_title="Tennis Edge", page_icon="🎾", layout="wide")

API_KEY  = "0b31349124b32d4ecc9248514616323c8b84040d2bfeb50deaf83d4bc0df3de3"
API_BASE = "https://api.api-tennis.com/tennis/"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap');
:root{--bg:#080c10;--card:#0d1117;--el:#161b22;--border:#21262d;--green:#30d158;--red:#ff453a;--amber:#ffd60a;--blue:#0a84ff;--tx:#f0f6fc;--tx2:#8b949e;--tx3:#484f58;}
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{background:var(--bg)!important;color:var(--tx)!important;font-family:'Inter',sans-serif;}
[data-testid="stHeader"]{background:transparent!important;}
::-webkit-scrollbar{width:5px;} ::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
.stTextInput input{background:var(--el)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--tx)!important;font-family:'JetBrains Mono',monospace!important;font-size:13px!important;}
div[data-baseweb="select"]>div{background:var(--el)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--tx)!important;}
.stButton>button{background:linear-gradient(135deg,#30d158,#25a244)!important;color:#000!important;font-family:'Inter',sans-serif!important;font-weight:700!important;font-size:14px!important;border:none!important;border-radius:10px!important;padding:14px 32px!important;width:100%;}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 8px 24px rgba(48,209,88,.35)!important;}
#MainMenu,footer,header{visibility:hidden!important;}
.block-container{padding-top:2rem!important;max-width:1400px!important;}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px 24px;margin-bottom:12px;}
.dt{width:100%;border-collapse:collapse;font-size:13px;}
.dt th{background:var(--el);color:var(--tx2);font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:1px;text-transform:uppercase;padding:9px 13px;border-bottom:1px solid var(--border);text-align:left;}
.dt td{padding:8px 13px;border-bottom:1px solid var(--border);color:var(--tx);}
.dt tr:hover td{background:var(--el);}
.b{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600;}
.bg{background:rgba(48,209,88,.15);color:#30d158;border:1px solid rgba(48,209,88,.3);}
.br{background:rgba(255,69,58,.15);color:#ff453a;border:1px solid rgba(255,69,58,.3);}
.ba{background:rgba(255,214,10,.15);color:#ffd60a;border:1px solid rgba(255,214,10,.3);}
.bb{background:rgba(10,132,255,.15);color:#0a84ff;border:1px solid rgba(10,132,255,.3);}
.bp{background:rgba(191,90,242,.15);color:#bf5af2;border:1px solid rgba(191,90,242,.3);}
.sl{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--tx3);margin-bottom:8px;}
.sb{height:6px;border-radius:3px;background:var(--el);overflow:hidden;}
.vb{background:linear-gradient(135deg,rgba(48,209,88,.08),rgba(48,209,88,.02));border:1px solid rgba(48,209,88,.35);border-radius:16px;padding:26px 30px;}
.vb.d{background:linear-gradient(135deg,rgba(255,69,58,.08),rgba(255,69,58,.02));border-color:rgba(255,69,58,.35);}
.vb.n{background:linear-gradient(135deg,rgba(255,214,10,.08),rgba(255,214,10,.02));border-color:rgba(255,214,10,.35);}
.hr{border:none;border-top:1px solid var(--border);margin:22px 0;}
.ht{font-family:'DM Serif Display',serif;font-size:44px;background:linear-gradient(135deg,#f0f6fc 30%,#30d158);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1;}
.hs{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:3px;color:var(--tx3);text-transform:uppercase;}
.ib{background:rgba(10,132,255,.08);border:1px solid rgba(10,132,255,.25);border-radius:10px;padding:11px 16px;font-size:13px;color:#0a84ff;margin-bottom:14px;}
</style>
""", unsafe_allow_html=True)

# ── API ───────────────────────────────────────
def api_get(params):
    params["APIkey"] = API_KEY
    try:
        r = requests.get(API_BASE, params=params, timeout=15)
        d = r.json()
        if d.get("success") == 1:
            return d.get("result", [])
        return []
    except Exception as e:
        st.error(f"Erro API: {e}")
        return []

# Cache the full ATP standings (used for player search)
@st.cache_data(ttl=3600, show_spinner=False)
def get_atp_standings():
    return api_get({"method": "get_standings", "event_type": "ATP"})

def find_player(name_query, standings):
    """Fuzzy search player from standings list."""
    q = name_query.strip().lower()
    best = None
    for p in standings:
        pn = str(p.get("player","")).lower()
        # Exact match
        if q == pn: return p
        # Last name match
        parts = pn.split()
        if parts and q == parts[-1]: best = p; break
        # Contains
        if q in pn and best is None: best = p
    return best

@st.cache_data(ttl=1800, show_spinner=False)
def get_player_detail(player_key):
    return api_get({"method": "get_players", "player_key": str(player_key)})

@st.cache_data(ttl=1800, show_spinner=False)
def get_events(player_key, days_back=200):
    date_to   = datetime.now().strftime("%Y-%m-%d")
    date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    return api_get({"method": "get_fixtures", "date_start": date_from,
                    "date_stop": date_to, "player_key": str(player_key)})

@st.cache_data(ttl=1800, show_spinner=False)
def get_h2h(k1, k2):
    return api_get({"method": "get_H2H",
                    "first_player_key": str(k1),
                    "second_player_key": str(k2)})

# ── PROCESSING ────────────────────────────────
def parse_matches(events, player_key, surface):
    matches = []
    pk = str(player_key)
    for ev in events:
        if not isinstance(ev, dict): continue
        status = str(ev.get("event_status","")).lower()
        if status not in ["finished","after penalties","aet","retired"]: continue
        fp_key = str(ev.get("first_player_key",""))
        sp_key = str(ev.get("second_player_key",""))
        is_p1 = fp_key == pk
        is_p2 = sp_key == pk
        if not is_p1 and not is_p2: continue
        winner = str(ev.get("event_winner",""))
        result = "W" if (
            (winner=="First Player" and is_p1) or
            (winner=="Second Player" and is_p2)
        ) else "L"
        opponent = str(ev.get("event_second_player","?")) if is_p1 else str(ev.get("event_first_player","?"))
        scores = ev.get("scores", [])
        score_str = " ".join([
            f"{s.get('score_first','?')}-{s.get('score_second','?')}" if is_p1
            else f"{s.get('score_second','?')}-{s.get('score_first','?')}"
            for s in scores if isinstance(s,dict)
        ])
        ev_surf = str(ev.get("surface") or "Hard").strip().capitalize()
        if ev_surf in ["","None","null"]: ev_surf = "Hard"
        matches.append({
            "date": str(ev.get("event_date",""))[:10],
            "opponent": opponent,
            "tourney": str(ev.get("tournament_name", ev.get("league_name","?"))),
            "round": str(ev.get("tournament_round","")).replace(str(ev.get("tournament_name",""))+" - ",""),
            "surface": ev_surf,
            "result": result,
            "score": score_str,
            "scores_raw": scores,
            "is_p1": is_p1,
        })
    return sorted(matches, key=lambda x: x["date"], reverse=True)

def surface_form(matches, surface, n=10):
    last = matches[:n]
    ww,wt,sw,sc = 0,0,0,0
    for m in last:
        same = m["surface"].lower()==surface.lower()
        w = 2 if same else 1
        wt += w
        if m["result"]=="W": ww+=w
        if same:
            sc+=1
            if m["result"]=="W": sw+=1
    return round(ww/wt*100,1) if wt>0 else 0.0, sw, sc

def mental(matches):
    tw,tl,seq,dw,dt = 0,0,[],0,0
    for m in matches[:20]:
        is_p1 = m.get("is_p1",True)
        res = m["result"]
        for s in m.get("scores_raw",[]):
            if not isinstance(s,dict): continue
            sf=str(s.get("score_first","")); ss=str(s.get("score_second",""))
            my,op = (sf,ss) if is_p1 else (ss,sf)
            if my=="7" and op=="6": tw+=1; seq.append("W")
            elif my=="6" and op=="7": tl+=1; seq.append("L")
        if len(m.get("scores_raw",[]))>=3:
            dt+=1
            if res=="W": dw+=1
    last3=seq[-3:]; ttb=tw+tl
    return {"tw":tw,"tl":tl,"ttb":ttb,
            "tb_pct":round(tw/ttb*100,1) if ttb>0 else 50.0,
            "last3":last3,
            "unstable":len(last3)==3 and all(r=="L" for r in last3),
            "dw":dw,"dt":dt,
            "d_pct":round(dw/dt*100,1) if dt>0 else 50.0}

def season_stats_from_detail(detail, surface):
    stats_list = detail[0].get("stats",[]) if detail else []
    cy,ly = str(datetime.now().year), str(datetime.now().year-1)
    surf_map={"Hard":("hard_won","hard_lost"),"Clay":("clay_won","clay_lost"),"Grass":("grass_won","grass_lost")}
    sw_key,sl_key=surf_map.get(surface,("hard_won","hard_lost"))
    out={"rank":None,"surf_won":0,"surf_lost":0,"total_won":0,"total_lost":0,"titles":0,"hand":"Right"}
    for s in stats_list:
        if not isinstance(s,dict) or s.get("type")!="singles": continue
        season=str(s.get("season",""))
        if season not in [cy,ly]: continue
        if season==cy and s.get("rank") and not out["rank"]:
            try: out["rank"]=int(s["rank"])
            except: pass
        for k,fk in [("surf_won",sw_key),("surf_lost",sl_key),
                     ("total_won","matches_won"),("total_lost","matches_lost"),("titles","titles")]:
            try: out[k]+=int(s.get(fk,0) or 0)
            except: pass
    return out

def dominance_rate(matches, surface=None, n=None):
    """
    Calculate Dominance Rate from set scores.
    DR = sets won / (sets won + sets lost)
    Optional: filter by surface, limit to last n matches.
    """
    pool = matches
    if n: pool = pool[:n]
    if surface: pool = [m for m in pool if m["surface"].lower() == surface.lower()]

    sets_won = 0; sets_lost = 0
    for m in pool:
        for s in m.get("scores_raw", []):
            if not isinstance(s, dict): continue
            is_p1 = m.get("is_p1", True)
            try:
                my  = int(s.get("score_first","0")  if is_p1 else s.get("score_second","0"))
                opp = int(s.get("score_second","0") if is_p1 else s.get("score_first","0"))
                if my > opp: sets_won += 1
                else: sets_lost += 1
            except: pass

    total = sets_won + sets_lost
    dr = round(sets_won / total * 100, 1) if total > 0 else None
    return dr, sets_won, sets_lost, total

def edge_score(p1sf,p2sf,p1me,p2me,p1st,p2st,n1,n2):
    s1,s2=0,0
    d=abs(p1sf-p2sf)
    if p1sf>p2sf: s1+=min(35,d*.45)
    else: s2+=min(35,d*.45)
    def wr(s): w,l=s["total_won"],s["total_lost"]; return w/(w+l)*100 if (w+l)>0 else 50
    d2=abs(wr(p1st)-wr(p2st))
    if wr(p1st)>wr(p2st): s1+=min(20,d2*.4)
    else: s2+=min(20,d2*.4)
    if p1me["unstable"] and not p2me["unstable"]: s2+=25
    elif p2me["unstable"] and not p1me["unstable"]: s1+=25
    else:
        d3=abs(p1me["tb_pct"]-p2me["tb_pct"])
        if p1me["tb_pct"]>p2me["tb_pct"]: s1+=min(15,d3*.4)
        else: s2+=min(15,d3*.4)
    d4=abs(p1me["d_pct"]-p2me["d_pct"])
    if p1me["d_pct"]>p2me["d_pct"]: s1+=min(20,d4*.3)
    else: s2+=min(20,d4*.3)
    tot=s1+s2
    if tot==0: p1p,p2p=50,50
    else: p1p=round(s1/tot*100); p2p=100-p1p
    gap=abs(p1p-p2p)
    fav=n1.split()[-1] if p1p>p2p else n2.split()[-1]
    if gap>=20: v=f"FAVORITO CLARO — {fav.upper()}"; side="p1" if p1p>p2p else "p2"
    elif gap>=10: v=f"LIGEIRA VANTAGEM — {fav.upper()}"; side="p1" if p1p>p2p else "p2"
    else: v="MATCHUP EQUILIBRADO — SEM EDGE CLARO"; side="neutral"
    return p1p,p2p,v,side

def hand_txt(h1,h2,n1,n2,surf):
    l1=n1.split()[-1]; l2=n2.split()[-1]
    if "left" in h1.lower() and "right" in h2.lower():
        return (f"<strong>Canhoto vs Destro</strong> — Serviço de {l1} abre o court para fora do backhand de {l2}. "
                +("Em Clay o deslize amplifica o reposicionamento." if surf=="Clay" else f"Em {surf} a velocidade potencia o ângulo canhoto.")
                +f" Verificar value em {l1} acima de 1.85.")
    elif "right" in h1.lower() and "left" in h2.lower():
        return (f"<strong>Destro vs Canhoto</strong> — Serviço de {l2} isola o backhand de {l1}. "
                +("Em Clay o ritmo lento permite reposicionamento." if surf=="Clay" else f"Em {surf} o ritmo rápido amplifica o ângulo canhoto.")
                +f" Canhotos têm edge em tiebreaks — value em {l2} acima de 1.80.")
    else:
        h="Ambos Destros" if "right" in h1.lower() else "Ambos Canhotos"
        return f"<strong>{h}</strong> — Sem factor de lateralidade. Break Points Converted como KPI primário."

# ── UI ────────────────────────────────────────
def bar(label,v1,v2,u="%"):
    v1=v1 or 0; v2=v2 or 0
    mx=max(v1,v2,1); w1=int(v1/mx*100); w2=int(v2/mx*100)
    c1="#30d158" if v1>=v2 else "#8b949e"; c2="#30d158" if v2>v1 else "#8b949e"
    st.markdown(f"""<div style="margin:7px 0">
      <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
        <span style="color:#f0f6fc;font-weight:600">{v1}{u}</span>
        <span style="color:#484f58;font-size:11px">{label}</span>
        <span style="color:#f0f6fc;font-weight:600">{v2}{u}</span></div>
      <div style="display:flex;gap:4px">
        <div style="flex:1"><div class="sb"><div style="width:{w1}%;height:6px;background:{c1};float:right;border-radius:3px"></div></div></div>
        <div style="flex:1"><div class="sb"><div style="width:{w2}%;height:6px;background:{c2};border-radius:3px"></div></div></div>
      </div></div>""", unsafe_allow_html=True)

def matches_tbl(matches,surface):
    if not matches:
        st.markdown('<div style="color:#484f58;padding:10px">Sem dados disponíveis.</div>',unsafe_allow_html=True); return
    scls={"hard":"bb","clay":"ba","grass":"bg","carpet":"bp"}
    rows=""
    for m in matches[:10]:
        res=m["result"]
        rb=f'<span class="b bg">W</span>' if res=="W" else f'<span class="b br">L</span>'
        surf=str(m["surface"]); sc=scls.get(surf.lower(),"bb")
        star="★ " if surf.lower()==surface.lower() else ""
        rows+=f"<tr><td style='color:#8b949e;white-space:nowrap'>{m['date']}</td><td>{m['opponent']}</td><td style='color:#8b949e'>{m['tourney'][:22]}</td><td><span class='b {sc}'>{star}{surf}</span></td><td style='color:#8b949e;font-size:11px'>{m['round'][:18]}</td><td>{rb}</td><td style='font-family:JetBrains Mono,monospace;font-size:11px'>{m['score']}</td></tr>"
    st.markdown(f"<table class='dt'><thead><tr><th>Data</th><th>Adversário</th><th>Torneio</th><th>Piso</th><th>Ronda</th><th>R</th><th>Score</th></tr></thead><tbody>{rows}</tbody></table>",unsafe_allow_html=True)

def h2h_tbl(h2h_raw):
    if isinstance(h2h_raw,dict): events=h2h_raw.get("H2H",[])
    elif isinstance(h2h_raw,list): events=h2h_raw
    else: events=[]
    if not events:
        st.markdown('<div style="color:#484f58;padding:8px">Sem confrontos directos encontrados.</div>',unsafe_allow_html=True); return
    scls={"hard":"bb","clay":"ba","grass":"bg","carpet":"bp"}
    rows=""
    for ev in events[:8]:
        if not isinstance(ev,dict): continue
        p1=str(ev.get("event_first_player","?")); p2=str(ev.get("event_second_player","?"))
        winner=p1 if ev.get("event_winner")=="First Player" else p2
        surf=str(ev.get("surface","Hard")).capitalize(); sc=scls.get(surf.lower(),"bb")
        scores=ev.get("scores",[])
        sc_str=" ".join([f"{s.get('score_first','?')}-{s.get('score_second','?')}" for s in scores if isinstance(s,dict)])
        rows+=f"<tr><td style='color:#8b949e'>{str(ev.get('event_date',''))[:10]}</td><td style='font-weight:600;color:#30d158'>{winner}</td><td style='color:#8b949e'>{str(ev.get('tournament_name',ev.get('league_name','?')))[:24]}</td><td><span class='b {sc}'>{surf}</span></td><td style='font-family:JetBrains Mono,monospace;font-size:11px'>{sc_str}</td></tr>"
    if not rows:
        st.markdown('<div style="color:#484f58;padding:8px">Sem confrontos encontrados.</div>',unsafe_allow_html=True); return
    st.markdown(f"<table class='dt'><thead><tr><th>Data</th><th>Vencedor</th><th>Torneio</th><th>Piso</th><th>Score</th></tr></thead><tbody>{rows}</tbody></table>",unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────
def main():
    st.markdown("""<div style="text-align:center;padding:34px 0 14px">
      <div class="hs">Tennis Edge · api-tennis.com · Dados Reais 2025/2026</div>
      <div class="ht">Elite Trading Dashboard</div>
      <div style="color:#484f58;font-size:12px;margin-top:8px;font-family:'JetBrains Mono',monospace">
        Rankings ATP reais · Resultados 2025/2026 · H2H · Análise de Piso
      </div></div>""", unsafe_allow_html=True)
    st.markdown('<hr class="hr">', unsafe_allow_html=True)

    # Load standings once (needed for player search)
    with st.spinner("A carregar rankings ATP..."):
        standings = get_atp_standings()

    if not standings:
        st.error("Não foi possível carregar os rankings ATP. Verifica a chave API.")
        return

    c1,c2,c3,c4=st.columns([2,2,1,1])
    with c1:
        st.markdown('<div class="sl">Jogador 1</div>',unsafe_allow_html=True)
        p1i=st.text_input("p1","",placeholder="Ex: Sinner, Fucsovics, Alcaraz...",label_visibility="collapsed")
    with c2:
        st.markdown('<div class="sl">Jogador 2</div>',unsafe_allow_html=True)
        p2i=st.text_input("p2","",placeholder="Ex: Tabilo, Medvedev, Zverev...",label_visibility="collapsed")
    with c3:
        st.markdown('<div class="sl">Piso</div>',unsafe_allow_html=True)
        surface=st.selectbox("surf",["Hard","Clay","Grass","Carpet"],label_visibility="collapsed")
    with c4:
        st.markdown('<div class="sl">&nbsp;</div>',unsafe_allow_html=True)
        go=st.button("⚡ Gerar Relatório")

    st.markdown("""<div class="ib">💡 <strong>Dados reais 2025/2026</strong> — Escreve o apelido:
      <em>Sinner</em>, <em>Alcaraz</em>, <em>Fucsovics</em>, <em>Tabilo</em>, <em>Djokovic</em>...
    </div>""",unsafe_allow_html=True)

    # Debug search
    with st.expander("🔍 Pesquisar nome exacto (usa se aparecer 'não encontrado')"):
        dq=st.text_input("Nome:",placeholder="Ex: Fucsovics",key="debug_q")
        if st.button("Pesquisar",key="debug_btn") and dq:
            res=[p for p in standings if dq.lower() in str(p.get("player","")).lower()]
            if res:
                for r in res[:10]:
                    st.code(f"#{r.get('place')} {r.get('player')} | key:{r.get('player_key')} | {r.get('country')}")
            else:
                st.warning("Não encontrado. Tenta outra grafia.")

    if not go: 
        st.markdown("""<div style="text-align:center;padding:55px 20px;color:#484f58">
          <div style="font-size:44px;margin-bottom:12px">🎾</div>
          <div style="font-family:'DM Serif Display',serif;font-size:20px;color:#8b949e">Pronto para analisar</div>
          <div style="font-size:12px;margin-top:8px;font-family:'JetBrains Mono',monospace">Preenche os nomes e clica Gerar Relatório</div>
        </div>""",unsafe_allow_html=True); return

    if not p1i.strip() or not p2i.strip():
        st.error("Preenche os nomes dos dois jogadores."); return

    p1_standing = find_player(p1i, standings)
    p2_standing = find_player(p2i, standings)

    if not p1_standing:
        st.error(f"'{p1i}' não encontrado nos rankings ATP. Usa o campo de pesquisa abaixo para ver a grafia exacta.")
        return
    if not p2_standing:
        st.error(f"'{p2i}' não encontrado nos rankings ATP. Usa o campo de pesquisa abaixo para ver a grafia exacta.")
        return

    p1k=str(p1_standing.get("player_key","")); p2k=str(p2_standing.get("player_key",""))
    p1n=str(p1_standing.get("player","")); p2n=str(p2_standing.get("player",""))
    p1c=str(p1_standing.get("country","")); p2c=str(p2_standing.get("country",""))
    p1_rank_pos=str(p1_standing.get("place","")); p2_rank_pos=str(p2_standing.get("place",""))
    p1_pts=str(p1_standing.get("points","")); p2_pts=str(p2_standing.get("points",""))

    with st.spinner("A carregar dados..."):
        p1ev=get_events(p1k); p2ev=get_events(p2k)
        p1det=get_player_detail(p1k); p2det=get_player_detail(p2k)
        h2h_raw=get_h2h(p1k,p2k)

    p1m=parse_matches(p1ev,p1k,surface); p2m=parse_matches(p2ev,p2k,surface)
    p1sf,p1sw,p1sc=surface_form(p1m,surface); p2sf,p2sw,p2sc=surface_form(p2m,surface)
    p1me=mental(p1m); p2me=mental(p2m)
    p1st=season_stats_from_detail(p1det,surface); p2st=season_stats_from_detail(p2det,surface)
    p1h=p1st.get("hand","Right"); p2h=p2st.get("hand","Right")

    # Use ranking from standings (more reliable)
    if not p1st["rank"] and p1_rank_pos:
        try: p1st["rank"]=int(p1_rank_pos)
        except: pass
    if not p2st["rank"] and p2_rank_pos:
        try: p2st["rank"]=int(p2_rank_pos)
        except: pass

    # Dominance Rate — overall, surface-specific, last 10
    p1dr_all,  p1sw_all,  p1sl_all,  _ = dominance_rate(p1m)
    p1dr_surf, p1sw_surf, p1sl_surf, _ = dominance_rate(p1m, surface=surface)
    p1dr_10,   p1sw_10,   p1sl_10,   _ = dominance_rate(p1m, n=10)
    p2dr_all,  p2sw_all,  p2sl_all,  _ = dominance_rate(p2m)
    p2dr_surf, p2sw_surf, p2sl_surf, _ = dominance_rate(p2m, surface=surface)
    p2dr_10,   p2sw_10,   p2sl_10,   _ = dominance_rate(p2m, n=10)

    pct1,pct2,verdict,side=edge_score(p1sf,p2sf,p1me,p2me,p1st,p2st,p1n,p2n)
    htxt=hand_txt(p1h,p2h,p1n,p2n,surface)

    # H2H count
    if isinstance(h2h_raw,dict): h2h_events=h2h_raw.get("H2H",[])
    elif isinstance(h2h_raw,list): h2h_events=h2h_raw
    else: h2h_events=[]
    hw1=sum(1 for e in h2h_events if isinstance(e,dict) and e.get("event_winner")=="First Player"
            and str(e.get("first_player_key",""))==p1k)
    hw2=len(h2h_events)-hw1

    st.markdown('<hr class="hr">',unsafe_allow_html=True)

    r1s=f"#{p1st['rank']}" if p1st['rank'] else "NR"
    r2s=f"#{p2st['rank']}" if p2st['rank'] else "NR"
    h1l="Canhoto 🤚" if "left" in p1h.lower() else "Destro ✋"
    h2l="Canhoto 🤚" if "left" in p2h.lower() else "Destro ✋"
    m1c="br" if p1me["unstable"] else "bg"; m1l="⚠ INSTÁVEL" if p1me["unstable"] else "✓ ESTÁVEL"
    m2c="br" if p2me["unstable"] else "bg"; m2l="⚠ INSTÁVEL" if p2me["unstable"] else "✓ ESTÁVEL"

    st.markdown(f"""<div class="card">
      <div class="sl">Análise de Partida — Dados Reais 2025/2026</div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-top:14px;flex-wrap:wrap;gap:20px">
        <div style="text-align:center;flex:1;min-width:160px">
          <div style="font-family:'DM Serif Display',serif;font-size:24px">{p1n}</div>
          <div style="font-size:12px;color:#8b949e">{p1c}</div>
          <div style="font-size:32px;font-weight:800;color:#30d158;margin:4px 0">{r1s}</div>
          <div style="font-size:11px;color:#8b949e;margin-bottom:10px">{p1_pts} pts · {p1st['surf_won']}V/{p1st['surf_lost']}D em {surface}</div>
          <span class="b {m1c}">{m1l}</span>&nbsp;<span class="b bb">{h1l}</span></div>
        <div style="text-align:center;padding:0 14px">
          <div style="font-family:'JetBrains Mono',monospace;font-size:18px;color:#484f58">VS</div>
          <div style="margin-top:8px"><span class="b ba">{surface}</span></div>
          <div style="margin-top:6px;font-size:11px;color:#484f58;font-family:'JetBrains Mono',monospace">H2H {hw1}–{hw2}</div></div>
        <div style="text-align:center;flex:1;min-width:160px">
          <div style="font-family:'DM Serif Display',serif;font-size:24px">{p2n}</div>
          <div style="font-size:12px;color:#8b949e">{p2c}</div>
          <div style="font-size:32px;font-weight:800;color:#30d158;margin:4px 0">{r2s}</div>
          <div style="font-size:11px;color:#8b949e;margin-bottom:10px">{p2_pts} pts · {p2st['surf_won']}V/{p2st['surf_lost']}D em {surface}</div>
          <span class="b {m2c}">{m2l}</span>&nbsp;<span class="b bb">{h2l}</span></div>
      </div></div>""",unsafe_allow_html=True)

    st.markdown(f"""<div class="card">
      <div class="sl">Edge Score — Surface-Weighted Analysis</div>
      <div style="display:flex;gap:8px;margin-top:14px;align-items:center">
        <div style="color:#f0f6fc;font-weight:700;font-size:15px;min-width:42px">{pct1}%</div>
        <div style="flex:1;height:12px;background:var(--el);border-radius:6px;overflow:hidden">
          <div style="display:flex;height:100%">
            <div style="width:{pct1}%;background:linear-gradient(90deg,#30d158,#25a244);border-radius:6px 0 0 6px"></div>
            <div style="width:{pct2}%;background:linear-gradient(90deg,#ff453a,#cc3730);border-radius:0 6px 6px 0"></div>
          </div></div>
        <div style="color:#f0f6fc;font-weight:700;font-size:15px;min-width:42px;text-align:right">{pct2}%</div></div>
      <div style="display:flex;justify-content:space-between;margin-top:5px">
        <div style="font-size:10px;color:#8b949e;font-family:'JetBrains Mono',monospace">{p1n.split()[-1].upper()}</div>
        <div style="font-size:10px;color:#8b949e;font-family:'JetBrains Mono',monospace">{p2n.split()[-1].upper()}</div>
      </div></div>""",unsafe_allow_html=True)

    t1,t2,t3,t4,t5=st.tabs(["📊 Forma & Piso","📈 Stats de Época","🧠 Momento Psicológico","🤝 H2H & Matchup","🏆 Bottom Line"])

    with t1:
        ca,cb=st.columns(2)
        for col,pn,pm,psf,psw,psc,pst,rk in [(ca,p1n,p1m,p1sf,p1sw,p1sc,p1st,r1s),(cb,p2n,p2m,p2sf,p2sw,p2sc,p2st,r2s)]:
            with col:
                l10=pm[:10]; wc=sum(1 for m in l10 if m["result"]=="W"); tot=len(l10)
                wrp=round(wc/tot*100) if tot>0 else 0
                st.markdown(f"""<div class="card"><div class="sl">{pn}</div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin:10px 0 14px;gap:10px;flex-wrap:wrap">
                    <div><div style="font-size:32px;font-family:'DM Serif Display',serif;color:#30d158">{wrp}%</div>
                      <div style="font-size:11px;color:#8b949e">Win Rate (últimos 10)</div></div>
                    <div style="text-align:center;padding:10px 13px;background:var(--el);border-radius:10px">
                      <div style="font-size:20px;font-weight:700;color:#ffd60a">{rk}</div>
                      <div style="font-size:10px;color:#8b949e">Ranking ATP</div></div>
                    <div style="text-align:right"><div style="font-size:18px;font-weight:700">{psf}%</div>
                      <div style="font-size:11px;color:#8b949e">{surface} form (×2)</div>
                      <div style="font-size:10px;color:#484f58">{psw}/{psc} jogos</div></div>
                  </div></div>""",unsafe_allow_html=True)
                matches_tbl(pm,surface)
        st.markdown("""<div style="background:var(--el);border-radius:8px;padding:9px 14px;margin-top:10px;font-size:12px;color:#8b949e">
          ★ Jogos no mesmo piso têm <strong style="color:#f0f6fc">peso duplo</strong> · api-tennis.com 2025/2026
        </div>""",unsafe_allow_html=True)

    with t2:
        ca,cb=st.columns(2)
        for col,pn,pst2 in [(ca,p1n,p1st),(cb,p2n,p2st)]:
            with col:
                tw=pst2["total_won"]; tl=pst2["total_lost"]
                wr=round(tw/(tw+tl)*100,1) if (tw+tl)>0 else 0
                sw2=pst2["surf_won"]; sl2=pst2["surf_lost"]
                swr=round(sw2/(sw2+sl2)*100,1) if (sw2+sl2)>0 else 0
                st.markdown(f"""<div class="card"><div class="sl">{pn} — Época Actual</div>
                  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:12px">
                    <div style="background:var(--el);border-radius:8px;padding:12px;text-align:center">
                      <div style="font-size:20px;font-weight:700;color:#30d158">{tw}V/{tl}D</div>
                      <div style="font-size:10px;color:#8b949e;margin-top:2px">Total</div></div>
                    <div style="background:var(--el);border-radius:8px;padding:12px;text-align:center">
                      <div style="font-size:20px;font-weight:700;color:#ffd60a">{wr}%</div>
                      <div style="font-size:10px;color:#8b949e;margin-top:2px">Win Rate</div></div>
                    <div style="background:var(--el);border-radius:8px;padding:12px;text-align:center">
                      <div style="font-size:20px;font-weight:700;color:#30d158">{pst2['titles']}</div>
                      <div style="font-size:10px;color:#8b949e;margin-top:2px">Títulos</div></div>
                  </div>
                  <div style="margin-top:10px;background:var(--el);border-radius:8px;padding:12px">
                    <div style="font-size:11px;color:#8b949e;margin-bottom:4px">{surface} esta época</div>
                    <div style="font-size:18px;font-weight:700;color:{'#30d158' if swr>=50 else '#ff453a'}">{sw2}V / {sl2}D &nbsp;·&nbsp; {swr}%</div>
                  </div></div>""",unsafe_allow_html=True)

        st.markdown(f"""<div class="card"><div class="sl">Comparação Directa</div>
          <div style="display:flex;justify-content:space-between;padding:10px 0 12px;border-bottom:1px solid var(--border);margin-bottom:4px">
            <span style="font-weight:600">{p1n.split()[-1]}</span>
            <span style="font-size:10px;color:#484f58;letter-spacing:1px">MÉTRICA</span>
            <span style="font-weight:600">{p2n.split()[-1]}</span></div>""",unsafe_allow_html=True)
        def wr_v(s): w,l=s["total_won"],s["total_lost"]; return round(w/(w+l)*100,1) if (w+l)>0 else 0
        def sw_v(s): w,l=s["surf_won"],s["surf_lost"]; return round(w/(w+l)*100,1) if (w+l)>0 else 0
        bar("Win Rate Geral",wr_v(p1st),wr_v(p2st))
        bar(f"Win Rate em {surface}",sw_v(p1st),sw_v(p2st))
        bar("Surface Form Score (×2 peso)",p1sf,p2sf)
        bar("Tie-Break Win %",p1me["tb_pct"],p2me["tb_pct"])
        bar("Sets Decisivos Win %",p1me["d_pct"],p2me["d_pct"])
        st.markdown("</div>",unsafe_allow_html=True)

        # ── DOMINANCE RATE ──
        def dr_color(v):
            if v is None: return "#484f58"
            if v >= 60: return "#30d158"
            if v >= 50: return "#ffd60a"
            return "#ff453a"
        def dr_fmt(v): return f"{v}%" if v is not None else "N/D"

        st.markdown(f"""<div class="card">
          <div class="sl">Dominance Rate — Controlo de Sets</div>
          <div style="font-size:12px;color:#8b949e;margin-bottom:16px">
            Sets ganhos / Sets totais jogados — métrica de dominância real independente do resultado final
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">

            <div style="background:var(--el);border-radius:10px;padding:16px">
              <div style="font-size:10px;color:#484f58;letter-spacing:1px;margin-bottom:10px">OVERALL</div>
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div style="text-align:center;flex:1">
                  <div style="font-size:26px;font-weight:800;color:{dr_color(p1dr_all)}">{dr_fmt(p1dr_all)}</div>
                  <div style="font-size:10px;color:#8b949e;margin-top:2px">{p1n.split()[-1]}</div>
                  <div style="font-size:10px;color:#484f58">{p1sw_all}S/{p1sl_all}S</div>
                </div>
                <div style="font-size:12px;color:#484f58;padding:0 8px">vs</div>
                <div style="text-align:center;flex:1">
                  <div style="font-size:26px;font-weight:800;color:{dr_color(p2dr_all)}">{dr_fmt(p2dr_all)}</div>
                  <div style="font-size:10px;color:#8b949e;margin-top:2px">{p2n.split()[-1]}</div>
                  <div style="font-size:10px;color:#484f58">{p2sw_all}S/{p2sl_all}S</div>
                </div>
              </div>
            </div>

            <div style="background:var(--el);border-radius:10px;padding:16px;border:1px solid rgba(255,214,10,.2)">
              <div style="font-size:10px;color:#ffd60a;letter-spacing:1px;margin-bottom:10px">EM {surface.upper()} (×2 PESO)</div>
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div style="text-align:center;flex:1">
                  <div style="font-size:26px;font-weight:800;color:{dr_color(p1dr_surf)}">{dr_fmt(p1dr_surf)}</div>
                  <div style="font-size:10px;color:#8b949e;margin-top:2px">{p1n.split()[-1]}</div>
                  <div style="font-size:10px;color:#484f58">{p1sw_surf}S/{p1sl_surf}S</div>
                </div>
                <div style="font-size:12px;color:#484f58;padding:0 8px">vs</div>
                <div style="text-align:center;flex:1">
                  <div style="font-size:26px;font-weight:800;color:{dr_color(p2dr_surf)}">{dr_fmt(p2dr_surf)}</div>
                  <div style="font-size:10px;color:#8b949e;margin-top:2px">{p2n.split()[-1]}</div>
                  <div style="font-size:10px;color:#484f58">{p2sw_surf}S/{p2sl_surf}S</div>
                </div>
              </div>
            </div>

            <div style="background:var(--el);border-radius:10px;padding:16px">
              <div style="font-size:10px;color:#484f58;letter-spacing:1px;margin-bottom:10px">ÚLTIMOS 10 JOGOS</div>
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div style="text-align:center;flex:1">
                  <div style="font-size:26px;font-weight:800;color:{dr_color(p1dr_10)}">{dr_fmt(p1dr_10)}</div>
                  <div style="font-size:10px;color:#8b949e;margin-top:2px">{p1n.split()[-1]}</div>
                  <div style="font-size:10px;color:#484f58">{p1sw_10}S/{p1sl_10}S</div>
                </div>
                <div style="font-size:12px;color:#484f58;padding:0 8px">vs</div>
                <div style="text-align:center;flex:1">
                  <div style="font-size:26px;font-weight:800;color:{dr_color(p2dr_10)}">{dr_fmt(p2dr_10)}</div>
                  <div style="font-size:10px;color:#8b949e;margin-top:2px">{p2n.split()[-1]}</div>
                  <div style="font-size:10px;color:#484f58">{p2sw_10}S/{p2sl_10}S</div>
                </div>
              </div>
            </div>

          </div>
          <div style="margin-top:12px;font-size:11px;color:#484f58">
            🟢 ≥60% dominante &nbsp;·&nbsp; 🟡 50–60% equilibrado &nbsp;·&nbsp; 🔴 &lt;50% vulnerável
          </div>
        </div>""",unsafe_allow_html=True)

    with t3:
        ca,cb=st.columns(2)
        for col,pn,pm2 in [(ca,p1n,p1me),(cb,p2n,p2me)]:
            with col:
                mc="#ff453a" if pm2["unstable"] else "#30d158"
                ml="⚠ MENTALMENTE INSTÁVEL" if pm2["unstable"] else "✓ MENTALMENTE ESTÁVEL"
                tbs=" ".join([f'<span class="b {"bg" if r=="W" else "br"}">{r}</span>' for r in pm2["last3"]]) or '<span style="color:#484f58">Sem tie-breaks</span>'
                st.markdown(f"""<div class="card" style="border-color:{mc}40"><div class="sl">{pn}</div>
                  <div style="font-size:13px;font-weight:700;color:{mc};margin:10px 0">{ml}</div>
                  <div style="margin-bottom:14px">
                    <div style="font-size:10px;color:#8b949e;margin-bottom:6px;letter-spacing:1px">ÚLTIMOS TIE-BREAKS</div>
                    <div style="display:flex;gap:5px;flex-wrap:wrap">{tbs}</div></div>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
                    <div style="background:var(--el);border-radius:8px;padding:11px">
                      <div style="font-size:19px;font-weight:700">{pm2['tw']}/{pm2['ttb']}</div>
                      <div style="font-size:10px;color:#8b949e">Tie-Breaks</div>
                      <div style="font-size:13px;color:{'#30d158' if pm2['tb_pct']>=50 else '#ff453a'};font-weight:600">{pm2['tb_pct']}%</div></div>
                    <div style="background:var(--el);border-radius:8px;padding:11px">
                      <div style="font-size:19px;font-weight:700">{pm2['dw']}/{pm2['dt']}</div>
                      <div style="font-size:10px;color:#8b949e">Sets Decisivos</div>
                      <div style="font-size:13px;color:{'#30d158' if pm2['d_pct']>=50 else '#ff453a'};font-weight:600">{pm2['d_pct']}%</div></div>
                  </div></div>""",unsafe_allow_html=True)
        if p1me["unstable"] and p2me["unstable"]: mv="⚠ Ambos instáveis — preferir Over/Under Games."; mc2="d"
        elif p1me["unstable"]: mv=f"🎯 {p2n.split()[-1]} tem vantagem psicológica."; mc2=""
        elif p2me["unstable"]: mv=f"🎯 {p1n.split()[-1]} tem vantagem psicológica."; mc2=""
        else: mv="✓ Ambos estáveis — decidir via métricas técnicas e piso."; mc2="n"
        st.markdown(f"""<div class="vb {mc2}" style="margin-top:14px"><div class="sl">Veredito Psicológico</div>
          <div style="font-size:15px;color:#f0f6fc;margin-top:8px;line-height:1.7">{mv}</div></div>""",unsafe_allow_html=True)

    with t4:
        st.markdown(f"""<div class="card"><div class="sl">Head-to-Head Histórico</div>
          <div style="display:flex;align-items:center;justify-content:center;gap:40px;margin:14px 0;padding:14px;background:var(--el);border-radius:10px">
            <div style="text-align:center">
              <div style="font-size:40px;font-weight:800;color:{'#30d158' if hw1>=hw2 else '#f0f6fc'}">{hw1}</div>
              <div style="font-size:12px;color:#8b949e">{p1n.split()[-1]}</div></div>
            <div style="font-size:18px;color:#484f58">—</div>
            <div style="text-align:center">
              <div style="font-size:40px;font-weight:800;color:{'#30d158' if hw2>hw1 else '#f0f6fc'}">{hw2}</div>
              <div style="font-size:12px;color:#8b949e">{p2n.split()[-1]}</div></div>
          </div>
          <div class="sl" style="margin-top:14px">Últimos Confrontos Directos</div>""",unsafe_allow_html=True)
        h2h_tbl(h2h_raw)
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown(f"""<div class="card"><div class="sl">Análise de Lateralidade</div>
          <div style="display:flex;justify-content:center;gap:36px;padding:14px;background:var(--el);border-radius:10px;margin:12px 0">
            <div style="text-align:center"><div style="font-size:26px">{'🤚' if 'left' in p1h.lower() else '✋'}</div>
              <div style="font-weight:600;margin-top:4px">{p1n.split()[-1]}</div>
              <div style="font-size:11px;color:#8b949e">{p1h}</div></div>
            <div style="display:flex;align-items:center;color:#484f58">⟷</div>
            <div style="text-align:center"><div style="font-size:26px">{'🤚' if 'left' in p2h.lower() else '✋'}</div>
              <div style="font-weight:600;margin-top:4px">{p2n.split()[-1]}</div>
              <div style="font-size:11px;color:#8b949e">{p2h}</div></div>
          </div>
          <div style="font-size:14px;line-height:1.8;color:#c9d1d9;margin-top:10px">{htxt}</div></div>""",unsafe_allow_html=True)

    with t5:
        favn=p1n if side=="p1" else (p2n if side=="p2" else "—")
        favp=pct1 if side=="p1" else (pct2 if side=="p2" else 50)
        vc="d" if side=="p2" else ("n" if side=="neutral" else "")
        mn=""
        if p1me["unstable"] and side!="p1": mn=f" ⚠ {p1n.split()[-1]} perdeu os últimos 3 tie-breaks."
        elif p2me["unstable"] and side!="p2": mn=f" ⚠ {p2n.split()[-1]} perdeu os últimos 3 tie-breaks."
        sn={"Hard":"Hard equilibrado — serviço e retorno com peso similar.",
            "Clay":"Clay penaliza grandes servidores e amplifica o retorno.",
            "Grass":"Grass favorece grandes servidores — 1º serviço é KPI crítico.",
            "Carpet":"Carpet rápido — favorece servos agressivos."}.get(surface,"")
        hn=""
        if hw1+hw2>0:
            if hw1>hw2: hn=f" H2H: {p1n.split()[-1]} lidera {hw1}-{hw2}."
            elif hw2>hw1: hn=f" H2H: {p2n.split()[-1]} lidera {hw2}-{hw1}."
            else: hn=f" H2H equilibrado {hw1}-{hw2}."
        mkt="Diferencial suficiente para Match Odds." if abs(pct1-pct2)>=15 else "Diferencial marginal — considerar Handicap de Sets ou Total Games."
        st.markdown(f"""<div class="vb {vc}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:20px">
            <div style="flex:2;min-width:240px">
              <div style="font-size:10px;color:#8b949e;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px">Match Odds — Veredito Final</div>
              <div style="font-family:'DM Serif Display',serif;font-size:24px;color:#f0f6fc;line-height:1.2;margin-bottom:12px">{verdict}</div>
              <div style="font-size:14px;color:#c9d1d9;line-height:1.8">{sn}{mn}{hn}<br>
                Edge: <strong style="color:{'#30d158' if side=='p1' else '#f0f6fc'}">{p1n.split()[-1]} {pct1}%</strong> vs
                <strong style="color:{'#30d158' if side=='p2' else '#f0f6fc'}">{p2n.split()[-1]} {pct2}%</strong>. {mkt}</div></div>
            <div style="flex:1;min-width:130px;text-align:center;padding:22px;background:rgba(0,0,0,.2);border-radius:12px">
              <div style="font-size:10px;color:#8b949e;margin-bottom:8px;letter-spacing:1px">EDGE SCORE</div>
              <div style="font-size:50px;font-family:'DM Serif Display',serif;color:{'#30d158' if side!='neutral' else '#ffd60a'}">{favp}%</div>
              <div style="font-size:12px;font-weight:600;color:#f0f6fc;margin-top:4px">{'⚡ '+favn.split()[-1] if side!='neutral' else '🎲 COIN FLIP'}</div></div></div>
          <div style="margin-top:18px;padding-top:12px;border-top:1px solid rgba(255,255,255,.07);font-size:11px;color:#484f58">
            Fonte: api-tennis.com · Dados 2025/2026 · Uso educativo — trading responsável.
          </div></div>""",unsafe_allow_html=True)

if __name__=="__main__":
    main()
    
