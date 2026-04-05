import streamlit as st
import requests
import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime, timedelta
import re

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Tennis Edge — Elite Trading Dashboard",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@300;400;600&family=Inter:wght@300;400;500;600&display=swap');
:root {
  --bg-primary:#080c10; --bg-card:#0d1117; --bg-elevated:#161b22;
  --border:#21262d; --accent-green:#30d158; --accent-red:#ff453a;
  --accent-amber:#ffd60a; --accent-blue:#0a84ff;
  --text-primary:#f0f6fc; --text-secondary:#8b949e; --text-muted:#484f58;
}
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{background:var(--bg-primary)!important;color:var(--text-primary)!important;font-family:'Inter',sans-serif;}
[data-testid="stHeader"]{background:transparent!important;}
::-webkit-scrollbar{width:6px;} ::-webkit-scrollbar-track{background:var(--bg-primary);} ::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
.stTextArea textarea,.stTextInput input{background:var(--bg-elevated)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--text-primary)!important;font-family:'JetBrains Mono',monospace!important;font-size:13px!important;}
.stTextArea textarea:focus,.stTextInput input:focus{border-color:var(--accent-green)!important;box-shadow:0 0 0 3px rgba(48,209,88,0.12)!important;}
div[data-baseweb="select"]>div{background:var(--bg-elevated)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--text-primary)!important;}
.stButton>button{background:linear-gradient(135deg,#30d158,#25a244)!important;color:#000!important;font-family:'Inter',sans-serif!important;font-weight:700!important;font-size:14px!important;letter-spacing:0.5px!important;border:none!important;border-radius:10px!important;padding:14px 32px!important;transition:all 0.2s ease!important;width:100%;}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 8px 24px rgba(48,209,88,0.35)!important;}
#MainMenu,footer,header{visibility:hidden!important;}
.block-container{padding-top:2rem!important;max-width:1400px!important;}
.metric-card{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:20px 24px;margin-bottom:12px;}
.data-table{width:100%;border-collapse:collapse;font-size:13px;}
.data-table th{background:var(--bg-elevated);color:var(--text-secondary);font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:1px;text-transform:uppercase;padding:10px 14px;border-bottom:1px solid var(--border);text-align:left;}
.data-table td{padding:9px 14px;border-bottom:1px solid var(--border);color:var(--text-primary);}
.data-table tr:hover td{background:var(--bg-elevated);}
.badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600;letter-spacing:0.3px;}
.badge-green{background:rgba(48,209,88,0.15);color:#30d158;border:1px solid rgba(48,209,88,0.3);}
.badge-red{background:rgba(255,69,58,0.15);color:#ff453a;border:1px solid rgba(255,69,58,0.3);}
.badge-amber{background:rgba(255,214,10,0.15);color:#ffd60a;border:1px solid rgba(255,214,10,0.3);}
.badge-blue{background:rgba(10,132,255,0.15);color:#0a84ff;border:1px solid rgba(10,132,255,0.3);}
.badge-purple{background:rgba(191,90,242,0.15);color:#bf5af2;border:1px solid rgba(191,90,242,0.3);}
.section-label{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px;}
.stat-bar-container{margin:8px 0;}
.stat-bar{height:6px;border-radius:3px;background:var(--bg-elevated);overflow:hidden;}
.stat-bar-fill{height:100%;border-radius:3px;}
.verdict-box{background:linear-gradient(135deg,rgba(48,209,88,0.08),rgba(48,209,88,0.02));border:1px solid rgba(48,209,88,0.35);border-radius:16px;padding:28px 32px;margin-top:8px;}
.verdict-box.danger{background:linear-gradient(135deg,rgba(255,69,58,0.08),rgba(255,69,58,0.02));border-color:rgba(255,69,58,0.35);}
.verdict-box.neutral{background:linear-gradient(135deg,rgba(255,214,10,0.08),rgba(255,214,10,0.02));border-color:rgba(255,214,10,0.35);}
.divider{border:none;border-top:1px solid var(--border);margin:24px 0;}
.hero-title{font-family:'DM Serif Display',serif;font-size:46px;background:linear-gradient(135deg,#f0f6fc 30%,#30d158);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1;}
.hero-sub{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:3px;color:var(--text-muted);text-transform:uppercase;}
.info-box{background:rgba(10,132,255,0.08);border:1px solid rgba(10,132,255,0.25);border-radius:10px;padding:12px 18px;font-size:13px;color:#0a84ff;margin-bottom:16px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA LOADERS
# ─────────────────────────────────────────────
BASE = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master"

@st.cache_data(ttl=3600, show_spinner=False)
def load_players():
    r = requests.get(f"{BASE}/atp_players.csv", timeout=15)
    df = pd.read_csv(StringIO(r.text), header=None,
                     names=["player_id","first_name","last_name","hand","dob","country"])
    df["full_name"] = (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).str.strip()
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def load_rankings():
    r = requests.get(f"{BASE}/atp_rankings_current.csv", timeout=15)
    df = pd.read_csv(StringIO(r.text), header=None,
                     names=["ranking_date","ranking","player_id","ranking_points"])
    df["ranking_date"] = pd.to_datetime(df["ranking_date"].astype(str), format="%Y%m%d", errors="coerce")
    latest = df["ranking_date"].max()
    return df[df["ranking_date"] == latest].copy()

@st.cache_data(ttl=3600, show_spinner=False)
def load_matches_year(year):
    r = requests.get(f"{BASE}/atp_matches_{year}.csv", timeout=20)
    if r.status_code != 200:
        return pd.DataFrame()
    return pd.read_csv(StringIO(r.text), low_memory=False)

@st.cache_data(ttl=3600, show_spinner=False)
def load_recent_matches():
    cy = datetime.now().year
    frames = [load_matches_year(y) for y in range(cy-2, cy+1)]
    frames = [f for f in frames if not f.empty]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# ─────────────────────────────────────────────
#  PLAYER SEARCH
# ─────────────────────────────────────────────
def find_player(query, players_df):
    q = query.strip().lower()
    # Exact full name
    m = players_df["full_name"].str.lower() == q
    if m.any(): return players_df[m].iloc[0]
    # Last name exact
    m = players_df["last_name"].str.lower() == q
    if m.any(): return players_df[m].iloc[0]
    # Contains in full name
    m = players_df["full_name"].str.lower().str.contains(q, na=False)
    if m.any(): return players_df[m].iloc[0]
    # Contains in last name
    m = players_df["last_name"].str.lower().str.contains(q, na=False)
    if m.any(): return players_df[m].iloc[0]
    return None

def get_ranking(pid, rankings_df):
    row = rankings_df[rankings_df["player_id"] == pid]
    if not row.empty:
        return int(row.iloc[0]["ranking"]), int(row.iloc[0]["ranking_points"])
    return None, None

# ─────────────────────────────────────────────
#  MATCH PROCESSING
# ─────────────────────────────────────────────
def get_player_matches(pid, matches_df, n=30):
    if matches_df.empty: return pd.DataFrame()
    pid = int(pid)
    def build(df, role):
        out = df.copy()
        if role == "winner":
            out["result"] = "W"
            out["opponent_name"] = out["loser_name"]
            out["opponent_rank"] = out["loser_rank"]
            for stat in ["ace","df","svpt","1stIn","1stWon","2ndWon","bpSaved","bpFaced"]:
                out[f"player_{stat}"] = out.get(f"w_{stat}", pd.Series(dtype=float))
                out[f"opp_{stat}"] = out.get(f"l_{stat}", pd.Series(dtype=float))
        else:
            out["result"] = "L"
            out["opponent_name"] = out["winner_name"]
            out["opponent_rank"] = out["winner_rank"]
            for stat in ["ace","df","svpt","1stIn","1stWon","2ndWon","bpSaved","bpFaced"]:
                out[f"player_{stat}"] = out.get(f"l_{stat}", pd.Series(dtype=float))
                out[f"opp_{stat}"] = out.get(f"w_{stat}", pd.Series(dtype=float))
        return out

    as_w = build(matches_df[matches_df["winner_id"] == pid].copy(), "winner")
    as_l = build(matches_df[matches_df["loser_id"] == pid].copy(), "loser")
    combined = pd.concat([as_w, as_l], ignore_index=True)
    combined["tourney_date"] = pd.to_datetime(combined["tourney_date"].astype(str), format="%Y%m%d", errors="coerce")
    combined = combined.sort_values("tourney_date", ascending=False)
    return combined.head(n)

def safe_pct(num, den):
    try:
        n, d = float(num), float(den)
        return round(n/d*100, 1) if d > 0 else None
    except: return None

def srv_stats(matches):
    s = {"first_srv_pct":None,"pts_won_1st":None,"pts_won_2nd":None,
         "return_pts_won":None,"aces_pm":None,"df_pm":None,
         "bp_saved_pct":None,"bp_converted_pct":None}
    if matches.empty: return s
    def ss(col):
        try: return pd.to_numeric(matches[col], errors="coerce").sum()
        except: return 0
    svpt=ss("player_svpt"); fin=ss("player_1stIn"); fwon=ss("player_1stWon")
    swon=ss("player_2ndWon"); aces=ss("player_ace"); dfs=ss("player_df")
    bps=ss("player_bpSaved"); bpf=ss("player_bpFaced")
    osvpt=ss("opp_svpt"); ofin=ss("opp_1stIn"); ofwon=ss("opp_1stWon")
    oswon=ss("opp_2ndWon"); obps=ss("opp_bpSaved"); obpf=ss("opp_bpFaced")
    s2nd = svpt - fin
    s["first_srv_pct"] = safe_pct(fin, svpt)
    s["pts_won_1st"] = safe_pct(fwon, fin)
    s["pts_won_2nd"] = safe_pct(swon, s2nd) if s2nd > 0 else None
    s["aces_pm"] = round(aces/len(matches),1) if len(matches) > 0 else None
    s["df_pm"] = round(dfs/len(matches),1) if len(matches) > 0 else None
    s["bp_saved_pct"] = safe_pct(bps, bpf)
    ret_won = osvpt - ofwon - oswon
    s["return_pts_won"] = safe_pct(ret_won, osvpt)
    s["bp_converted_pct"] = safe_pct(obpf - obps, obpf)
    return s

def surface_form(matches, surface, n=10):
    if matches.empty: return 0, 0, 0
    last = matches.head(n)
    ww, wt, sw, sc = 0, 0, 0, 0
    for _, row in last.iterrows():
        same = str(row.get("surface","")).lower() == surface.lower()
        w = 2 if same else 1
        wt += w
        if row["result"] == "W": ww += w
        if same:
            sc += 1
            if row["result"] == "W": sw += 1
    sf = round(ww/wt*100,1) if wt > 0 else 0
    return sf, sw, sc

def mental_stats(matches):
    tb_seq, tb_w, tb_l, dec_w, dec_t = [], 0, 0, 0, 0
    for _, row in matches.iterrows():
        score = str(row.get("score",""))
        result = row.get("result","")
        for s in score.split():
            if "7-6" in s or "6-7" in s:
                won = (result=="W" and "7-6" in s) or (result=="L" and "6-7" in s)
                if won: tb_w += 1; tb_seq.append("W")
                else: tb_l += 1; tb_seq.append("L")
        sets = [s for s in score.split() if re.match(r'\d+-\d+', s)]
        if len(sets) >= 3:
            dec_t += 1
            if result == "W": dec_w += 1
    last3 = tb_seq[-3:]
    total_tb = tb_w + tb_l
    return {
        "tb_won": tb_w, "tb_lost": tb_l,
        "tb_pct": round(tb_w/total_tb*100,1) if total_tb > 0 else 50.0,
        "last3": last3,
        "mentally_unstable": len(last3)==3 and all(r=="L" for r in last3),
        "dec_wins": dec_w, "dec_total": dec_t,
        "dec_pct": round(dec_w/dec_t*100,1) if dec_t > 0 else 50.0
    }

def get_h2h(p1id, p2id, matches_df):
    if matches_df.empty: return 0, 0, []
    p1id, p2id = int(p1id), int(p2id)
    h = matches_df[
        ((matches_df["winner_id"]==p1id)&(matches_df["loser_id"]==p2id))|
        ((matches_df["winner_id"]==p2id)&(matches_df["loser_id"]==p1id))
    ].copy()
    h["tourney_date"] = pd.to_datetime(h["tourney_date"].astype(str), format="%Y%m%d", errors="coerce")
    h = h.sort_values("tourney_date", ascending=False)
    w1 = len(h[h["winner_id"]==p1id])
    w2 = len(h[h["winner_id"]==p2id])
    recent = []
    for _, row in h.head(6).iterrows():
        d = row["tourney_date"].strftime("%d/%m/%y") if pd.notna(row["tourney_date"]) else "?"
        recent.append({"date":d,"winner":str(row.get("winner_name","?")),"tourney":str(row.get("tourney_name","?")),
                       "surface":str(row.get("surface","?")),"score":str(row.get("score","?"))})
    return w1, w2, recent

# ─────────────────────────────────────────────
#  EDGE SCORE
# ─────────────────────────────────────────────
def edge_score(p1sf, p2sf, p1srv, p2srv, p1m, p2m, n1, n2):
    s1, s2 = 0, 0
    # Surface form 30pts
    d = abs(p1sf-p2sf)
    if p1sf>p2sf: s1+=min(30,d*0.4)
    else: s2+=min(30,d*0.4)
    # Service 25pts
    srv1=(p1srv.get("pts_won_1st") or 65)*0.6+(p1srv.get("pts_won_2nd") or 50)*0.4
    srv2=(p2srv.get("pts_won_1st") or 65)*0.6+(p2srv.get("pts_won_2nd") or 50)*0.4
    d2=abs(srv1-srv2)
    if srv1>srv2: s1+=min(25,d2*1.2)
    else: s2+=min(25,d2*1.2)
    # Return 20pts
    r1=p1srv.get("return_pts_won") or 38; r2=p2srv.get("return_pts_won") or 38
    d3=abs(r1-r2)
    if r1>r2: s1+=min(20,d3*1.0)
    else: s2+=min(20,d3*1.0)
    # Mental 25pts
    if p1m["mentally_unstable"] and not p2m["mentally_unstable"]: s2+=25
    elif p2m["mentally_unstable"] and not p1m["mentally_unstable"]: s1+=25
    else:
        d4=abs(p1m["tb_pct"]-p2m["tb_pct"])
        if p1m["tb_pct"]>p2m["tb_pct"]: s1+=min(15,d4*0.4)
        else: s2+=min(15,d4*0.4)
    total=s1+s2
    if total==0: pct1,pct2=50,50
    else: pct1=round(s1/total*100); pct2=100-pct1
    gap=abs(pct1-pct2)
    fav=n1.split()[-1] if pct1>pct2 else n2.split()[-1]
    if gap>=20: verdict=f"FAVORITO CLARO — {fav.upper()}"; side="p1" if pct1>pct2 else "p2"
    elif gap>=10: verdict=f"LIGEIRA VANTAGEM — {fav.upper()}"; side="p1" if pct1>pct2 else "p2"
    else: verdict="MATCHUP EQUILIBRADO — SEM EDGE CLARO"; side="neutral"
    return pct1, pct2, verdict, side

def hand_analysis(h1, h2, n1, n2, surface):
    l1=n1.split()[-1]; l2=n2.split()[-1]
    if h1=="L" and h2=="R":
        return (f"**Canhoto vs Destro** — O serviço de {l1} abre o court para fora do backhand de {l2} "
                f"tanto no Ad court como no Deuce court. "
                +("Em Clay o deslize amplifica o esforço de reposicionamento do destro." if surface=="Clay"
                  else f"Em {surface} a velocidade potencia o ângulo do serviço canhoto.")
                +f" O mercado tende a sub-valorizar canhotos em confronto directo — verificar value em {l1} se odds acima de 1.85.")
    elif h1=="R" and h2=="L":
        return (f"**Destro vs Canhoto** — O serviço de {l2} isola consistentemente o backhand de {l1}. "
                +("Em Clay o ritmo lento dá tempo a {l1} para se reposicionar." if surface=="Clay"
                  else f"Em {surface} a rapidez do ponto amplifica o ângulo canhoto.")
                +f" Canhotos têm edge estatístico em tiebreaks por este padrão repetitivo — considerar value em {l2} se odds acima de 1.80.")
    else:
        h="Ambos Destros" if h1=="R" else "Ambos Canhotos"
        return (f"**{h}** — Sem factor de lateralidade. O resultado resolve-se via serviço, retorno e resistência mental. "
                f"Foco em Break Points Converted como KPI primário.")

# ─────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────
def stat_bar(label, v1, v2, unit="%"):
    v1 = v1 or 0; v2 = v2 or 0
    mx = max(v1, v2, 1)
    w1=int(v1/mx*100); w2=int(v2/mx*100)
    c1="#30d158" if v1>=v2 else "#8b949e"; c2="#30d158" if v2>v1 else "#8b949e"
    st.markdown(f"""<div class="stat-bar-container">
      <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
        <span style="color:#f0f6fc;font-weight:600">{v1}{unit}</span>
        <span style="color:#484f58;font-size:11px">{label}</span>
        <span style="color:#f0f6fc;font-weight:600">{v2}{unit}</span>
      </div>
      <div style="display:flex;gap:4px">
        <div style="flex:1"><div class="stat-bar"><div class="stat-bar-fill" style="width:{w1}%;background:{c1};float:right"></div></div></div>
        <div style="flex:1"><div class="stat-bar"><div class="stat-bar-fill" style="width:{w2}%;background:{c2}"></div></div></div>
      </div></div>""", unsafe_allow_html=True)

def matches_table(matches, surface):
    if matches.empty:
        st.markdown('<div style="color:#484f58;font-size:13px;padding:12px">Sem dados disponíveis.</div>', unsafe_allow_html=True)
        return
    scls={"Hard":"badge-blue","Clay":"badge-amber","Grass":"badge-green","Carpet":"badge-purple"}
    rows=""
    for _, m in matches.head(10).iterrows():
        res=m.get("result","?")
        rb=f'<span class="badge badge-green">W</span>' if res=="W" else f'<span class="badge badge-red">L</span>'
        surf=str(m.get("surface","?"))
        sc=scls.get(surf,"badge-blue")
        same="★ " if surf.lower()==surface.lower() else ""
        score=str(m.get("score","")).strip()
        opp=str(m.get("opponent_name","?")).strip()
        opp_r=m.get("opponent_rank","")
        opp_rs=f"#{int(opp_r)}" if pd.notna(opp_r) and str(opp_r).strip() not in ["","nan"] else ""
        date=m.get("tourney_date","")
        ds=date.strftime("%d/%m/%y") if hasattr(date,"strftime") and pd.notna(date) else str(date)[:10]
        tourney=str(m.get("tourney_name","")).strip()[:22]
        rows+=f"""<tr>
          <td style="color:#8b949e;white-space:nowrap">{ds}</td>
          <td><div>{opp}</div><div style="font-size:10px;color:#484f58">{opp_rs}</div></td>
          <td style="color:#8b949e">{tourney}</td>
          <td><span class="badge {sc}">{same}{surf}</span></td>
          <td>{rb}</td>
          <td style="font-family:'JetBrains Mono',monospace;font-size:11px">{score}</td></tr>"""
    st.markdown(f"""<table class="data-table"><thead><tr>
      <th>Data</th><th>Adversário</th><th>Torneio</th><th>Piso</th><th>Res</th><th>Score</th>
      </tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)

def h2h_table(recent):
    if not recent:
        st.markdown('<div style="color:#484f58;font-size:13px;padding:8px">Sem confrontos directos nos dados (últimos 3 anos).</div>', unsafe_allow_html=True)
        return
    scls={"Hard":"badge-blue","Clay":"badge-amber","Grass":"badge-green","Carpet":"badge-purple"}
    rows=""
    for m in recent:
        sc=scls.get(m["surface"],"badge-blue")
        rows+=f"""<tr>
          <td style="color:#8b949e">{m['date']}</td>
          <td style="font-weight:600;color:#30d158">{m['winner']}</td>
          <td style="color:#8b949e">{m['tourney']}</td>
          <td><span class="badge {sc}">{m['surface']}</span></td>
          <td style="font-family:'JetBrains Mono',monospace;font-size:11px">{m['score']}</td></tr>"""
    st.markdown(f"""<table class="data-table"><thead><tr>
      <th>Data</th><th>Vencedor</th><th>Torneio</th><th>Piso</th><th>Score</th>
      </tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)

def fmt(v, u="%"):
    return f"{v}{u}" if v is not None else "N/D"

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    st.markdown("""
    <div style="text-align:center;padding:36px 0 16px">
      <div class="hero-sub">Tennis Edge Analytics · Jeff Sackmann / Tennis Abstract</div>
      <div class="hero-title">Elite Trading Dashboard</div>
      <div style="color:#484f58;font-size:12px;margin-top:8px;font-family:'JetBrains Mono',monospace">
        Rankings ATP reais · Últimos 3 anos de resultados · H2H histórico · Stats de serviço reais
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([2,2,1,1])
    with c1:
        st.markdown('<div class="section-label">Jogador 1</div>', unsafe_allow_html=True)
        p1_in = st.text_input("p1","",placeholder="Ex: Djokovic, Sinner, Alcaraz...",label_visibility="collapsed")
    with c2:
        st.markdown('<div class="section-label">Jogador 2</div>', unsafe_allow_html=True)
        p2_in = st.text_input("p2","",placeholder="Ex: Medvedev, Zverev, Rune...",label_visibility="collapsed")
    with c3:
        st.markdown('<div class="section-label">Piso</div>', unsafe_allow_html=True)
        surface = st.selectbox("surf",["Hard","Clay","Grass","Carpet"],label_visibility="collapsed")
    with c4:
        st.markdown('<div class="section-label">&nbsp;</div>', unsafe_allow_html=True)
        go = st.button("⚡ Gerar Relatório")

    st.markdown("""<div class="info-box">
      💡 <strong>Dados reais</strong> Jeff Sackmann / Tennis Abstract — Rankings ATP actuais, 
      últimos 3 anos de resultados, stats de serviço e H2H histórico. 
      Escreve o apelido: <em>Djokovic</em>, <em>Sinner</em>, <em>Alcaraz</em>, <em>Medvedev</em>...
    </div>""", unsafe_allow_html=True)

    if not go:
        st.markdown("""<div style="text-align:center;padding:60px 20px;color:#484f58">
          <div style="font-size:44px;margin-bottom:12px">🎾</div>
          <div style="font-family:'DM Serif Display',serif;font-size:20px;color:#8b949e">Pronto para analisar</div>
          <div style="font-size:12px;margin-top:8px;font-family:'JetBrains Mono',monospace">
            Preenche os nomes dos dois jogadores e clica Gerar Relatório
          </div></div>""", unsafe_allow_html=True)
        return

    if not p1_in.strip() or not p2_in.strip():
        st.error("Preenche os dois nomes."); return

    with st.spinner("A carregar dados ATP (Jeff Sackmann)..."):
        try:
            players_df = load_players()
            rankings_df = load_rankings()
            matches_df = load_recent_matches()
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}"); return

    p1r = find_player(p1_in, players_df)
    p2r = find_player(p2_in, players_df)
    if p1r is None: st.error(f"'{p1_in}' não encontrado. Tenta o apelido completo."); return
    if p2r is None: st.error(f"'{p2_in}' não encontrado. Tenta o apelido completo."); return

    p1id=p1r["player_id"]; p2id=p2r["player_id"]
    p1n=p1r["full_name"]; p2n=p2r["full_name"]
    p1h=str(p1r.get("hand","R")).strip().upper()
    p2h=str(p2r.get("hand","R")).strip().upper()

    p1rank,p1pts=get_ranking(p1id,rankings_df)
    p2rank,p2pts=get_ranking(p2id,rankings_df)

    with st.spinner("A processar matches..."):
        p1m=get_player_matches(p1id,matches_df,30)
        p2m=get_player_matches(p2id,matches_df,30)

    p1sf,p1sw,p1sc=surface_form(p1m,surface)
    p2sf,p2sw,p2sc=surface_form(p2m,surface)
    p1srv=srv_stats(p1m.head(15)); p2srv=srv_stats(p2m.head(15))
    p1ment=mental_stats(p1m.head(20)); p2ment=mental_stats(p2m.head(20))
    h2hw1,h2hw2,h2h_recent=get_h2h(p1id,p2id,matches_df)
    pct1,pct2,verdict,side=edge_score(p1sf,p2sf,p1srv,p2srv,p1ment,p2ment,p1n,p2n)
    hand_txt=hand_analysis(p1h,p2h,p1n,p2n,surface)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── HEADER ──
    r1s=f"#{p1rank}" if p1rank else "NR"; r2s=f"#{p2rank}" if p2rank else "NR"
    p1s=f"{p1pts:,} pts" if p1pts else ""; p2s=f"{p2pts:,} pts" if p2pts else ""
    h1l="Canhoto 🤚" if p1h=="L" else "Destro ✋"
    h2l="Canhoto 🤚" if p2h=="L" else "Destro ✋"
    m1c="badge-red" if p1ment["mentally_unstable"] else "badge-green"
    m2c="badge-red" if p2ment["mentally_unstable"] else "badge-green"
    m1l="⚠ INSTÁVEL" if p1ment["mentally_unstable"] else "✓ ESTÁVEL"
    m2l="⚠ INSTÁVEL" if p2ment["mentally_unstable"] else "✓ ESTÁVEL"

    st.markdown(f"""
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:16px;padding:28px 36px;margin-bottom:20px">
      <div class="section-label">Análise de Partida — Dados Reais ATP</div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-top:14px;flex-wrap:wrap;gap:20px">
        <div style="text-align:center;flex:1;min-width:180px">
          <div style="font-family:'DM Serif Display',serif;font-size:26px">{p1n}</div>
          <div style="font-size:34px;font-weight:800;color:#30d158;margin:4px 0">{r1s}</div>
          <div style="font-size:12px;color:#8b949e;margin-bottom:10px">{p1s}</div>
          <div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap">
            <span class="badge {m1c}">{m1l}</span>
            <span class="badge badge-blue">{h1l}</span>
          </div>
        </div>
        <div style="text-align:center;padding:0 20px">
          <div style="font-family:'JetBrains Mono',monospace;font-size:20px;color:#484f58">VS</div>
          <div style="margin-top:10px"><span class="badge badge-amber">{surface}</span></div>
          <div style="margin-top:8px;font-size:11px;color:#484f58;font-family:'JetBrains Mono',monospace">H2H {h2hw1}–{h2hw2}</div>
        </div>
        <div style="text-align:center;flex:1;min-width:180px">
          <div style="font-family:'DM Serif Display',serif;font-size:26px">{p2n}</div>
          <div style="font-size:34px;font-weight:800;color:#30d158;margin:4px 0">{r2s}</div>
          <div style="font-size:12px;color:#8b949e;margin-bottom:10px">{p2s}</div>
          <div style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap">
            <span class="badge {m2c}">{m2l}</span>
            <span class="badge badge-blue">{h2l}</span>
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── EDGE BAR ──
    st.markdown(f"""
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:20px 28px;margin-bottom:20px">
      <div class="section-label">Edge Score — Surface-Weighted Analysis</div>
      <div style="display:flex;gap:8px;margin-top:14px;align-items:center">
        <div style="color:#f0f6fc;font-weight:700;font-size:16px;min-width:44px">{pct1}%</div>
        <div style="flex:1;height:12px;background:var(--bg-elevated);border-radius:6px;overflow:hidden">
          <div style="display:flex;height:100%">
            <div style="width:{pct1}%;background:linear-gradient(90deg,#30d158,#25a244);border-radius:6px 0 0 6px"></div>
            <div style="width:{pct2}%;background:linear-gradient(90deg,#ff453a,#cc3730);border-radius:0 6px 6px 0"></div>
          </div>
        </div>
        <div style="color:#f0f6fc;font-weight:700;font-size:16px;min-width:44px;text-align:right">{pct2}%</div>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:5px">
        <div style="font-size:11px;color:#8b949e;font-family:'JetBrains Mono',monospace">{p1n.split()[-1].upper()}</div>
        <div style="font-size:11px;color:#8b949e;font-family:'JetBrains Mono',monospace">{p2n.split()[-1].upper()}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── TABS ──
    tab1,tab2,tab3,tab4,tab5 = st.tabs([
        "📊 Forma & Piso","🎯 Serviço vs Retorno",
        "🧠 Momento Psicológico","🤝 H2H & Matchup","🏆 Bottom Line"])

    # TAB 1
    with tab1:
        ca,cb=st.columns(2)
        for col,pn,pm,psf,psw,psc,prank,ppts2 in [
            (ca,p1n,p1m,p1sf,p1sw,p1sc,p1rank,p1pts),
            (cb,p2n,p2m,p2sf,p2sw,p2sc,p2rank,p2pts)]:
            with col:
                last10=pm.head(10)
                wr=len(last10[last10["result"]=="W"]) if not last10.empty else 0
                tot=len(last10)
                wrp=round(wr/tot*100) if tot>0 else 0
                rs=f"#{prank}" if prank else "NR"
                ps2=f"{ppts2:,} pts" if ppts2 else "—"
                st.markdown(f"""<div class="metric-card">
                  <div class="section-label">{pn}</div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin:10px 0 14px;flex-wrap:wrap;gap:10px">
                    <div>
                      <div style="font-size:34px;font-family:'DM Serif Display',serif;color:#30d158">{wrp}%</div>
                      <div style="font-size:11px;color:#8b949e">Win Rate (últimos 10)</div>
                    </div>
                    <div style="text-align:center;padding:10px 14px;background:var(--bg-elevated);border-radius:10px">
                      <div style="font-size:22px;font-weight:700;color:#ffd60a">{rs}</div>
                      <div style="font-size:10px;color:#8b949e">Ranking ATP</div>
                      <div style="font-size:10px;color:#484f58">{ps2}</div>
                    </div>
                    <div style="text-align:right">
                      <div style="font-size:20px;font-weight:700">{psf}%</div>
                      <div style="font-size:11px;color:#8b949e">{surface} (×2 peso)</div>
                      <div style="font-size:10px;color:#484f58">{psw}/{psw+max(0,psf and psw)} • {psw}/{pssc if (pssc:=pssc) else pssc}</div>
                    </div>
                  </div>
                </div>""".replace("pssc:=pssc","pssc:=psc").replace("pssc","psc"), unsafe_allow_html=True)

                # fix simplified
                st.markdown(f"""<div class="metric-card">
                  <div class="section-label">{pn}</div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin:10px 0 14px;gap:10px">
                    <div><div style="font-size:34px;font-family:'DM Serif Display',serif;color:#30d158">{wrp}%</div>
                      <div style="font-size:11px;color:#8b949e">Win Rate (últimos 10)</div></div>
                    <div style="text-align:center;padding:10px 14px;background:var(--bg-elevated);border-radius:10px">
                      <div style="font-size:22px;font-weight:700;color:#ffd60a">{rs}</div>
                      <div style="font-size:10px;color:#8b949e">Ranking ATP</div>
                      <div style="font-size:10px;color:#484f58">{ps2}</div></div>
                    <div style="text-align:right"><div style="font-size:20px;font-weight:700">{psf}%</div>
                      <div style="font-size:11px;color:#8b949e">{surface} form (×2)</div>
                      <div style="font-size:10px;color:#484f58">{psw}/{psc} jogos</div></div>
                  </div></div>""", unsafe_allow_html=True)

                matches_table(pm, surface)

        st.markdown("""<div style="background:var(--bg-elevated);border-radius:8px;padding:10px 16px;margin-top:12px;font-size:12px;color:#8b949e">
          ★ Jogos no mesmo piso têm <strong style="color:#f0f6fc">peso duplo</strong> no Surface Form Score &nbsp;|&nbsp; Fonte: Jeff Sackmann / Tennis Abstract
        </div>""", unsafe_allow_html=True)

    # TAB 2
    with tab2:
        st.markdown(f"""<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:22px;margin-bottom:16px">
          <div class="section-label">Comparação Service vs Return — Stats Reais ATP</div>
          <div style="display:flex;justify-content:space-between;padding:10px 0 12px;border-bottom:1px solid var(--border);margin-bottom:4px">
            <span style="font-weight:600">{p1n.split()[-1]}</span>
            <span style="font-size:10px;color:#484f58;font-family:'JetBrains Mono',monospace;letter-spacing:1px">MÉTRICA</span>
            <span style="font-weight:600">{p2n.split()[-1]}</span>
          </div>""", unsafe_allow_html=True)

        for label,v1,v2 in [
            ("1º Serviço Dentro",p1srv["first_srv_pct"],p2srv["first_srv_pct"]),
            ("Pts Ganhos no 1º Serviço",p1srv["pts_won_1st"],p2srv["pts_won_1st"]),
            ("Pts Ganhos no 2º Serviço",p1srv["pts_won_2nd"],p2srv["pts_won_2nd"]),
            ("Pontos Ganhos no Return",p1srv["return_pts_won"],p2srv["return_pts_won"]),
            ("Break Points Salvos",p1srv["bp_saved_pct"],p2srv["bp_saved_pct"]),
            ("Break Points Convertidos",p1srv["bp_converted_pct"],p2srv["bp_converted_pct"]),
        ]:
            stat_bar(label,round(v1,1) if v1 else 0,round(v2,1) if v2 else 0)
        st.markdown("</div>",unsafe_allow_html=True)

        ca,cb=st.columns(2)
        for col,pn,ps in [(ca,p1n,p1srv),(cb,p2n,p2srv)]:
            with col:
                st.markdown(f"""<div class="metric-card">
                  <div class="section-label">{pn}</div>
                  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:12px">
                    <div style="background:var(--bg-elevated);border-radius:8px;padding:12px;text-align:center">
                      <div style="font-size:22px;font-weight:700;color:#30d158">{fmt(ps['aces_pm'],'')}</div>
                      <div style="font-size:10px;color:#8b949e;margin-top:2px">Aces/jogo</div></div>
                    <div style="background:var(--bg-elevated);border-radius:8px;padding:12px;text-align:center">
                      <div style="font-size:22px;font-weight:700;color:#ff453a">{fmt(ps['df_pm'],'')}</div>
                      <div style="font-size:10px;color:#8b949e;margin-top:2px">DFs/jogo</div></div>
                    <div style="background:var(--bg-elevated);border-radius:8px;padding:12px;text-align:center">
                      <div style="font-size:22px;font-weight:700;color:#ffd60a">{fmt(ps['first_srv_pct'])}</div>
                      <div style="font-size:10px;color:#8b949e;margin-top:2px">1º Srv %</div></div>
                  </div></div>""", unsafe_allow_html=True)

    # TAB 3
    with tab3:
        ca,cb=st.columns(2)
        for col,pn,pm2 in [(ca,p1n,p1ment),(cb,p2n,p2ment)]:
            with col:
                mc="#ff453a" if pm2["mentally_unstable"] else "#30d158"
                ml="⚠ MENTALMENTE INSTÁVEL" if pm2["mentally_unstable"] else "✓ MENTALMENTE ESTÁVEL"
                tbs=" ".join([f'<span class="badge {"badge-green" if r=="W" else "badge-red"}">{r}</span>' for r in pm2["last3"]]) or '<span style="color:#484f58">Sem tie-breaks nos dados</span>'
                ttb=pm2["tb_won"]+pm2["tb_lost"]
                st.markdown(f"""<div class="metric-card" style="border-color:{mc}40">
                  <div class="section-label">{pn}</div>
                  <div style="font-size:14px;font-weight:700;color:{mc};margin:10px 0">{ml}</div>
                  <div style="margin-bottom:14px">
                    <div style="font-size:10px;color:#8b949e;margin-bottom:6px;font-family:'JetBrains Mono',monospace;letter-spacing:1px">ÚLTIMOS TIE-BREAKS</div>
                    <div style="display:flex;gap:5px;flex-wrap:wrap">{tbs}</div></div>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
                    <div style="background:var(--bg-elevated);border-radius:8px;padding:12px">
                      <div style="font-size:20px;font-weight:700">{pm2['tb_won']}/{ttb}</div>
                      <div style="font-size:10px;color:#8b949e">Tie-Breaks</div>
                      <div style="font-size:14px;color:{'#30d158' if pm2['tb_pct']>=50 else '#ff453a'};font-weight:600">{pm2['tb_pct']}%</div></div>
                    <div style="background:var(--bg-elevated);border-radius:8px;padding:12px">
                      <div style="font-size:20px;font-weight:700">{pm2['dec_wins']}/{pm2['dec_total']}</div>
                      <div style="font-size:10px;color:#8b949e">Sets Decisivos</div>
                      <div style="font-size:14px;color:{'#30d158' if pm2['dec_pct']>=50 else '#ff453a'};font-weight:600">{pm2['dec_pct']}%</div></div>
                  </div></div>""", unsafe_allow_html=True)

        if p1ment["mentally_unstable"] and p2ment["mentally_unstable"]:
            mv="⚠ Ambos instáveis — evitar Match Odds, preferir Over/Under Games."; mc2="danger"
        elif p1ment["mentally_unstable"]:
            mv=f"🎯 {p2n.split()[-1]} tem vantagem psicológica — value nas Match Odds."; mc2=""
        elif p2ment["mentally_unstable"]:
            mv=f"🎯 {p1n.split()[-1]} tem vantagem psicológica — value nas Match Odds."; mc2=""
        else:
            mv="✓ Ambos estáveis mentalmente — decidir via métricas técnicas."; mc2="neutral"
        st.markdown(f"""<div class="verdict-box {mc2}" style="margin-top:14px">
          <div class="section-label">Veredito Psicológico</div>
          <div style="font-size:15px;color:#f0f6fc;margin-top:8px;line-height:1.7">{mv}</div>
        </div>""", unsafe_allow_html=True)

    # TAB 4
    with tab4:
        st.markdown(f"""<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:22px;margin-bottom:16px">
          <div class="section-label">Head-to-Head Histórico (últimos 3 anos)</div>
          <div style="display:flex;align-items:center;justify-content:center;gap:40px;margin:16px 0;padding:16px;background:var(--bg-elevated);border-radius:10px">
            <div style="text-align:center">
              <div style="font-size:42px;font-weight:800;color:#{'30d158' if h2hw1>=h2hw2 else 'f0f6fc'}">{h2hw1}</div>
              <div style="font-size:12px;color:#8b949e">{p1n.split()[-1]}</div></div>
            <div style="font-size:20px;color:#484f58;font-family:'JetBrains Mono',monospace">—</div>
            <div style="text-align:center">
              <div style="font-size:42px;font-weight:800;color:#{'30d158' if h2hw2>=h2hw1 else 'f0f6fc'}">{h2hw2}</div>
              <div style="font-size:12px;color:#8b949e">{p2n.split()[-1]}</div></div>
          </div>
          <div class="section-label" style="margin-top:16px">Últimos Confrontos Directos</div>""", unsafe_allow_html=True)
        h2h_table(h2h_recent)
        st.markdown("</div>",unsafe_allow_html=True)

        st.markdown(f"""<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:22px">
          <div class="section-label">Análise de Lateralidade</div>
          <div style="display:flex;justify-content:center;gap:40px;padding:16px;background:var(--bg-elevated);border-radius:10px;margin:12px 0">
            <div style="text-align:center">
              <div style="font-size:28px">{'🤚' if p1h=='L' else '✋'}</div>
              <div style="font-weight:600;margin-top:4px">{p1n.split()[-1]}</div>
              <div style="font-size:11px;color:#8b949e">{'Canhoto' if p1h=='L' else 'Destro'}</div></div>
            <div style="display:flex;align-items:center;color:#484f58;font-size:20px">⟷</div>
            <div style="text-align:center">
              <div style="font-size:28px">{'🤚' if p2h=='L' else '✋'}</div>
              <div style="font-weight:600;margin-top:4px">{p2n.split()[-1]}</div>
              <div style="font-size:11px;color:#8b949e">{'Canhoto' if p2h=='L' else 'Destro'}</div></div>
          </div>
          <div style="font-size:14px;line-height:1.8;color:#c9d1d9;margin-top:10px">{hand_txt}</div>
        </div>""", unsafe_allow_html=True)

    # TAB 5 — BOTTOM LINE
    with tab5:
        favn=p1n if side=="p1" else (p2n if side=="p2" else "—")
        favp=pct1 if side=="p1" else (pct2 if side=="p2" else 50)
        vc="danger" if side=="p2" else ("neutral" if side=="neutral" else "")
        mn=""
        if p1ment["mentally_unstable"] and side!="p1": mn=f" ⚠ {p1n.split()[-1]} perdeu os últimos 3 tie-breaks."
        elif p2ment["mentally_unstable"] and side!="p2": mn=f" ⚠ {p2n.split()[-1]} perdeu os últimos 3 tie-breaks."
        sn={"Hard":"Hard equilibrado — serviço e retorno têm peso similar.",
            "Clay":"Clay penaliza grandes servidores e amplifica o retorno.",
            "Grass":"Grass favorece grandes servidores — 1º serviço é KPI crítico.",
            "Carpet":"Carpet rápido — favorece servos agressivos."}.get(surface,"")
        hn=""
        if h2hw1+h2hw2>0:
            if h2hw1>h2hw2: hn=f" H2H: {p1n.split()[-1]} lidera {h2hw1}-{h2hw2}."
            elif h2hw2>h2hw1: hn=f" H2H: {p2n.split()[-1]} lidera {h2hw2}-{h2hw1}."
            else: hn=f" H2H equilibrado {h2hw1}-{h2hw2}."
        mkt="Diferencial suficiente para posição directa nas Match Odds." if abs(pct1-pct2)>=15 else "Diferencial marginal — considerar Handicap de Sets ou Total Games."

        st.markdown(f"""<div class="verdict-box {vc}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:20px">
            <div style="flex:2;min-width:260px">
              <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#8b949e;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px">Match Odds — Veredito Final</div>
              <div style="font-family:'DM Serif Display',serif;font-size:26px;color:#f0f6fc;line-height:1.2;margin-bottom:14px">{verdict}</div>
              <div style="font-size:14px;color:#c9d1d9;line-height:1.8">{sn}{mn}{hn}<br>
                Edge: <strong style="color:{'#30d158' if side=='p1' else '#f0f6fc'}">{p1n.split()[-1]} {pct1}%</strong> vs
                <strong style="color:{'#30d158' if side=='p2' else '#f0f6fc'}">{p2n.split()[-1]} {pct2}%</strong>. {mkt}
              </div></div>
            <div style="flex:1;min-width:150px;text-align:center;padding:24px;background:rgba(0,0,0,0.2);border-radius:12px">
              <div style="font-size:10px;color:#8b949e;margin-bottom:8px;font-family:'JetBrains Mono',monospace;letter-spacing:1px">EDGE SCORE</div>
              <div style="font-size:52px;font-family:'DM Serif Display',serif;color:{'#30d158' if side!='neutral' else '#ffd60a'}">{favp}%</div>
              <div style="font-size:13px;font-weight:600;color:#f0f6fc;margin-top:4px">{'⚡ '+favn.split()[-1] if side!='neutral' else '🎲 COIN FLIP'}</div>
            </div></div>
          <div style="margin-top:20px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.07);font-size:11px;color:#484f58;font-family:'JetBrains Mono',monospace">
            Fonte: Jeff Sackmann / Tennis Abstract · ATP últimos 3 anos · Uso educativo — trading responsável.
          </div></div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    
