import streamlit as st
import requests
import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime
import re

st.set_page_config(page_title="Tennis Edge", page_icon="🎾", layout="wide")

# ── CSS ──────────────────────────────────────
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
.eb{background:rgba(255,69,58,.08);border:1px solid rgba(255,69,58,.25);border-radius:10px;padding:11px 16px;font-size:13px;color:#ff453a;margin-bottom:14px;}
</style>
""", unsafe_allow_html=True)

# ── DATA LOADERS ─────────────────────────────
BASE = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master"

@st.cache_data(ttl=3600, show_spinner=False)
def load_players():
    """atp_players.csv HAS a header row: player_id,first_name,last_name,hand,dob,country_code"""
    url = f"{BASE}/atp_players.csv"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    # Try with header first
    df = pd.read_csv(StringIO(r.text), low_memory=False)
    # Normalise column names (sometimes no header)
    cols = list(df.columns)
    if cols[0].isdigit() or len(cols) < 5:
        # No header — assign manually
        df = pd.read_csv(StringIO(r.text), header=None, low_memory=False,
                         names=["player_id","first_name","last_name","hand","dob","country_code"])
    else:
        # Has header — rename to standard
        rename = {}
        for c in cols:
            cl = c.lower().strip()
            if "id" in cl: rename[c] = "player_id"
            elif "first" in cl: rename[c] = "first_name"
            elif "last" in cl: rename[c] = "last_name"
            elif "hand" in cl: rename[c] = "hand"
            elif "dob" in cl or "birth" in cl: rename[c] = "dob"
            elif "country" in cl: rename[c] = "country_code"
        df = df.rename(columns=rename)

    df["player_id"] = pd.to_numeric(df["player_id"], errors="coerce")
    df = df.dropna(subset=["player_id"])
    df["player_id"] = df["player_id"].astype(int)
    df["first_name"] = df["first_name"].fillna("").astype(str).str.strip()
    df["last_name"] = df["last_name"].fillna("").astype(str).str.strip()
    df["full_name"] = (df["first_name"] + " " + df["last_name"]).str.strip()
    df["hand"] = df["hand"].fillna("R").astype(str).str.strip().str.upper()
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def load_rankings():
    """atp_rankings_current.csv — no header: ranking_date,ranking,player_id,ranking_points"""
    url = f"{BASE}/atp_rankings_current.csv"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    # Always no header for ranking files
    df = pd.read_csv(StringIO(r.text), header=None, low_memory=False,
                     names=["ranking_date","ranking","player_id","ranking_points"])
    df["player_id"] = pd.to_numeric(df["player_id"], errors="coerce")
    df["ranking"] = pd.to_numeric(df["ranking"], errors="coerce")
    df["ranking_points"] = pd.to_numeric(df["ranking_points"], errors="coerce")
    df["ranking_date"] = pd.to_datetime(df["ranking_date"].astype(str), format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=["player_id","ranking"])
    df["player_id"] = df["player_id"].astype(int)
    latest = df["ranking_date"].max()
    return df[df["ranking_date"] == latest].copy()

@st.cache_data(ttl=3600, show_spinner=False)
def load_matches_year(year):
    url = f"{BASE}/atp_matches_{year}.csv"
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        return pd.DataFrame()
    df = pd.read_csv(StringIO(r.text), low_memory=False)
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def load_recent_matches():
    cy = datetime.now().year
    frames = []
    for y in range(cy - 2, cy + 1):
        df = load_matches_year(y)
        if not df.empty:
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# ── PLAYER SEARCH ─────────────────────────────
def find_player(query, players_df):
    q = query.strip().lower()
    for col in ["full_name", "last_name", "first_name"]:
        m = players_df[col].str.lower() == q
        if m.any(): return players_df[m].iloc[0]
    for col in ["full_name", "last_name"]:
        m = players_df[col].str.lower().str.contains(q, na=False)
        if m.any(): return players_df[m].iloc[0]
    return None

def get_ranking(pid, rdf):
    row = rdf[rdf["player_id"] == int(pid)]
    if not row.empty:
        r = row.iloc[0]
        return int(r["ranking"]), int(r["ranking_points"]) if pd.notna(r["ranking_points"]) else 0
    return None, None

# ── MATCH PROCESSING ──────────────────────────
def get_player_matches(pid, mdf, n=30):
    if mdf.empty: return pd.DataFrame()
    pid = int(pid)
    frames = []
    for role, id_col, pfx, opfx, oname_col, orank_col in [
        ("W", "winner_id", "w_", "l_", "loser_name", "loser_rank"),
        ("L", "loser_id",  "l_", "w_", "winner_name","winner_rank")
    ]:
        sub = mdf[mdf[id_col] == pid].copy()
        if sub.empty: continue
        sub["result"] = role
        sub["opponent_name"] = sub.get(oname_col, pd.Series(dtype=str))
        sub["opponent_rank"] = pd.to_numeric(sub.get(orank_col, pd.Series(dtype=float)), errors="coerce")
        for stat in ["ace","df","svpt","1stIn","1stWon","2ndWon","bpSaved","bpFaced"]:
            pc = f"{pfx}{stat}"
            oc = f"{opfx}{stat}"
            sub[f"p_{stat}"] = pd.to_numeric(sub.get(pc, pd.Series(dtype=float)), errors="coerce")
            sub[f"o_{stat}"] = pd.to_numeric(sub.get(oc, pd.Series(dtype=float)), errors="coerce")
        frames.append(sub)

    if not frames: return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["tourney_date"] = pd.to_datetime(out["tourney_date"].astype(str), format="%Y%m%d", errors="coerce")
    out = out.sort_values("tourney_date", ascending=False)
    return out.head(n)

def safe_pct(a, b):
    try:
        a, b = float(a), float(b)
        return round(a/b*100, 1) if b > 0 else None
    except: return None

def srv_stats(matches):
    s = dict.fromkeys(["first_srv","pts_1st","pts_2nd","ret","aces_pm","df_pm","bp_saved","bp_conv"], None)
    if matches.empty: return s
    def sm(c):
        try: return pd.to_numeric(matches[c], errors="coerce").sum()
        except: return 0.0
    svpt=sm("p_svpt"); fin=sm("p_1stIn"); fwon=sm("p_1stWon")
    swon=sm("p_2ndWon"); aces=sm("p_ace"); dfs=sm("p_df")
    bps=sm("p_bpSaved"); bpf=sm("p_bpFaced")
    osvpt=sm("o_svpt"); ofwon=sm("o_1stWon"); oswon=sm("o_2ndWon")
    obps=sm("o_bpSaved"); obpf=sm("o_bpFaced")
    s2nd = svpt - fin
    n = len(matches)
    s["first_srv"] = safe_pct(fin, svpt)
    s["pts_1st"]   = safe_pct(fwon, fin)
    s["pts_2nd"]   = safe_pct(swon, s2nd) if s2nd > 0 else None
    s["aces_pm"]   = round(aces/n,1) if n > 0 else None
    s["df_pm"]     = round(dfs/n,1) if n > 0 else None
    s["bp_saved"]  = safe_pct(bps, bpf)
    ret_won = osvpt - ofwon - oswon
    s["ret"]       = safe_pct(ret_won, osvpt)
    s["bp_conv"]   = safe_pct(obpf - obps, obpf)
    return s

def surf_form(matches, surface, n=10):
    if matches.empty: return 0.0, 0, 0
    last = matches.head(n)
    ww, wt, sw, sc = 0, 0, 0, 0
    for _, row in last.iterrows():
        same = str(row.get("surface","")).strip().lower() == surface.lower()
        w = 2 if same else 1
        wt += w
        if row["result"] == "W": ww += w
        if same:
            sc += 1
            if row["result"] == "W": sw += 1
    return round(ww/wt*100,1) if wt > 0 else 0.0, sw, sc

def mental(matches):
    tb_seq, tw, tl, dw, dt = [], 0, 0, 0, 0
    for _, row in matches.iterrows():
        score = str(row.get("score",""))
        res = row.get("result","")
        for s in score.split():
            if "7-6" in s:
                tw+=1; tb_seq.append("W")
            elif "6-7" in s:
                tl+=1; tb_seq.append("L")
        sets = [s for s in score.split() if re.match(r'^\d+-\d+', s)]
        if len(sets) >= 3:
            dt += 1
            if res == "W": dw += 1
    last3 = tb_seq[-3:]
    ttb = tw + tl
    return {
        "tw":tw,"tl":tl,"ttb":ttb,
        "tb_pct": round(tw/ttb*100,1) if ttb>0 else 50.0,
        "last3": last3,
        "unstable": len(last3)==3 and all(r=="L" for r in last3),
        "dw":dw,"dt":dt,
        "d_pct": round(dw/dt*100,1) if dt>0 else 50.0
    }

def h2h(p1id, p2id, mdf):
    if mdf.empty: return 0, 0, []
    p1id, p2id = int(p1id), int(p2id)
    h = mdf[
        ((mdf["winner_id"]==p1id)&(mdf["loser_id"]==p2id))|
        ((mdf["winner_id"]==p2id)&(mdf["loser_id"]==p1id))
    ].copy()
    h["tourney_date"] = pd.to_datetime(h["tourney_date"].astype(str), format="%Y%m%d", errors="coerce")
    h = h.sort_values("tourney_date", ascending=False)
    w1 = len(h[h["winner_id"]==p1id])
    w2 = len(h[h["winner_id"]==p2id])
    rec = []
    for _, row in h.head(6).iterrows():
        d = row["tourney_date"].strftime("%d/%m/%y") if pd.notna(row["tourney_date"]) else "?"
        rec.append({"date":d,"winner":str(row.get("winner_name","?")),"tourney":str(row.get("tourney_name","?"))[:24],
                    "surface":str(row.get("surface","?")),"score":str(row.get("score","?"))})
    return w1, w2, rec

# ── EDGE SCORE ────────────────────────────────
def edge(p1sf,p2sf,p1s,p2s,p1m,p2m,n1,n2):
    s1,s2=0,0
    d=abs(p1sf-p2sf)
    if p1sf>p2sf: s1+=min(30,d*.4)
    else: s2+=min(30,d*.4)
    v1=(p1s["pts_1st"] or 65)*.6+(p1s["pts_2nd"] or 50)*.4
    v2=(p2s["pts_1st"] or 65)*.6+(p2s["pts_2nd"] or 50)*.4
    d2=abs(v1-v2)
    if v1>v2: s1+=min(25,d2*1.2)
    else: s2+=min(25,d2*1.2)
    r1=p1s["ret"] or 38; r2=p2s["ret"] or 38
    d3=abs(r1-r2)
    if r1>r2: s1+=min(20,d3)
    else: s2+=min(20,d3)
    if p1m["unstable"] and not p2m["unstable"]: s2+=25
    elif p2m["unstable"] and not p1m["unstable"]: s1+=25
    else:
        d4=abs(p1m["tb_pct"]-p2m["tb_pct"])
        if p1m["tb_pct"]>p2m["tb_pct"]: s1+=min(15,d4*.4)
        else: s2+=min(15,d4*.4)
    tot=s1+s2
    if tot==0: p1,p2=50,50
    else: p1=round(s1/tot*100); p2=100-p1
    gap=abs(p1-p2)
    fav=n1.split()[-1] if p1>p2 else n2.split()[-1]
    if gap>=20: v=f"FAVORITO CLARO — {fav.upper()}"; side="p1" if p1>p2 else "p2"
    elif gap>=10: v=f"LIGEIRA VANTAGEM — {fav.upper()}"; side="p1" if p1>p2 else "p2"
    else: v="MATCHUP EQUILIBRADO — SEM EDGE CLARO"; side="neutral"
    return p1,p2,v,side

def hand_txt(h1,h2,n1,n2,surf):
    l1=n1.split()[-1]; l2=n2.split()[-1]
    if h1=="L" and h2=="R":
        return (f"**Canhoto vs Destro** — O serviço de {l1} abre o court para fora do backhand de {l2}. "
                +("Em Clay o deslize amplifica o esforço de reposicionamento." if surf=="Clay"
                  else f"Em {surf} a velocidade potencia o ângulo canhoto.")
                +f" O mercado sub-valoriza canhotos em confronto directo — verificar value em {l1} acima de 1.85.")
    elif h1=="R" and h2=="L":
        return (f"**Destro vs Canhoto** — Serviço de {l2} isola o backhand de {l1}. "
                +("Em Clay o ritmo lento permite reposicionamento mais fácil." if surf=="Clay"
                  else f"Em {surf} o ritmo rápido amplifica o ângulo canhoto.")
                +f" Canhotos têm edge em tiebreaks por este padrão — verificar value em {l2} acima de 1.80.")
    else:
        h="Ambos Destros" if h1=="R" else "Ambos Canhotos"
        return f"**{h}** — Sem factor de lateralidade. Resultado via serviço, retorno e resistência mental. Foco em Break Points Converted como KPI primário."

# ── UI HELPERS ────────────────────────────────
def stat_bar(label,v1,v2,u="%"):
    v1=v1 or 0; v2=v2 or 0
    mx=max(v1,v2,1); w1=int(v1/mx*100); w2=int(v2/mx*100)
    c1="#30d158" if v1>=v2 else "#8b949e"; c2="#30d158" if v2>v1 else "#8b949e"
    st.markdown(f"""<div style="margin:7px 0">
      <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
        <span style="color:#f0f6fc;font-weight:600">{v1}{u}</span>
        <span style="color:#484f58;font-size:11px">{label}</span>
        <span style="color:#f0f6fc;font-weight:600">{v2}{u}</span>
      </div>
      <div style="display:flex;gap:4px">
        <div style="flex:1"><div class="sb"><div style="width:{w1}%;height:6px;background:{c1};float:right;border-radius:3px"></div></div></div>
        <div style="flex:1"><div class="sb"><div style="width:{w2}%;height:6px;background:{c2};border-radius:3px"></div></div></div>
      </div></div>""", unsafe_allow_html=True)

def matches_tbl(matches, surface):
    if matches.empty:
        st.markdown('<div style="color:#484f58;font-size:13px;padding:10px">Sem dados.</div>', unsafe_allow_html=True); return
    scls={"Hard":"bb","Clay":"ba","Grass":"bg","Carpet":"bp"}
    rows=""
    for _,m in matches.head(10).iterrows():
        res=m.get("result","?")
        rb=f'<span class="b bg">W</span>' if res=="W" else f'<span class="b br">L</span>'
        surf=str(m.get("surface","?")).strip()
        sc=scls.get(surf,"bb")
        star="★ " if surf.lower()==surface.lower() else ""
        score=str(m.get("score","")).strip()
        opp=str(m.get("opponent_name","?")).strip()
        opr=m.get("opponent_rank","")
        oprs=f"#{int(opr)}" if pd.notna(opr) and str(opr).strip() not in ["","nan"] else ""
        date=m.get("tourney_date","")
        ds=date.strftime("%d/%m/%y") if hasattr(date,"strftime") and pd.notna(date) else str(date)[:10]
        tourney=str(m.get("tourney_name","")).strip()[:20]
        rows+=f"<tr><td style='color:#8b949e;white-space:nowrap'>{ds}</td><td><div>{opp}</div><div style='font-size:10px;color:#484f58'>{oprs}</div></td><td style='color:#8b949e'>{tourney}</td><td><span class='b {sc}'>{star}{surf}</span></td><td>{rb}</td><td style='font-family:JetBrains Mono,monospace;font-size:11px'>{score}</td></tr>"
    st.markdown(f"<table class='dt'><thead><tr><th>Data</th><th>Adversário</th><th>Torneio</th><th>Piso</th><th>Res</th><th>Score</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)

def h2h_tbl(rec):
    if not rec:
        st.markdown('<div style="color:#484f58;font-size:13px;padding:8px">Sem confrontos directos nos dados (últimos 3 anos).</div>', unsafe_allow_html=True); return
    scls={"Hard":"bb","Clay":"ba","Grass":"bg","Carpet":"bp"}
    rows=""
    for m in rec:
        sc=scls.get(m["surface"],"bb")
        rows+=f"<tr><td style='color:#8b949e'>{m['date']}</td><td style='font-weight:600;color:#30d158'>{m['winner']}</td><td style='color:#8b949e'>{m['tourney']}</td><td><span class='b {sc}'>{m['surface']}</span></td><td style='font-family:JetBrains Mono,monospace;font-size:11px'>{m['score']}</td></tr>"
    st.markdown(f"<table class='dt'><thead><tr><th>Data</th><th>Vencedor</th><th>Torneio</th><th>Piso</th><th>Score</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)

def fmv(v,u="%"):
    return f"{v}{u}" if v is not None else "N/D"

# ── MAIN ──────────────────────────────────────
def main():
    st.markdown("""<div style="text-align:center;padding:34px 0 14px">
      <div class="hs">Tennis Edge Analytics · Jeff Sackmann / Tennis Abstract</div>
      <div class="ht">Elite Trading Dashboard</div>
      <div style="color:#484f58;font-size:12px;margin-top:8px;font-family:'JetBrains Mono',monospace">
        Rankings ATP reais · Últimos 3 anos · H2H histórico · Stats de serviço reais
      </div></div>""", unsafe_allow_html=True)
    st.markdown('<hr class="hr">', unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns([2,2,1,1])
    with c1:
        st.markdown('<div class="sl">Jogador 1</div>', unsafe_allow_html=True)
        p1i=st.text_input("p1","",placeholder="Ex: Djokovic, Sinner, Alcaraz...",label_visibility="collapsed")
    with c2:
        st.markdown('<div class="sl">Jogador 2</div>', unsafe_allow_html=True)
        p2i=st.text_input("p2","",placeholder="Ex: Medvedev, Zverev, Rune...",label_visibility="collapsed")
    with c3:
        st.markdown('<div class="sl">Piso</div>', unsafe_allow_html=True)
        surface=st.selectbox("surf",["Hard","Clay","Grass","Carpet"],label_visibility="collapsed")
    with c4:
        st.markdown('<div class="sl">&nbsp;</div>', unsafe_allow_html=True)
        go=st.button("⚡ Gerar Relatório")

    st.markdown("""<div class="ib">💡 <strong>Dados reais ATP</strong> — Jeff Sackmann / Tennis Abstract. 
      Escreve o apelido: <em>Djokovic</em>, <em>Sinner</em>, <em>Alcaraz</em>, <em>Medvedev</em>, <em>Zverev</em>...
    </div>""", unsafe_allow_html=True)

    if not go:
        st.markdown("""<div style="text-align:center;padding:55px 20px;color:#484f58">
          <div style="font-size:44px;margin-bottom:12px">🎾</div>
          <div style="font-family:'DM Serif Display',serif;font-size:20px;color:#8b949e">Pronto para analisar</div>
          <div style="font-size:12px;margin-top:8px;font-family:'JetBrains Mono',monospace">
            Preenche os nomes e clica Gerar Relatório
          </div></div>""", unsafe_allow_html=True)
        return

    if not p1i.strip() or not p2i.strip():
        st.error("Preenche os nomes dos dois jogadores."); return

    # ── LOAD ──
    with st.spinner("A carregar dados ATP..."):
        try:
            pdf = load_players()
            rdf = load_rankings()
            mdf = load_recent_matches()
        except Exception as e:
            st.markdown(f'<div class="eb">❌ Erro ao carregar dados: {e}</div>', unsafe_allow_html=True)
            return

    p1r=find_player(p1i, pdf)
    p2r=find_player(p2i, pdf)

    if p1r is None:
        st.error(f"'{p1i}' não encontrado. Tenta o apelido completo (ex: 'Djokovic')."); return
    if p2r is None:
        st.error(f"'{p2i}' não encontrado. Tenta o apelido completo (ex: 'Sinner')."); return

    p1id=int(p1r["player_id"]); p2id=int(p2r["player_id"])
    p1n=p1r["full_name"]; p2n=p2r["full_name"]
    p1h=str(p1r.get("hand","R")).upper(); p2h=str(p2r.get("hand","R")).upper()

    p1rank,p1pts=get_ranking(p1id,rdf)
    p2rank,p2pts=get_ranking(p2id,rdf)

    with st.spinner("A processar matches..."):
        p1m=get_player_matches(p1id,mdf,30)
        p2m=get_player_matches(p2id,mdf,30)

    p1sf,p1sw,p1sc=surf_form(p1m,surface)
    p2sf,p2sw,p2sc=surf_form(p2m,surface)
    p1s=srv_stats(p1m.head(15)); p2s=srv_stats(p2m.head(15))
    p1me=mental(p1m.head(20)); p2me=mental(p2m.head(20))
    hw1,hw2,hrec=h2h(p1id,p2id,mdf)
    pct1,pct2,verdict,side=edge(p1sf,p2sf,p1s,p2s,p1me,p2me,p1n,p2n)
    htxt=hand_txt(p1h,p2h,p1n,p2n,surface)

    st.markdown('<hr class="hr">', unsafe_allow_html=True)

    # ── MATCH HEADER ──
    r1s=f"#{p1rank}" if p1rank else "NR"; r2s=f"#{p2rank}" if p2rank else "NR"
    p1ps=f"{p1pts:,} pts" if p1pts else ""; p2ps=f"{p2pts:,} pts" if p2pts else ""
    h1l="Canhoto 🤚" if p1h=="L" else "Destro ✋"; h2l="Canhoto 🤚" if p2h=="L" else "Destro ✋"
    m1c="br" if p1me["unstable"] else "bg"; m2c="br" if p2me["unstable"] else "bg"
    m1l="⚠ INSTÁVEL" if p1me["unstable"] else "✓ ESTÁVEL"
    m2l="⚠ INSTÁVEL" if p2me["unstable"] else "✓ ESTÁVEL"

    st.markdown(f"""<div class="card">
      <div class="sl">Análise de Partida — Dados Reais ATP</div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-top:14px;flex-wrap:wrap;gap:20px">
        <div style="text-align:center;flex:1;min-width:170px">
          <div style="font-family:'DM Serif Display',serif;font-size:24px">{p1n}</div>
          <div style="font-size:32px;font-weight:800;color:#30d158;margin:4px 0">{r1s}</div>
          <div style="font-size:12px;color:#8b949e;margin-bottom:10px">{p1ps}</div>
          <div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap">
            <span class="b {m1c}">{m1l}</span><span class="b bb">{h1l}</span></div></div>
        <div style="text-align:center;padding:0 16px">
          <div style="font-family:'JetBrains Mono',monospace;font-size:18px;color:#484f58">VS</div>
          <div style="margin-top:8px"><span class="b ba">{surface}</span></div>
          <div style="margin-top:6px;font-size:11px;color:#484f58;font-family:'JetBrains Mono',monospace">H2H {hw1}–{hw2}</div></div>
        <div style="text-align:center;flex:1;min-width:170px">
          <div style="font-family:'DM Serif Display',serif;font-size:24px">{p2n}</div>
          <div style="font-size:32px;font-weight:800;color:#30d158;margin:4px 0">{r2s}</div>
          <div style="font-size:12px;color:#8b949e;margin-bottom:10px">{p2ps}</div>
          <div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap">
            <span class="b {m2c}">{m2l}</span><span class="b bb">{h2l}</span></div></div>
      </div></div>""", unsafe_allow_html=True)

    # ── EDGE BAR ──
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
      </div></div>""", unsafe_allow_html=True)

    # ── TABS ──
    t1,t2,t3,t4,t5=st.tabs(["📊 Forma & Piso","🎯 Serviço vs Retorno","🧠 Momento Psicológico","🤝 H2H & Matchup","🏆 Bottom Line"])

    # TAB 1
    with t1:
        ca,cb=st.columns(2)
        for col,pn,pm,psf,psw,psc,prank,ppts2 in [(ca,p1n,p1m,p1sf,p1sw,p1sc,p1rank,p1pts),(cb,p2n,p2m,p2sf,p2sw,p2sc,p2rank,p2pts)]:
            with col:
                l10=pm.head(10); wc=len(l10[l10["result"]=="W"]) if not l10.empty else 0
                wrp=round(wc/len(l10)*100) if len(l10)>0 else 0
                rs=f"#{prank}" if prank else "NR"; ps2=f"{ppts2:,} pts" if ppts2 else "—"
                st.markdown(f"""<div class="card">
                  <div class="sl">{pn}</div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin:10px 0 14px;gap:10px">
                    <div><div style="font-size:32px;font-family:'DM Serif Display',serif;color:#30d158">{wrp}%</div>
                      <div style="font-size:11px;color:#8b949e">Win Rate (últimos 10)</div></div>
                    <div style="text-align:center;padding:10px 13px;background:var(--el);border-radius:10px">
                      <div style="font-size:20px;font-weight:700;color:#ffd60a">{rs}</div>
                      <div style="font-size:10px;color:#8b949e">Ranking ATP</div>
                      <div style="font-size:10px;color:#484f58">{ps2}</div></div>
                    <div style="text-align:right"><div style="font-size:18px;font-weight:700">{psf}%</div>
                      <div style="font-size:11px;color:#8b949e">{surface} form (×2)</div>
                      <div style="font-size:10px;color:#484f58">{psw}/{psc} jogos</div></div>
                  </div></div>""", unsafe_allow_html=True)
                matches_tbl(pm, surface)
        st.markdown("""<div style="background:var(--el);border-radius:8px;padding:9px 14px;margin-top:10px;font-size:12px;color:#8b949e">
          ★ Jogos no mesmo piso têm <strong style="color:#f0f6fc">peso duplo</strong> · Fonte: Jeff Sackmann / Tennis Abstract
        </div>""", unsafe_allow_html=True)

    # TAB 2
    with t2:
        st.markdown(f"""<div class="card">
          <div class="sl">Comparação Service vs Return — Stats Reais ATP</div>
          <div style="display:flex;justify-content:space-between;padding:10px 0 12px;border-bottom:1px solid var(--border);margin-bottom:4px">
            <span style="font-weight:600">{p1n.split()[-1]}</span>
            <span style="font-size:10px;color:#484f58;font-family:'JetBrains Mono',monospace;letter-spacing:1px">MÉTRICA</span>
            <span style="font-weight:600">{p2n.split()[-1]}</span></div>""", unsafe_allow_html=True)
        for lbl,v1,v2 in [
            ("1º Serviço Dentro",p1s["first_srv"],p2s["first_srv"]),
            ("Pts Ganhos no 1º Serviço",p1s["pts_1st"],p2s["pts_1st"]),
            ("Pts Ganhos no 2º Serviço",p1s["pts_2nd"],p2s["pts_2nd"]),
            ("Pontos Ganhos no Return",p1s["ret"],p2s["ret"]),
            ("Break Points Salvos",p1s["bp_saved"],p2s["bp_saved"]),
            ("Break Points Convertidos",p1s["bp_conv"],p2s["bp_conv"]),
        ]: stat_bar(lbl,round(v1,1) if v1 else 0,round(v2,1) if v2 else 0)
        st.markdown("</div>",unsafe_allow_html=True)
        ca,cb=st.columns(2)
        for col,pn,ps in [(ca,p1n,p1s),(cb,p2n,p2s)]:
            with col:
                st.markdown(f"""<div class="card"><div class="sl">{pn}</div>
                  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:12px">
                    <div style="background:var(--el);border-radius:8px;padding:11px;text-align:center">
                      <div style="font-size:20px;font-weight:700;color:#30d158">{fmv(ps['aces_pm'],'')}</div>
                      <div style="font-size:10px;color:#8b949e;margin-top:2px">Aces/jogo</div></div>
                    <div style="background:var(--el);border-radius:8px;padding:11px;text-align:center">
                      <div style="font-size:20px;font-weight:700;color:#ff453a">{fmv(ps['df_pm'],'')}</div>
                      <div style="font-size:10px;color:#8b949e;margin-top:2px">DFs/jogo</div></div>
                    <div style="background:var(--el);border-radius:8px;padding:11px;text-align:center">
                      <div style="font-size:20px;font-weight:700;color:#ffd60a">{fmv(ps['first_srv'])}</div>
                      <div style="font-size:10px;color:#8b949e;margin-top:2px">1º Srv %</div></div>
                  </div></div>""", unsafe_allow_html=True)

    # TAB 3
    with t3:
        ca,cb=st.columns(2)
        for col,pn,pm2 in [(ca,p1n,p1me),(cb,p2n,p2me)]:
            with col:
                mc="#ff453a" if pm2["unstable"] else "#30d158"
                ml="⚠ MENTALMENTE INSTÁVEL" if pm2["unstable"] else "✓ MENTALMENTE ESTÁVEL"
                tbs=" ".join([f'<span class="b {"bg" if r=="W" else "br"}">{r}</span>' for r in pm2["last3"]]) or '<span style="color:#484f58">Sem tie-breaks</span>'
                st.markdown(f"""<div class="card" style="border-color:{mc}40">
                  <div class="sl">{pn}</div>
                  <div style="font-size:13px;font-weight:700;color:{mc};margin:10px 0">{ml}</div>
                  <div style="margin-bottom:14px">
                    <div style="font-size:10px;color:#8b949e;margin-bottom:6px;font-family:'JetBrains Mono',monospace;letter-spacing:1px">ÚLTIMOS TIE-BREAKS</div>
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
                  </div></div>""", unsafe_allow_html=True)
        if p1me["unstable"] and p2me["unstable"]:
            mv="⚠ Ambos instáveis — evitar Match Odds, preferir Over/Under Games."; mc2="d"
        elif p1me["unstable"]:
            mv=f"🎯 {p2n.split()[-1]} tem vantagem psicológica — value nas Match Odds."; mc2=""
        elif p2me["unstable"]:
            mv=f"🎯 {p1n.split()[-1]} tem vantagem psicológica — value nas Match Odds."; mc2=""
        else:
            mv="✓ Ambos estáveis — decidir via métricas técnicas de serviço e piso."; mc2="n"
        st.markdown(f"""<div class="vb {mc2}" style="margin-top:14px">
          <div class="sl">Veredito Psicológico</div>
          <div style="font-size:15px;color:#f0f6fc;margin-top:8px;line-height:1.7">{mv}</div>
        </div>""", unsafe_allow_html=True)

    # TAB 4
    with t4:
        st.markdown(f"""<div class="card">
          <div class="sl">Head-to-Head (últimos 3 anos)</div>
          <div style="display:flex;align-items:center;justify-content:center;gap:40px;margin:14px 0;padding:14px;background:var(--el);border-radius:10px">
            <div style="text-align:center">
              <div style="font-size:40px;font-weight:800;color:{'#30d158' if hw1>=hw2 else '#f0f6fc'}">{hw1}</div>
              <div style="font-size:12px;color:#8b949e">{p1n.split()[-1]}</div></div>
            <div style="font-size:18px;color:#484f58;font-family:'JetBrains Mono',monospace">—</div>
            <div style="text-align:center">
              <div style="font-size:40px;font-weight:800;color:{'#30d158' if hw2>=hw1 else '#f0f6fc'}">{hw2}</div>
              <div style="font-size:12px;color:#8b949e">{p2n.split()[-1]}</div></div>
          </div>
          <div class="sl" style="margin-top:14px">Últimos Confrontos Directos</div>""", unsafe_allow_html=True)
        h2h_tbl(hrec)
        st.markdown("</div>",unsafe_allow_html=True)

        st.markdown(f"""<div class="card">
          <div class="sl">Análise de Lateralidade</div>
          <div style="display:flex;justify-content:center;gap:36px;padding:14px;background:var(--el);border-radius:10px;margin:12px 0">
            <div style="text-align:center">
              <div style="font-size:26px">{'🤚' if p1h=='L' else '✋'}</div>
              <div style="font-weight:600;margin-top:4px">{p1n.split()[-1]}</div>
              <div style="font-size:11px;color:#8b949e">{'Canhoto' if p1h=='L' else 'Destro'}</div></div>
            <div style="display:flex;align-items:center;color:#484f58;font-size:18px">⟷</div>
            <div style="text-align:center">
              <div style="font-size:26px">{'🤚' if p2h=='L' else '✋'}</div>
              <div style="font-weight:600;margin-top:4px">{p2n.split()[-1]}</div>
              <div style="font-size:11px;color:#8b949e">{'Canhoto' if p2h=='L' else 'Destro'}</div></div>
          </div>
          <div style="font-size:14px;line-height:1.8;color:#c9d1d9;margin-top:10px">{htxt}</div>
        </div>""", unsafe_allow_html=True)

    # TAB 5
    with t5:
        favn=p1n if side=="p1" else (p2n if side=="p2" else "—")
        favp=pct1 if side=="p1" else (pct2 if side=="p2" else 50)
        vc="d" if side=="p2" else ("n" if side=="neutral" else "")
        mn=""
        if p1me["unstable"] and side!="p1": mn=f" ⚠ {p1n.split()[-1]} perdeu os últimos 3 tie-breaks."
        elif p2me["unstable"] and side!="p2": mn=f" ⚠ {p2n.split()[-1]} perdeu os últimos 3 tie-breaks."
        sn={"Hard":"Hard equilibrado — serviço e retorno com peso similar.","Clay":"Clay penaliza grandes servidores e amplifica o retorno.","Grass":"Grass favorece grandes servidores — 1º serviço é KPI crítico.","Carpet":"Carpet rápido — favorece servos agressivos."}.get(surface,"")
        hn=""
        if hw1+hw2>0:
            if hw1>hw2: hn=f" H2H: {p1n.split()[-1]} lidera {hw1}-{hw2}."
            elif hw2>hw1: hn=f" H2H: {p2n.split()[-1]} lidera {hw2}-{hw1}."
            else: hn=f" H2H equilibrado {hw1}-{hw2}."
        mkt="Diferencial suficiente para posição directa nas Match Odds." if abs(pct1-pct2)>=15 else "Diferencial marginal — considerar Handicap de Sets ou Total Games."

        st.markdown(f"""<div class="vb {vc}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:20px">
            <div style="flex:2;min-width:250px">
              <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#8b949e;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px">Match Odds — Veredito Final</div>
              <div style="font-family:'DM Serif Display',serif;font-size:24px;color:#f0f6fc;line-height:1.2;margin-bottom:12px">{verdict}</div>
              <div style="font-size:14px;color:#c9d1d9;line-height:1.8">{sn}{mn}{hn}<br>
                Edge: <strong style="color:{'#30d158' if side=='p1' else '#f0f6fc'}">{p1n.split()[-1]} {pct1}%</strong> vs
                <strong style="color:{'#30d158' if side=='p2' else '#f0f6fc'}">{p2n.split()[-1]} {pct2}%</strong>. {mkt}</div></div>
            <div style="flex:1;min-width:140px;text-align:center;padding:22px;background:rgba(0,0,0,.2);border-radius:12px">
              <div style="font-size:10px;color:#8b949e;margin-bottom:8px;font-family:'JetBrains Mono',monospace;letter-spacing:1px">EDGE SCORE</div>
              <div style="font-size:50px;font-family:'DM Serif Display',serif;color:{'#30d158' if side!='neutral' else '#ffd60a'}">{favp}%</div>
              <div style="font-size:12px;font-weight:600;color:#f0f6fc;margin-top:4px">{'⚡ '+favn.split()[-1] if side!='neutral' else '🎲 COIN FLIP'}</div></div></div>
          <div style="margin-top:18px;padding-top:12px;border-top:1px solid rgba(255,255,255,.07);font-size:11px;color:#484f58;font-family:'JetBrains Mono',monospace">
            Fonte: Jeff Sackmann / Tennis Abstract · ATP últimos 3 anos · Uso educativo — trading responsável.
          </div></div>""", unsafe_allow_html=True)

if __name__=="__main__":
    main()
    
