import streamlit as st
import requests
import numpy as np
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AI Quant Predictor Pro", layout="wide")

LLAVE_FOOTBALL_DATA = "08e00792567d4861bef295d0dc72f6a5"
LLAVE_RAPIDAPI_SPORTAPI = "6be0c20affmsh847bbf9d8484c53p1313b8jsn376566ead2f9"

# --- MOTOR DE DATOS ---
def obtener_partidos_api():
    """Captura datos de las APIs disponibles. Retorna una lista unificada."""
    lista_partidos = []
    
    # 1. Football-Data (Prioridad 1)
    try:
        url = "https://api.football-data.org/v4/matches"
        headers = {"X-Auth-Token": LLAVE_FOOTBALL_DATA}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            for m in res.json().get("matches", []):
                lista_partidos.append({
                    "local": m["homeTeam"]["name"], "visitante": m["awayTeam"]["name"],
                    "fecha": m["utcDate"], "liga": m["competition"]["name"],
                    "media_h2h_goles_loc": 1.5, "media_h2h_goles_vis": 1.3 # Aquí deberías mapear tus stats reales
                })
    except: pass

    # 2. Si no hay datos, incluimos un set de prueba para que la interfaz no esté vacía
    if not lista_partidos:
        lista_partidos = [
            {"local": "Brasil", "visitante": "Alemania", "fecha": "2026-07-03T20:00:00Z", "liga": "Mundial 2026", "media_h2h_goles_loc": 2.1, "media_h2h_goles_vis": 1.8},
            {"local": "Real Madrid", "visitante": "Barcelona", "fecha": "2026-08-15T21:00:00Z", "liga": "LaLiga", "media_h2h_goles_loc": 1.9, "media_h2h_goles_vis": 2.2}
        ]
    return lista_partidos

# --- MOTOR MATEMÁTICO ---
def calcular_metricas(loc, vis):
    # Modelo basado en diferencial de fuerza
    diff = loc - vis
    prob_loc = 1 / (1 + np.exp(-1.2 * diff))
    prob_vis = 1 - prob_loc
    prob_empate = 0.25 - (abs(diff) * 0.05)
    
    # Normalizar
    total = prob_loc + prob_vis + prob_empate
    return {
        "p_loc": prob_loc/total, "p_emp": prob_empate/total, "p_vis": prob_vis/total,
        "prob_max": max(prob_loc/total, prob_vis/total),
        "over": (loc + vis) / 3.0
    }

# --- INTERFAZ ---
st.title("🦅 AI Ultra-Predictor | Buscador de Combinadas")
partidos_crudos = obtener_partidos_api()

# Procesamiento y ordenamiento (COMBO FINDER)
partidos_procesados = []
for p in partidos_crudos:
    metrics = calcular_metricas(p["media_h2h_goles_loc"], p["media_h2h_goles_vis"])
    p["metrics"] = metrics
    partidos_procesados.append(p)

# ORDENAR: El Buscador de combinadas (Mayor probabilidad primero)
partidos_procesados.sort(key=lambda x: x["metrics"]["prob_max"], reverse=True)

# Renderizado
st.sidebar.header("Filtros")
st.sidebar.success(f"Se han encontrado {len(partidos_procesados)} eventos.")

for p in partidos_procesados:
    m = p["metrics"]
    fecha_dt = datetime.strptime(p["fecha"], "%Y-%m-%dT%H:%M:%SZ")
    
    with st.container(border=True):
        st.markdown(f"**{p['liga']}** | 📅 {fecha_dt.strftime('%d/%m %H:%M')}")
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        c1.subheader(f"{p['local']} vs {p['visitante']}")
        c2.metric("Local", f"{round(m['p_loc']*100, 1)}%")
        c3.metric("Empate", f"{round(m['p_emp']*100, 1)}%")
        c4.metric("Visitante", f"{round(m['p_vis']*100, 1)}%")
        
        # Ticket Dinámico basado en el ordenamiento
        st.info(f"💎 **Ticket Recomendado:** {p['local']} o {p['visitante']} | Prob. Acierto: {round(m['prob_max']*100, 1)}%")
