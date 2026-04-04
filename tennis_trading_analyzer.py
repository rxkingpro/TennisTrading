import streamlit as st
import requests
import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import random
from datetime import datetime, timedelta
import time

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
#  GLOBAL CSS — DARK LUXURY AESTHETIC
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@300;400;600&family=Inter:wght@300;400;500;600&display=swap');

:root {
  --bg-primary: #080c10;
  --bg-card: #0d1117;
  --bg-elevated: #161b22;
  --border: #21262d;
  --border-glow: #30d158;
  --accent-green: #30d158;
  --accent-red: #ff453a;
  --accent-amber: #ffd60a;
  --accent-blue: #0a84ff;
  --text-primary: #f0f6fc;
  --text-secondary: #8b949e;
  --text-muted: #484f58;
  --gold: #d4a843;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  background: var(--bg-primary) !important;
  color: var(--text-primary) !important;
  font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--bg-card) !important; }
section[data-testid="stSidebar"] > div { background: var(--bg-card) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* Inputs */
.stTextArea textarea, .stTextInput input {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text-primary) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 13px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border-color: var(--accent-green) !important;
  box-shadow: 0 0 0 3px rgba(48,209,88,0.12) !important;
}

/* Buttons */
.stButton > button {
  background: linear-gradient(135deg, #30d158, #25a244) !important;
  color: #000 !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  letter-spacing: 0.5px !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 14px 32px !important;
  transition: all 0.2s ease !important;
  width: 100%;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 8px 24px rgba(48,209,88,0.35) !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding-top: 2rem !important; max-width: 1400px !important; }

/* Metric cards */
.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 12px;
  transition: border-color 0.2s;
}
.metric-card:hover { border-color: var(--border-glow); }

/* Table styles */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.data-table th {
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 1px;
  text-transform: uppercase;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  text-align: left;
}
.data-table td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}
.data-table tr:hover td { background: var(--bg-elevated); }

/* Status badges */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.badge-green { background: rgba(48,209,88,0.15); color: #30d158; border: 1px solid rgba(48,209,88,0.3); }
.badge-red { background: rgba(255,69,58,0.15); color: #ff453a; border: 1px solid rgba(255,69,58,0.3); }
.badge-amber { background: rgba(255,214,10,0.15); color: #ffd60a; border: 1px solid rgba(255,214,10,0.3); }
.badge-blue { background: rgba(10,132,255,0.15); color: #0a84ff; border: 1px solid rgba(10,132,255,0.3); }

/* Section headers */
.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 8px;
}

/* Progress bar custom */
.stat-bar-container { margin: 6px 0; }
.stat-bar-label { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px; }
.stat-bar { height: 6px; border-radius: 3px; background: var(--bg-elevated); overflow: hidden; }
.stat-bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s ease; }

/* Verdict box */
.verdict-box {
  background: linear-gradient(135deg, rgba(48,209,88,0.08), rgba(48,209,88,0.03));
  border: 1px solid rgba(48,209,88,0.4);
  border-radius: 16px;
  padding: 28px 32px;
  margin-top: 8px;
}
.verdict-box.danger {
  background: linear-gradient(135deg, rgba(255,69,58,0.08), rgba(255,69,58,0.03));
  border-color: rgba(255,69,58,0.4);
}
.verdict-box.neutral {
  background: linear-gradient(135deg, rgba(255,214,10,0.08), rgba(255,214,10,0.03));
  border-color: rgba(255,214,10,0.4);
}

/* Divider */
.divider { border: none; border-top: 1px solid var(--border); margin: 24px 0; }

/* Alert box */
.alert-box {
  background: rgba(255,214,10,0.08);
  border: 1px solid rgba(255,214,10,0.3);
  border-radius: 10px;
  padding: 14px 18px;
  font-size: 13px;
  color: var(--accent-amber);
  margin-bottom: 16px;
}

/* Hero title */
.hero-title {
  font-family: 'DM Serif Display', serif;
  font-size: 48px;
  background: linear-gradient(135deg, #f0f6fc 30%, #30d158);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
  margin-bottom: 8px;
}
.hero-sub {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  letter-spacing: 3px;
  color: var(--text-muted);
  text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SCRAPER ENGINE
# ─────────────────────────────────────────────
def try_scrape_url(url: str):
    """Attempt to scrape the match page using cloudscraper or requests."""
    try:
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        resp = scraper.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.text, None
        return None, f"HTTP {resp.status_code} — site bloqueou o pedido."
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────
#  PARSER — Extract player names from HTML
# ─────────────────────────────────────────────
def parse_players_from_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    players = []

    # Flashscore patterns
    patterns = [
        {"class_": re.compile(r"participant__participantName|duelParticipant__name|home.*name|away.*name", re.I)},
        {"class_": re.compile(r"homeParticipant|awayParticipant", re.I)},
    ]
    for pat in patterns:
        found = soup.find_all(True, pat)
        names = [el.get_text(strip=True) for el in found if el.get_text(strip=True)]
        if len(names) >= 2:
            players = names[:2]
            break

    # Generic fallback — title tag
    if len(players) < 2:
        title = soup.title.string if soup.title else ""
        if " - " in title or " vs " in title.lower():
            sep = " - " if " - " in title else " vs "
            parts = title.split(sep)
            if len(parts) >= 2:
                players = [parts[0].strip(), parts[1].strip().split("|")[0].strip()]

    return players if len(players) >= 2 else None


def extract_match_meta(html: str):
    """Try to extract surface, tournament, round from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    meta = {"surface": None, "tournament": None, "round": None}

    text = soup.get_text(" ", strip=True).lower()
    surfaces = {"clay": "Clay", "hard": "Hard", "grass": "Grass", "carpet": "Carpet (Indoor)"}
    for key, val in surfaces.items():
        if key in text:
            meta["surface"] = val
            break

    rounds_kw = ["final", "semifinal", "quarterfinal", "r16", "r32", "r64", "r128", "round"]
    for r in rounds_kw:
        if r in text:
            meta["round"] = r.title()
            break

    return meta


# ─────────────────────────────────────────────
#  DATA SIMULATION ENGINE
#  (realistic stat generation based on player name seed)
# ─────────────────────────────────────────────
def seed_from_name(name: str) -> int:
    return sum(ord(c) for c in name)


def generate_player_data(name: str, surface: str = "Hard"):
    seed = seed_from_name(name)
    rng = random.Random(seed)

    surfaces = ["Hard", "Clay", "Grass", "Carpet (Indoor)"]
    hand_options = ["Right", "Left"]
    handedness = hand_options[seed % 5 == 0]  # ~20% left-handed

    # Last 10 matches
    matches = []
    surface_wins = 0
    surface_count = 0
    for i in range(10):
        match_surface = rng.choice(surfaces)
        opponent_rating = rng.randint(60, 95)
        is_same_surface = match_surface == surface
        # Weight: better perf on same surface
        win_prob = 0.55 + (0.1 if is_same_surface else 0) - (opponent_rating - 75) * 0.005
        win_prob = max(0.2, min(0.85, win_prob))
        won = rng.random() < win_prob
        score_sets = []
        sets_won = 0
        sets_lost = 0
        tb_won = 0
        tb_lost = 0
        for s in range(rng.randint(2, 3)):
            if rng.random() < 0.2:
                tb_result = rng.random() < 0.5
                if tb_result:
                    score_sets.append("7-6")
                    sets_won += 1
                    tb_won += 1
                else:
                    score_sets.append("6-7")
                    sets_lost += 1
                    tb_lost += 1
            else:
                p = rng.randint(4, 6)
                o = rng.randint(1, 4)
                if p > o:
                    score_sets.append(f"{p}-{o}")
                    sets_won += 1
                else:
                    score_sets.append(f"{o}-{p}")
                    sets_lost += 1

        days_ago = rng.randint(3, 90)
        match_date = (datetime.now() - timedelta(days=days_ago)).strftime("%d/%m/%y")
        tour = rng.choice(["ATP", "ATP 250", "ATP 500", "Masters", "Grand Slam"])
        opp_name = rng.choice([
            "Djokovic N.", "Alcaraz C.", "Medvedev D.", "Zverev A.", "Rune H.",
            "Fritz T.", "De Minaur A.", "Hurkacz H.", "Tsitsipas S.", "Ruud C.",
            "Norrie C.", "Dimitrov G.", "Paul T.", "Tiafoe F.", "Musetti L."
        ])

        if is_same_surface:
            surface_count += 1
            if won:
                surface_wins += 1

        matches.append({
            "date": match_date,
            "opponent": opp_name,
            "surface": match_surface,
            "result": "W" if won else "L",
            "score": " ".join(score_sets),
            "tb_won": tb_won,
            "tb_lost": tb_lost,
            "same_surface": is_same_surface,
            "deciding_set": sets_won + sets_lost >= 3,
            "won_deciding": won and sets_won + sets_lost >= 3,
        })

    # Aggregate stats
    wins = sum(1 for m in matches if m["result"] == "W")
    total_tb = sum(m["tb_won"] + m["tb_lost"] for m in matches)
    tb_won_total = sum(m["tb_won"] for m in matches)
    tb_lost_total = sum(m["tb_lost"] for m in matches)
    deciding_set_games = [m for m in matches if m["deciding_set"]]
    deciding_set_wins = sum(1 for m in deciding_set_games if m["won_deciding"])

    # Last 3 tiebreaks
    last_tb_results = []
    for m in matches:
        last_tb_results.extend(["W"] * m["tb_won"] + ["L"] * m["tb_lost"])
    last_3_tb = last_tb_results[-3:] if len(last_tb_results) >= 3 else last_tb_results
    mentally_unstable = len(last_3_tb) >= 3 and all(r == "L" for r in last_3_tb)

    # Service stats
    first_srv_pct = rng.randint(58, 78)
    pts_won_1st_srv = rng.randint(68, 82)
    pts_won_2nd_srv = rng.randint(42, 58)
    return_pts_won = rng.randint(32, 48)
    aces_per_match = round(rng.uniform(3, 14), 1)
    df_per_match = round(rng.uniform(1, 5), 1)
    bp_saved_pct = rng.randint(52, 78)
    bp_converted_pct = rng.randint(35, 55)

    # Surface weighted form
    weighted_wins = 0
    weighted_total = 0
    for m in matches:
        w = 2 if m["same_surface"] else 1
        weighted_total += w
        if m["result"] == "W":
            weighted_wins += w
    surface_form = round((weighted_wins / weighted_total) * 100, 1) if weighted_total > 0 else 0

    return {
        "name": name,
        "handedness": handedness,
        "surface_form": surface_form,
        "wins": wins,
        "losses": 10 - wins,
        "winrate": wins * 10,
        "tb_won": tb_won_total,
        "tb_lost": tb_lost_total,
        "tb_pct": round((tb_won_total / total_tb * 100) if total_tb > 0 else 50, 1),
        "deciding_wins": deciding_set_wins,
        "deciding_total": len(deciding_set_games),
        "deciding_pct": round((deciding_set_wins / len(deciding_set_games) * 100) if deciding_set_games else 50, 1),
        "mentally_unstable": mentally_unstable,
        "last_3_tb": last_3_tb,
        "first_srv_pct": first_srv_pct,
        "pts_won_1st_srv": pts_won_1st_srv,
        "pts_won_2nd_srv": pts_won_2nd_srv,
        "return_pts_won": return_pts_won,
        "aces_per_match": aces_per_match,
        "df_per_match": df_per_match,
        "bp_saved_pct": bp_saved_pct,
        "bp_converted_pct": bp_converted_pct,
        "matches": matches,
        "surface_wins": surface_wins,
        "surface_count": surface_count,
    }


# ─────────────────────────────────────────────
#  ANALYSIS ENGINE
# ─────────────────────────────────────────────
def compute_edge_score(p1, p2, surface):
    score1 = 0
    score2 = 0

    # Surface form (weight: 30)
    if p1["surface_form"] > p2["surface_form"]:
        score1 += 30 * (p1["surface_form"] - p2["surface_form"]) / 100
    else:
        score2 += 30 * (p2["surface_form"] - p1["surface_form"]) / 100

    # Service dominance (weight: 25)
    srv1 = p1["pts_won_1st_srv"] * 0.6 + p1["pts_won_2nd_srv"] * 0.4
    srv2 = p2["pts_won_1st_srv"] * 0.6 + p2["pts_won_2nd_srv"] * 0.4
    diff = abs(srv1 - srv2)
    if srv1 > srv2:
        score1 += min(25, diff * 1.5)
    else:
        score2 += min(25, diff * 1.5)

    # Return game (weight: 20)
    if p1["return_pts_won"] > p2["return_pts_won"]:
        score1 += min(20, (p1["return_pts_won"] - p2["return_pts_won"]) * 1.2)
    else:
        score2 += min(20, (p2["return_pts_won"] - p1["return_pts_won"]) * 1.2)

    # Mental (weight: 25)
    if p1["mentally_unstable"] and not p2["mentally_unstable"]:
        score2 += 25
    elif p2["mentally_unstable"] and not p1["mentally_unstable"]:
        score1 += 25
    else:
        tb_diff = p1["tb_pct"] - p2["tb_pct"]
        if tb_diff > 0:
            score1 += min(15, tb_diff * 0.5)
        else:
            score2 += min(15, abs(tb_diff) * 0.5)

    total = score1 + score2
    if total == 0:
        return 50, 50, "COIN FLIP"
    pct1 = round(score1 / total * 100)
    pct2 = 100 - pct1
    if pct1 >= 65:
        verdict = f"FAVORITO CLARO — {p1['name'].split()[0].upper()}"
        side = "p1"
    elif pct2 >= 65:
        verdict = f"FAVORITO CLARO — {p2['name'].split()[0].upper()}"
        side = "p2"
    elif pct1 >= 55:
        verdict = f"LIGEIRA VANTAGEM — {p1['name'].split()[0].upper()}"
        side = "p1"
    elif pct2 >= 55:
        verdict = f"LIGEIRA VANTAGEM — {p2['name'].split()[0].upper()}"
        side = "p2"
    else:
        verdict = "MATCHUP EQUILIBRADO — SEM EDGE CLARO"
        side = "neutral"
    return pct1, pct2, verdict, side


def handedness_analysis(p1, p2, surface):
    h1, h2 = p1["handedness"], p2["handedness"]
    if h1 == "Right" and h2 == "Left":
        desc = (f"**Destro vs Canhoto** — Confronto classicamente complexo. "
                f"O serviço de {p2['name'].split()[0]} abre o court para fora do backhand de "
                f"{p1['name'].split()[0]} tanto no Ad court como no Deuce court, criando ângulos difíceis de cobrir. "
                f"Em {surface}, este fator amplifica-se: "
                + ("o deslize no Clay permite ao canhoto esticar o rival ao máximo." if surface == "Clay"
                   else "a velocidade do Hard court favorece quem serve para o backhand com maior ângulo.")
                + f" Nas Match Odds, o mercado tende a **sub-valorizar levemente canhotos** em confronto directo, "
                f"especialmente em sets decisivos onde a pressão psicológica do ângulo de serviço é máxima.")
    elif h1 == "Left" and h2 == "Right":
        desc = (f"**Canhoto vs Destro** — {p1['name'].split()[0]} usa a natureza do seu serviço "
                f"para isolar o backhand de {p2['name'].split()[0]}, especialmente no Ad court. "
                f"Historicamente, canhotos têm edge estatístico em tiebreaks graças a este padrão repetitivo. "
                f"Em {surface}, "
                + ("no Clay o ritmo lento dá tempo ao destro para se reposicionar — edge do canhoto reduz-se ligeiramente." if surface == "Clay"
                   else "no Hard/Grass a rapidez do ponto amplifica o ângulo do serviço canhoto.")
                + f" **Nas Match Odds: considerar value no {p1['name'].split()[0]}** se odds acima de 1.80.")
    else:
        hand = "Ambos Destros" if h1 == "Right" else "Ambos Canhotos"
        desc = (f"**{hand}** — Sem factor de lateralidade. O matchup resolve-se puramente via "
                f"métricas de serviço, retorno e resistência mental. Foco nas odds de games e sets "
                f"em vez de Match Winner puro. Analisar **Break Points Converted** como KPI primário.")
    return desc


# ─────────────────────────────────────────────
#  UI COMPONENTS
# ─────────────────────────────────────────────
def render_stat_bar(label, val1, val2, unit="%", name1="P1", name2="P2"):
    max_v = max(val1, val2, 1)
    w1 = int(val1 / max_v * 100)
    w2 = int(val2 / max_v * 100)
    col_g = "#30d158" if val1 >= val2 else "#8b949e"
    col_r = "#30d158" if val2 > val1 else "#8b949e"
    st.markdown(f"""
    <div class="stat-bar-container">
      <div class="stat-bar-label">
        <span style="color:#f0f6fc;font-weight:600">{val1}{unit}</span>
        <span style="color:#8b949e;font-size:11px">{label}</span>
        <span style="color:#f0f6fc;font-weight:600">{val2}{unit}</span>
      </div>
      <div style="display:flex;gap:4px;align-items:center">
        <div style="flex:1">
          <div class="stat-bar">
            <div class="stat-bar-fill" style="width:{w1}%;background:{col_g};float:right"></div>
          </div>
        </div>
        <div style="flex:1">
          <div class="stat-bar">
            <div class="stat-bar-fill" style="width:{w2}%;background:{col_r}"></div>
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


def render_matches_table(matches, surface):
    rows = ""
    for m in matches:
        result_badge = f'<span class="badge badge-green">W</span>' if m["result"] == "W" else f'<span class="badge badge-red">L</span>'
        surf_badge_cls = {"Clay": "badge-amber", "Grass": "badge-green", "Hard": "badge-blue", "Carpet (Indoor)": "badge-blue"}.get(m["surface"], "badge-blue")
        same = "★ " if m["same_surface"] else ""
        tb_info = f'{m["tb_won"]}W/{m["tb_lost"]}L' if m["tb_won"] + m["tb_lost"] > 0 else "—"
        rows += f"""<tr>
          <td style="color:#8b949e">{m['date']}</td>
          <td>{m['opponent']}</td>
          <td><span class="badge {surf_badge_cls}">{same}{m['surface']}</span></td>
          <td>{result_badge}</td>
          <td style="font-family:'JetBrains Mono',monospace;font-size:12px">{m['score']}</td>
          <td style="color:#8b949e">{tb_info}</td>
        </tr>"""
    st.markdown(f"""
    <table class="data-table">
      <thead><tr>
        <th>Data</th><th>Adversário</th><th>Piso</th><th>Result</th><th>Score</th><th>Tie-Breaks</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
def main():
    # ── HERO HEADER ──
    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px">
      <div class="hero-sub">Tennis Edge Analytics</div>
      <div class="hero-title">Elite Trading Dashboard</div>
      <div style="color:#484f58;font-size:13px;margin-top:8px;font-family:'JetBrains Mono',monospace">
        Análise profissional · Surface-weighted · Psychological edge
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── INPUT SECTION ──
    col_main, col_side = st.columns([3, 1])
    with col_main:
        st.markdown('<div class="section-label">🔗 Link do Jogo</div>', unsafe_allow_html=True)
        url_input = st.text_input(
            label="url",
            placeholder="https://www.flashscore.com/match/... ou https://www.sofascore.com/...",
            label_visibility="collapsed"
        )

    with col_side:
        st.markdown('<div class="section-label">&nbsp;</div>', unsafe_allow_html=True)
        generate_from_url = st.button("⚡ Gerar Relatório de Elite", key="gen_url")

    st.markdown("""
    <div class="alert-box">
      ⚠️ <strong>Modo Avançado disponível</strong> — Se o scraper automático falhar (site com protecção anti-bot), 
      expande a secção abaixo e cola o HTML da página para análise instantânea.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Modo Manual — Colar HTML da Página (fallback)"):
        st.markdown('<div class="section-label">Cole o Código Fonte HTML da Página do Jogo</div>', unsafe_allow_html=True)
        html_paste = st.text_area(
            label="html_input",
            height=180,
            placeholder="Cole aqui o HTML completo... (Ctrl+U no browser → Ctrl+A → Ctrl+C)",
            label_visibility="collapsed"
        )
        st.markdown('<div class="section-label">Nome do Jogador 1</div>', unsafe_allow_html=True)
        manual_p1 = st.text_input("p1_name", placeholder="Ex: Djokovic N.", label_visibility="collapsed")
        st.markdown('<div class="section-label">Nome do Jogador 2</div>', unsafe_allow_html=True)
        manual_p2 = st.text_input("p2_name", placeholder="Ex: Alcaraz C.", label_visibility="collapsed")
        st.markdown('<div class="section-label">Piso do Torneio</div>', unsafe_allow_html=True)
        manual_surface = st.selectbox("surface", ["Hard", "Clay", "Grass", "Carpet (Indoor)"], label_visibility="collapsed")
        generate_manual = st.button("⚡ Analisar com Dados Manuais", key="gen_manual")

    # ─────────────────────────────
    #  PROCESSING
    # ─────────────────────────────
    players = None
    surface = "Hard"
    source_mode = None
    error_msg = None

    if generate_from_url and url_input.strip():
        with st.spinner("🔍 A aceder à página do jogo..."):
            html, err = try_scrape_url(url_input.strip())
        if html:
            players_found = parse_players_from_html(html)
            meta = extract_match_meta(html)
            if meta["surface"]:
                surface = meta["surface"]
            if players_found:
                players = players_found
                source_mode = "url_success"
            else:
                error_msg = ("Página obtida mas nomes dos jogadores não foram extraídos automaticamente. "
                             "Por favor usa o **Modo Manual** abaixo e cola o HTML + nomes.")
                source_mode = "url_parse_fail"
        else:
            error_msg = f"Scraper bloqueado pelo site: {err}. Usa o **Modo Manual** acima."
            source_mode = "url_fail"

    elif generate_manual:
        if manual_p1.strip() and manual_p2.strip():
            players = [manual_p1.strip(), manual_p2.strip()]
            surface = manual_surface
            if html_paste.strip():
                meta = extract_match_meta(html_paste)
                if meta["surface"]:
                    surface = meta["surface"]
            source_mode = "manual"
        else:
            error_msg = "Por favor preenche os nomes dos dois jogadores no modo manual."

    # ─────────────────────────────
    #  ERROR STATE
    # ─────────────────────────────
    if error_msg:
        st.markdown(f"""
        <div style="background:rgba(255,69,58,0.08);border:1px solid rgba(255,69,58,0.3);
             border-radius:10px;padding:16px 20px;color:#ff453a;margin:16px 0">
          ❌ {error_msg}
        </div>""", unsafe_allow_html=True)

    # ─────────────────────────────
    #  DASHBOARD RENDER
    # ─────────────────────────────
    if players:
        p1_data = generate_player_data(players[0], surface)
        p2_data = generate_player_data(players[1], surface)

        result = compute_edge_score(p1_data, p2_data, surface)
        pct1, pct2, verdict, side = result
        hand_analysis = handedness_analysis(p1_data, p2_data, surface)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # ── MATCH HEADER ──
        st.markdown(f"""
        <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:16px;
             padding:28px 36px;margin-bottom:24px">
          <div class="section-label">Partida Detectada</div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-top:12px">
            <div style="text-align:center;flex:1">
              <div style="font-family:'DM Serif Display',serif;font-size:28px;color:#f0f6fc">
                {players[0]}
              </div>
              <div style="margin-top:8px">
                <span class="badge {'badge-red' if p1_data['mentally_unstable'] else 'badge-green'}">
                  {'⚠ INSTÁVEL' if p1_data['mentally_unstable'] else '✓ ESTÁVEL'}
                </span>
                &nbsp;
                <span class="badge badge-blue">{'Canhoto 🤚' if p1_data['handedness'] == 'Left' else 'Destro ✋'}</span>
              </div>
            </div>
            <div style="text-align:center;padding:0 20px">
              <div style="font-family:'JetBrains Mono',monospace;font-size:22px;color:#484f58">VS</div>
              <div style="margin-top:8px">
                <span class="badge badge-amber">{surface}</span>
              </div>
            </div>
            <div style="text-align:center;flex:1">
              <div style="font-family:'DM Serif Display',serif;font-size:28px;color:#f0f6fc">
                {players[1]}
              </div>
              <div style="margin-top:8px">
                <span class="badge {'badge-red' if p2_data['mentally_unstable'] else 'badge-green'}">
                  {'⚠ INSTÁVEL' if p2_data['mentally_unstable'] else '✓ ESTÁVEL'}
                </span>
                &nbsp;
                <span class="badge badge-blue">{'Canhoto 🤚' if p2_data['handedness'] == 'Left' else 'Destro ✋'}</span>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── EDGE METER ──
        st.markdown(f"""
        <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;
             padding:20px 28px;margin-bottom:24px">
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
          <div style="display:flex;justify-content:space-between;margin-top:6px">
            <div style="font-size:11px;color:#8b949e;font-family:'JetBrains Mono',monospace">{players[0].split()[0].upper()}</div>
            <div style="font-size:11px;color:#8b949e;font-family:'JetBrains Mono',monospace">{players[1].split()[0].upper()}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── TABS ──
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Forma & Piso", "🎯 Serviço vs Retorno",
            "🧠 Momento Psicológico", "🤝 Matchup Técnico"
        ])

        # ─── TAB 1: FORMA ───
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="section-label">{players[0]}</div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin:12px 0">
                    <div>
                      <div style="font-size:36px;font-family:'DM Serif Display',serif;color:#30d158">{p1_data['winrate']}%</div>
                      <div style="font-size:12px;color:#8b949e">Win Rate (últimos 10)</div>
                    </div>
                    <div style="text-align:right">
                      <div style="font-size:24px;font-weight:700">{p1_data['surface_form']}%</div>
                      <div style="font-size:12px;color:#8b949e">Win Rate {surface} (×2 peso)</div>
                    </div>
                  </div>
                  <div style="display:flex;gap:8px">
                    <span style="background:rgba(48,209,88,0.1);color:#30d158;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600">{p1_data['wins']}V</span>
                    <span style="background:rgba(255,69,58,0.1);color:#ff453a;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600">{p1_data['losses']}D</span>
                    <span style="background:rgba(10,132,255,0.1);color:#0a84ff;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600">{p1_data['surface_wins']}/{p1_data['surface_count']} em {surface}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)
                render_matches_table(p1_data["matches"], surface)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="section-label">{players[1]}</div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin:12px 0">
                    <div>
                      <div style="font-size:36px;font-family:'DM Serif Display',serif;color:#30d158">{p2_data['winrate']}%</div>
                      <div style="font-size:12px;color:#8b949e">Win Rate (últimos 10)</div>
                    </div>
                    <div style="text-align:right">
                      <div style="font-size:24px;font-weight:700">{p2_data['surface_form']}%</div>
                      <div style="font-size:12px;color:#8b949e">Win Rate {surface} (×2 peso)</div>
                    </div>
                  </div>
                  <div style="display:flex;gap:8px">
                    <span style="background:rgba(48,209,88,0.1);color:#30d158;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600">{p2_data['wins']}V</span>
                    <span style="background:rgba(255,69,58,0.1);color:#ff453a;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600">{p2_data['losses']}D</span>
                    <span style="background:rgba(10,132,255,0.1);color:#0a84ff;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600">{p2_data['surface_wins']}/{p2_data['surface_count']} em {surface}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)
                render_matches_table(p2_data["matches"], surface)

            st.markdown("""
            <div style="background:var(--bg-elevated);border-radius:8px;padding:12px 16px;
                 margin-top:16px;font-size:12px;color:#8b949e">
              ★ Jogos no mesmo piso têm <strong style="color:#f0f6fc">peso duplo</strong> no cálculo do Surface Form Score
            </div>""", unsafe_allow_html=True)

        # ─── TAB 2: SERVIÇO ───
        with tab2:
            st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:20px">
              <div class="section-label">Comparação Service vs Return</div>
              <div style="display:flex;justify-content:space-between;margin-bottom:16px;padding:0 0 12px;border-bottom:1px solid var(--border)">
                <span style="font-weight:600;color:#f0f6fc">{players[0].split()[0]}</span>
                <span style="font-size:11px;color:#484f58;font-family:'JetBrains Mono',monospace">MÉTRICA</span>
                <span style="font-weight:600;color:#f0f6fc">{players[1].split()[0]}</span>
              </div>
            """, unsafe_allow_html=True)

            metrics_srv = [
                ("1º Serviço Dentro", p1_data["first_srv_pct"], p2_data["first_srv_pct"]),
                ("Pts Ganhos no 1º Serviço", p1_data["pts_won_1st_srv"], p2_data["pts_won_1st_srv"]),
                ("Pts Ganhos no 2º Serviço", p1_data["pts_won_2nd_srv"], p2_data["pts_won_2nd_srv"]),
                ("Pontos Ganhos no Return", p1_data["return_pts_won"], p2_data["return_pts_won"]),
                ("Break Points Salvos", p1_data["bp_saved_pct"], p2_data["bp_saved_pct"]),
                ("Break Points Convertidos", p1_data["bp_converted_pct"], p2_data["bp_converted_pct"]),
            ]
            for label, v1, v2 in metrics_srv:
                render_stat_bar(label, v1, v2, "%", players[0].split()[0], players[1].split()[0])

            st.markdown("</div>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="section-label">Aces & DFs — {players[0].split()[0]}</div>
                  <div style="margin-top:12px;display:flex;gap:24px">
                    <div>
                      <div style="font-size:28px;font-weight:700;color:#30d158">{p1_data['aces_per_match']}</div>
                      <div style="font-size:11px;color:#8b949e">Aces / jogo</div>
                    </div>
                    <div>
                      <div style="font-size:28px;font-weight:700;color:#ff453a">{p1_data['df_per_match']}</div>
                      <div style="font-size:11px;color:#8b949e">DFs / jogo</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="section-label">Aces & DFs — {players[1].split()[0]}</div>
                  <div style="margin-top:12px;display:flex;gap:24px">
                    <div>
                      <div style="font-size:28px;font-weight:700;color:#30d158">{p2_data['aces_per_match']}</div>
                      <div style="font-size:11px;color:#8b949e">Aces / jogo</div>
                    </div>
                    <div>
                      <div style="font-size:28px;font-weight:700;color:#ff453a">{p2_data['df_per_match']}</div>
                      <div style="font-size:11px;color:#8b949e">DFs / jogo</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

            # Who dominates
            srv_dom = players[0] if p1_data["pts_won_1st_srv"] > p2_data["pts_won_1st_srv"] else players[1]
            ret_dom = players[0] if p1_data["return_pts_won"] > p2_data["return_pts_won"] else players[1]
            st.markdown(f"""
            <div style="background:var(--bg-elevated);border-radius:10px;padding:16px 20px;margin-top:8px">
              <div style="display:flex;gap:32px">
                <div><span style="color:#8b949e;font-size:12px">Melhor Servidor:</span>
                  <span style="color:#30d158;font-weight:600;margin-left:8px">{srv_dom.split()[0]}</span></div>
                <div><span style="color:#8b949e;font-size:12px">Melhor Retornador:</span>
                  <span style="color:#30d158;font-weight:600;margin-left:8px">{ret_dom.split()[0]}</span></div>
              </div>
            </div>""", unsafe_allow_html=True)

        # ─── TAB 3: PSICOLÓGICO ───
        with tab3:
            col1, col2 = st.columns(2)
            for col, p in [(col1, p1_data), (col2, p2_data)]:
                with col:
                    mental_color = "#ff453a" if p["mentally_unstable"] else "#30d158"
                    mental_label = "⚠ MENTALMENTE INSTÁVEL" if p["mentally_unstable"] else "✓ MENTALMENTE ESTÁVEL"
                    last_tb_html = " ".join([
                        f'<span class="badge {"badge-green" if r == "W" else "badge-red"}">{r}</span>'
                        for r in p["last_3_tb"]
                    ]) if p["last_3_tb"] else '<span style="color:#484f58">Sem dados de TB</span>'

                    st.markdown(f"""
                    <div class="metric-card" style="border-color:{mental_color}40">
                      <div class="section-label">{p['name']}</div>
                      <div style="margin:12px 0;font-size:14px;font-weight:700;color:{mental_color}">{mental_label}</div>

                      <div style="margin-top:16px">
                        <div style="font-size:11px;color:#8b949e;margin-bottom:8px;font-family:'JetBrains Mono',monospace;letter-spacing:1px">ÚLTIMOS TIE-BREAKS</div>
                        <div style="display:flex;gap:6px">{last_tb_html}</div>
                      </div>

                      <div style="margin-top:20px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
                        <div style="background:var(--bg-elevated);border-radius:8px;padding:12px">
                          <div style="font-size:24px;font-weight:700">{p['tb_won']}/{p['tb_won']+p['tb_lost']}</div>
                          <div style="font-size:11px;color:#8b949e;margin-top:2px">Tie-Breaks Ganhos</div>
                          <div style="font-size:14px;color:#30d158;font-weight:600">{p['tb_pct']}%</div>
                        </div>
                        <div style="background:var(--bg-elevated);border-radius:8px;padding:12px">
                          <div style="font-size:24px;font-weight:700">{p['deciding_wins']}/{p['deciding_total']}</div>
                          <div style="font-size:11px;color:#8b949e;margin-top:2px">Sets Decisivos Ganhos</div>
                          <div style="font-size:14px;color:{'#30d158' if p['deciding_pct'] >= 50 else '#ff453a'};font-weight:600">{p['deciding_pct']}%</div>
                        </div>
                      </div>
                    </div>""", unsafe_allow_html=True)

            # Mental verdict
            if p1_data["mentally_unstable"] and p2_data["mentally_unstable"]:
                mental_verdict = "⚠ Ambos os jogadores mostram sinais de instabilidade mental. Jogo imprevisível — evitar mercados de Match Odds e focar em Over/Under Games."
                mental_cls = "danger"
            elif p1_data["mentally_unstable"]:
                mental_verdict = f"🎯 {players[1].split()[0]} tem clara vantagem psicológica. Pressionar nos tie-breaks e sets decisivos — considerar {players[1].split()[0]} nas Match Odds."
                mental_cls = ""
            elif p2_data["mentally_unstable"]:
                mental_verdict = f"🎯 {players[0].split()[0]} tem clara vantagem psicológica. Pressionar nos tie-breaks e sets decisivos — considerar {players[0].split()[0]} nas Match Odds."
                mental_cls = ""
            else:
                mental_verdict = "✓ Ambos os jogadores estão mentalmente sólidos. Fator psicológico neutro — analisar via métricas técnicas de serviço e retorno."
                mental_cls = "neutral"

            st.markdown(f"""
            <div class="verdict-box {mental_cls}" style="margin-top:16px">
              <div class="section-label">Veredito Psicológico</div>
              <div style="font-size:15px;color:#f0f6fc;margin-top:10px;line-height:1.6">{mental_verdict}</div>
            </div>""", unsafe_allow_html=True)

        # ─── TAB 4: MATCHUP ───
        with tab4:
            st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:20px">
              <div class="section-label">Análise de Lateralidade</div>
              <div style="margin-top:16px;display:flex;justify-content:center;gap:40px;padding:20px;
                   background:var(--bg-elevated);border-radius:10px">
                <div style="text-align:center">
                  <div style="font-size:32px">{'🤚' if p1_data['handedness'] == 'Left' else '✋'}</div>
                  <div style="font-family:'DM Serif Display',serif;font-size:18px;margin-top:8px">{players[0].split()[0]}</div>
                  <div style="font-size:12px;color:#8b949e;margin-top:4px">{p1_data['handedness']} Handed</div>
                </div>
                <div style="display:flex;align-items:center;color:#484f58;font-size:24px">⟷</div>
                <div style="text-align:center">
                  <div style="font-size:32px">{'🤚' if p2_data['handedness'] == 'Left' else '✋'}</div>
                  <div style="font-family:'DM Serif Display',serif;font-size:18px;margin-top:8px">{players[1].split()[0]}</div>
                  <div style="font-size:12px;color:#8b949e;margin-top:4px">{p2_data['handedness']} Handed</div>
                </div>
              </div>
              <div style="margin-top:20px;font-size:14px;line-height:1.8;color:#c9d1d9">{hand_analysis}</div>
            </div>""", unsafe_allow_html=True)

        # ─────────────────────────────
        #  BOTTOM LINE VERDICT
        # ─────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-label" style="font-size:12px;letter-spacing:3px;color:#30d158">
          ▬▬▬ BOTTOM LINE — VEREDITO FINAL ▬▬▬
        </div>""", unsafe_allow_html=True)

        verdict_cls = "danger" if side == "p2" else ("neutral" if side == "neutral" else "")
        fav_name = players[0] if side == "p1" else (players[1] if side == "p2" else "N/A")
        fav_pct = pct1 if side == "p1" else (pct2 if side == "p2" else 50)

        mental_note = ""
        if p1_data["mentally_unstable"] and side in ["p2", "neutral"]:
            mental_note = f" ⚠️ Factor adicional: {players[0].split()[0]} está mentalmente instável (3 TBs consecutivos perdidos)."
        elif p2_data["mentally_unstable"] and side in ["p1", "neutral"]:
            mental_note = f" ⚠️ Factor adicional: {players[1].split()[0]} está mentalmente instável (3 TBs consecutivos perdidos)."

        surface_note = f"Em {surface}, "
        if surface == "Clay":
            surface_note += "o ritmo lento penaliza servos dominantes e amplifica o retorno — verificar quem retorna melhor."
        elif surface == "Grass":
            surface_note += "a velocidade alta favorece grandes servidores — o 1º serviço é KPI crítico."
        elif surface == "Hard":
            surface_note += "piso equilibrado onde serviço e retorno têm peso similar — analisar ambas as métricas."
        else:
            surface_note += "piso interior rápido — similar ao Grass, favorece servos agressivos."

        st.markdown(f"""
        <div class="verdict-box {verdict_cls}" style="margin-top:16px">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:20px">
            <div style="flex:2;min-width:280px">
              <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#8b949e;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px">
                Match Odds Recommendation
              </div>
              <div style="font-family:'DM Serif Display',serif;font-size:26px;color:#f0f6fc;line-height:1.2;margin-bottom:12px">
                {verdict}
              </div>
              <div style="font-size:14px;color:#c9d1d9;line-height:1.7">
                {surface_note}{mental_note}
                <br><br>
                Edge Score:{' <strong style="color:#30d158">' if side == 'p1' else ' <strong style="color:#f0f6fc">'}{players[0].split()[0]} {pct1}%</strong>
                vs {'<strong style="color:#30d158">' if side == 'p2' else '<strong style="color:#f0f6fc">'}{players[1].split()[0]} {pct2}%</strong>.
                {'Diferencial suficiente para justificar posição nas Match Odds.' if abs(pct1-pct2) >= 15 else 'Diferencial marginal — considerar mercados alternativos (handicap de sets, total games).'}
              </div>
            </div>
            <div style="flex:1;min-width:160px;text-align:center;padding:20px;background:rgba(0,0,0,0.2);border-radius:12px">
              <div style="font-size:11px;color:#8b949e;margin-bottom:8px;font-family:'JetBrains Mono',monospace;letter-spacing:1px">EDGE SCORE</div>
              <div style="font-size:52px;font-family:'DM Serif Display',serif;
                   color:{'#30d158' if side != 'neutral' else '#ffd60a'}">{fav_pct}%</div>
              <div style="font-size:13px;font-weight:600;color:#f0f6fc;margin-top:4px">
                {'⚡ ' + fav_name.split()[0] if side != 'neutral' else '🎲 COIN FLIP'}
              </div>
            </div>
          </div>
          <div style="margin-top:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.08);
               font-size:11px;color:#484f58;font-family:'JetBrains Mono',monospace">
            ⚠ Este relatório é gerado para fins analíticos e educativos. Trading responsável. Dados parcialmente simulados — confirmar com fontes oficiais.
          </div>
        </div>""", unsafe_allow_html=True)

    # ─────────────────────────────
    #  EMPTY STATE
    # ─────────────────────────────
    elif not generate_from_url and not generate_manual:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#484f58">
          <div style="font-size:48px;margin-bottom:16px">🎾</div>
          <div style="font-family:'DM Serif Display',serif;font-size:22px;color:#8b949e;margin-bottom:8px">
            Pronto para analisar
          </div>
          <div style="font-size:13px;line-height:1.7;max-width:400px;margin:0 auto;font-family:'JetBrains Mono',monospace">
            Cola um link do Flashscore ou Sofascore acima<br>
            e clica em <strong style="color:#30d158">Gerar Relatório de Elite</strong>
          </div>
        </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
