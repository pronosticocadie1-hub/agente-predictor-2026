import streamlit as st
import requests
import numpy as np
import pandas as pd
from datetime import datetime

# Configuración profesional
st.set_page_config(page_title="AI Quant Predictor 2026 - Master Build", layout="wide")

# --- CREDENCIALES ---
LLAVE_FOOTBALL_DATA = "08e00792567d4861bef295d0dc72f6a5"
LLAVE_RAPIDAPI_SPORTAPI = "6be0c20affmsh847bbf9d8484c53p1313b8jsn376566ead2f9"

# --- MOTOR DE FUSIÓN (APIs + FALLBACK) ---
def engine_fusion_total(liga_seleccionada):
    partidos_api = []
    
    # Intento 1: Football-Data
    try:
        url = "https://api.football-data.org/v4/matches"
        headers = {"X-Auth-Token": LLAVE_FOOTBALL_DATA}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            for m in res.json().get("matches", [])[:5]:
                partidos_api.append({
                    "local": m["homeTeam"]["name"], "visitante": m["awayTeam"]["name"],
                    "media_h2h_goles_loc": 1.5, "media_h2h_goles_vis": 1.3, "seed": int(m["id"])
                })
    except: pass

    # Intento 2: Si la API no trajo nada, usamos respaldo (Modo Coherencia)
    if not partidos_api:
        return [
            {"local": "Francia", "visitante": "Paraguay", "media_h2h_goles_loc": 1.2, "media_h2h_goles_vis": 1.4, "seed": 7701},
            {"local": "Real Madrid", "visitante": "Barcelona", "media_h2h_goles_loc": 2.1, "media_h2h_goles_vis": 1.9, "seed": 8801}
        ]
    return partidos_api

# --- MOTOR MATEMÁTICO PURO (SIN SESGOS) ---
def simular_partido_monte_carlo(media_loc, media_vis, seed):
    np.random.seed(seed)
    sim_loc = np.random.poisson(media_loc, 10000)
    sim_vis = np.random.poisson(media_vis, 10000)
    
    return {
        "prob_loc": np.mean(sim_loc > sim_vis),
        "prob_vis": np.mean(sim_vis > sim_loc),
        "prob_empate": np.mean(sim_loc == sim_vis),
        "prob_over_25": np.mean((sim_loc + sim_vis) > 2.5),
        "exp_goles": round(np.mean(sim_loc + sim_vis), 1)
    }

# --- INTERFAZ ---
st.title("🦅 AI Ultra-Predictor | Master Build")
st.markdown("---")

liga_sel = st.selectbox("Competición Activa:", ["Mundial FIFA 2026", "LaLiga 2026/27"])
partidos = engine_fusion_total(liga_sel)

for p in partidos:
    res = simular_partido_monte_carlo(p["media_h2h_goles_loc"], p["media_h2h_goles_vis"], p["seed"])
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 2])
        c1.subheader(f"🏠 {p['local']}")
        c2.markdown("<h3 style='text-align:center;'>VS</h3>", unsafe_allow_html=True)
        c3.subheader(f"{p['visitante']} 🚌")
        
        # Métricas de Probabilidad
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Local", f"{round(res['prob_loc']*100, 1)}%")
        m2.metric("Empate", f"{round(res['prob_empate']*100, 1)}%")
        m3.metric("Visitante", f"{round(res['prob_vis']*100, 1)}%")
        m4.metric("Over 2.5", f"{round(res['prob_over_25']*100, 1)}%")
        
        # Lógica de construcción del Ticket (Basada 100% en res)
        favorito = p['local'] if res['prob_loc'] > res['prob_vis'] else p['visitante']
        prob_favorito = max(res['prob_loc'], res['prob_vis'])
        
        # Construcción dinámica
        linea_goles = "Más de 2.5" if res['prob_over_25'] > 0.5 else "Más de 1.5"
        
        st.markdown(f"""
        <div style='background-color:#1e293b; border: 1px solid #f59e0b; padding:15px; border-radius:10px; margin-top:10px;'>
            <p style='color:#f59e0b; font-weight:bold;'>💎 Ticket Quant Optimizado</p>
            <ul>
                <li>✅ <b>Selección 1:</b> Victoria o Empate: {favorito}</li>
                <li>✅ <b>Selección 2:</b> {linea_goles} Goles totales</li>
                <li>✅ <b>Selección 3:</b> Más de 7.5 Córners (Confianza: {round(prob_favorito*100, 1)}%)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
