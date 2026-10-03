import streamlit as st
import json
import os
import copy
import time
import re
from datetime import datetime

try:
    import garminconnect
    from garminconnect import Garmin, GarminConnectAuthenticationError, GarminConnectMFAError
except ImportError:
    Garmin = None
    GarminConnectAuthenticationError = Exception
    GarminConnectMFAError = Exception

# Configuración móvil
st.set_page_config(
    page_title="Biostrength",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estilos CSS específicos reforzados para iPhone sin gafas
st.markdown("""
<style>
    .stApp, body, html, [data-testid="stAppViewContainer"] {
        background-color: #0b0f17 !important;
        color: #ffffff !important;
    }

    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 6px !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div {
        min-width: 0 !important;
        flex-shrink: 1 !important;
    }

    h1 {
        font-size: 38px !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        margin-bottom: 8px !important;
    }

    h2, h3 {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin-top: 10px !important;
    }

    label p, .stTextInput label p, .stNumberInput label p, .stSelectbox label p {
        font-size: 21px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin-bottom: 6px !important;
    }

    div[data-testid="stTextInput"] input {
        background-color: #111827 !important;
        color: #ffffff !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        border: 1px solid #374151 !important;
        height: 54px !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"],
    div[data-baseweb="select"] * {
        background-color: #1e293b !important;
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: 800 !important;
    }

    .btn-rutina button {
        min-height: 56px !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 12px !important;
    }
    .btn-rutina-inactiva button {
        min-height: 56px !important;
        font-size: 21px !important;
        font-weight: 700 !important;
        background-color: #111827 !important;
        color: #cbd5e1 !important;
        border: 1px solid #374151 !important;
        border-radius: 12px !important;
    }

    .btn-empezar button {
        min-height: 64px !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, #0284c7 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
    }

    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        padding-top: 6px !important;
        padding-bottom: 6px !important;
    }
    div[data-testid="stExpander"] summary svg {
        fill: #ffffff !important;
        width: 22px !important;
        height: 22px !important;
    }

    .cabecera-maquina {
        background: #1e293b !important;
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        padding: 12px 14px !important;
        border-radius: 10px 10px 0 0 !important;
        border-left: 6px solid #38bdf8 !important;
        margin-top: 16px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
    }

    .cuerpo-maquina {
        background: #111827 !important;
        border: 1px solid #1e293b !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 12px !important;
        margin-bottom: 16px !important;
    }

    .lbl-col, div[data-testid="stNumberInput"] label p {
        font-size: 19px !important;
        font-weight: 800 !important;
        margin-bottom: 4px !important;
        text-align: center !important;
        color: #cbd5e1 !important;
    }

    div[data-testid="stNumberInput"] input {
        padding: 4px 1px !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        text-align: center !important;
        height: 50px !important;
        border-radius: 8px !important;
        color: #94a3b8 !important;
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
    }
    
    div[data-testid="stNumberInput"] button {
        display: none !important;
    }

    .caja-hecha {
        background: linear-gradient(180deg, #14532d 0%, #064e3b 100%) !important;
        border: 2px solid #22c55e !important;
        border-radius: 8px !important;
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        box-shadow: 0 0 8px rgba(34, 197, 94, 0.35) !important;
    }

    div[data-testid="stCheckbox"] {
        margin-top: 26px !important;
        display: flex !important;
        justify-content: flex-start !important;
    }
    div[data-testid="stCheckbox"] label span,
    div[data-testid="stCheckbox"] label p {
        font-size: 20px !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        margin-left: 2px !important;
    }
    div[data-testid="stCheckbox"] input[type="checkbox"] {
        width: 26px !important;
        height: 26px !important;
    }

    .btn-del-serie button {
        margin-top: 26px !important;
        height: 50px !important;
        width: 100% !important;
        padding: 0 !important;
        font-size: 21px !important;
        font-weight: 900 !important;
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border: 1px solid #374151 !important;
    }

    button,
    button p,
    button span,
    div[data-testid="stButton"] button p {
        font-size: 20px !important;
        font-weight: 800 !important;
    }
    button {
        min-height: 54px !important;
        border-radius: 10px !important;
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
    }

    .btn-saltar-descanso button {
        min-height: 48px !important;
        font-size: 19px !important;
        font-weight: 800 !important;
        background-color: #374151 !important;
        color: #f1f5f9 !important;
        border: 1px solid #4b5563 !important;
        border-radius: 10px !important;
        margin-top: -6px !important;
        margin-bottom: 12px !important;
    }

    div[data-testid="stProgress"] > div > div > div, .stProgress p {
        font-size: 19px !important;
        font-weight: 700 !important;
        color: #e2e8f0 !important;
    }

    .last-record-tag {
        font-size: 16px !important;
        color: #38bdf8 !important;
        background-color: rgba(56, 189, 248, 0.15);
        padding: 6px 12px;
        border-radius: 8px;
        display: inline-block;
        margin-bottom: 12px;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

CATALOGO_BASE = {
    "[Pecho] Chest Press": "Empuje horizontal guiado (Biostrength)",
    "[Pecho] Pectoral": "Aperturas en máquina (Biostrength)",
    "[Pecho] Press Banca Barra": "Básico de fuerza con barra libre",
    "[Pecho] Press Inclinado Mancuernas": "Zona superior con mancuernas",
    "[Pecho] Cruces de Poleas": "Aperturas en polea",
    "[Pecho] Fondos en Paralelas": "Pectoral inferior y tríceps",
    "[Pecho] Flexiones (Push-ups)": "Peso corporal",

    "[Espalda] Vertical Traction": "Jalón vertical guiado (Biostrength)",
    "[Espalda] Low Row": "Remo bajo guiado (Biostrength)",
    "[Espalda] Reverse Fly": "Deltoides posterior / espalda (Biostrength)",
    "[Espalda] Dominadas": "Dorsal ancho con peso corporal/asistido",
    "[Espalda] Jalón al Pecho Polea": "Polea alta con agarre ancho",
    "[Espalda] Remo con Mancuerna": "Remo unilateral en banco",
    "[Espalda] Remo Gironda Polea": "Remo sentado en polea baja",
    "[Espalda] Peso Muerto": "Cadena posterior completa",

    "[Hombro] Shoulder Press": "Empuje vertical guiado (Biostrength)",
    "[Hombro] Press Militar Mancuernas": "Empuje vertical de pie/sentado",
    "[Hombro] Elevaciones Laterales": "Deltoides lateral (Mancuernas / Polea)",
    "[Hombro] Pájaros con Mancuernas": "Deltoides posterior",
    "[Hombro] Face Pull Polea": "Deltoides posterior y rotadores",

    "[Pierna] Leg Press": "Prensa global guiada (Biostrength)",
    "[Pierna] Leg Extension": "Cuádriceps guiado (Biostrength)",
    "[Pierna] Leg Curl": "Isquiotibiales guiado (Biostrength)",
    "[Pierna] Abductor": "Glúteo medio / cadera (Biostrength)",
    "[Pierna] Adductor": "Aductores guiado (Biostrength)",
    "[Pierna] Sentadilla con Barra / Goblet": "Sentadilla libre o mancuerna",
    "[Pierna] Zancadas (Lunges)": "Trabajo unilateral de piernas",
    "[Pierna] Hip Thrust": "Glúteo mayor en banco",
    "[Pierna] Gemelos en Máquina / Pie": "Pantorrillas",

    "[Bíceps] Arm Curl": "Bíceps en máquina (Biostrength)",
    "[Bíceps] Curl Mancuernas": "Bíceps de pie o en banco",
    "[Bíceps] Curl Martillo": "Braquial y antebrazo con mancuernas",
    "[Tríceps] Arm Extension": "Tríceps en máquina (Biostrength)",
    "[Tríceps] Tríceps Polea Cuerda": "Extensión en polea alta",
    "[Tríceps] Press Francés": "Tríceps con barra Z o mancuernas",

    "[Abdomen] Plancha Isométrica": "Core / estabilidad (en segundos)",
    "[Abdomen] Crunch Polea": "Abdomen con carga",
    "[Abdomen] Elevación de Piernas": "Abdomen inferior colgado"
}

RUTINAS_DEFECTO = {
    "Torso Completo (Fuerza)": [
        {"name": "Chest Press", "series": [{"reps": 12, "peso": 40, "descanso": 90, "done": False}, {"reps": 10, "peso": 45, "descanso": 90, "done": False}, {"reps": 8, "peso": 50, "descanso": 90, "done": False}]},
        {"name": "Low Row", "series": [{"reps": 10, "peso": 45, "descanso": 90, "done": False}, {"reps": 10, "peso": 50, "descanso": 90, "done": False}, {"reps": 10, "peso": 50, "descanso": 90, "done": False}]},
        {"name": "Shoulder Press", "series": [{"reps": 10, "peso": 30, "descanso": 90, "done": False}, {"reps": 8, "peso": 35, "descanso": 90, "done": False}, {"reps": 8, "peso": 40, "descanso": 90, "done": False}]},
        {"name": "Vertical Traction", "series": [{"reps": 10, "peso": 45, "descanso": 90, "done": False}, {"reps": 10, "peso": 45, "descanso": 90, "done": False}, {"reps": 8, "peso": 50, "descanso": 90, "done": False}]},
        {"name": "Arm Extension", "series": [{"reps": 12, "peso": 30, "descanso": 60, "done": False}, {"reps": 12, "peso": 30, "descanso": 60, "done": False}]},
        {"name": "Arm Curl", "series": [{"reps": 12, "peso": 25, "descanso": 60, "done": False}, {"reps": 12, "peso": 30, "descanso": 60, "done": False}]}
    ],
    "Pierna y Tren Inferior": [
        {"name": "Leg Press", "series": [{"reps": 12, "peso": 70, "descanso": 120, "done": False}, {"reps": 10, "peso": 80, "descanso": 120, "done": False}, {"reps": 10, "peso": 90, "descanso": 120, "done": False}, {"reps": 8, "peso": 100, "descanso": 120, "done": False}]},
        {"name": "Leg Extension", "series": [{"reps": 12, "peso": 35, "descanso": 90, "done": False}, {"reps": 10, "peso": 40, "descanso": 90, "done": False}, {"reps": 10, "peso": 45, "descanso": 90, "done": False}]},
        {"name": "Leg Curl", "series": [{"reps": 12, "peso": 30, "descanso": 90, "done": False}, {"reps": 10, "peso": 35, "descanso": 90, "done": False}, {"reps": 10, "peso": 35, "descanso": 90, "done": False}]},
        {"name": "Abductor", "series": [{"reps": 15, "peso": 40, "descanso": 60, "done": False}, {"reps": 15, "peso": 45, "descanso": 60, "done": False}, {"reps": 15, "peso": 50, "descanso": 60, "done": False}]},
        {"name": "Adductor", "series": [{"reps": 15, "peso": 35, "descanso": 60, "done": False}, {"reps": 15, "peso": 40, "descanso": 60, "done": False}, {"reps": 15, "peso": 45, "descanso": 60, "done": False}]}
    ],
    "Full Body Eficiente": [
        {"name": "Leg Press", "series": [{"reps": 12, "peso": 70, "descanso": 90, "done": False}, {"reps": 10, "peso": 80, "descanso": 90, "done": False}, {"reps": 8, "peso": 85, "descanso": 90, "done": False}]},
        {"name": "Chest Press", "series": [{"reps": 10, "peso": 40, "descanso": 90, "done": False}, {"reps": 10, "peso": 45, "descanso": 90, "done": False}, {"reps": 8, "peso": 50, "descanso": 90, "done": False}]},
        {"name": "Vertical Traction", "series": [{"reps": 10, "peso": 40, "descanso": 90, "done": False}, {"reps": 10, "peso": 45, "descanso": 90, "done": False}, {"reps": 8, "peso": 50, "descanso": 90, "done": False}]},
        {"name": "Leg Curl", "series": [{"reps": 12, "peso": 30, "descanso": 75, "done": False}, {"reps": 10, "peso": 35, "descanso": 75, "done": False}]},
        {"name": "Reverse Fly", "series": [{"reps": 12, "peso": 25, "descanso": 60, "done": False}, {"reps": 10, "peso": 30, "descanso": 60, "done": False}]}
    ]
}

RUTINAS_FILE = "mis_rutinas.json"
HISTORIAL_FILE = "historial_marcas.json"
CONFIG_FILE = "config_garmin.json"
EJERCICIOS_CUSTOM_FILE = "mis_ejercicios.json"
GARMIN_TOKENS_FILE = "garmin_tokens.json"

def limpiar_nombre(nombre):
    s = re.sub(r"^\[.*?\]\s*", "", nombre)
    s = s.replace("Biostrength ", "").strip()
    return s

def cargar_catalogo_completo():
    catalogo = copy.deepcopy(CATALOGO_BASE)
    if os.path.exists(EJERCICIOS_CUSTOM_FILE):
        try:
            with open(EJERCICIOS_CUSTOM_FILE, "r", encoding="utf-8") as f:
                guardados = json.load(f)
                catalogo.update(guardados)
        except Exception:
            pass
    return dict(sorted(catalogo.items()))

def guardar_ejercicio_en_catalogo(nombre_con_grupo, descripcion="Ejercicio personalizado"):
    cat_actual = {}
    if os.path.exists(EJERCICIOS_CUSTOM_FILE):
        try:
            with open(EJERCICIOS_CUSTOM_FILE, "r", encoding="utf-8") as f:
                cat_actual = json.load(f)
        except Exception:
            cat_actual = {}
    cat_actual[nombre_con_grupo] = descripcion
    with open(EJERCICIOS_CUSTOM_FILE, "w", encoding="utf-8") as f:
        json.dump(cat_actual, f, ensure_ascii=False, indent=2)

def cargar_todas_las_rutinas():
    rutinas = copy.deepcopy(RUTINAS_DEFECTO)
    if os.path.exists(RUTINAS_FILE):
        try:
            with open(RUTINAS_FILE, "r", encoding="utf-8") as f:
                guardadas = json.load(f)
                for r_k, ej_list in guardadas.items():
                    for ej in ej_list:
                        ej["name"] = limpiar_nombre(ej["name"])
                rutinas.update(guardadas)
        except Exception:
            pass
    return rutinas

def guardar_rutina_personalizada(nombre, lista_ejercicios):
    guardadas = {}
    if os.path.exists(RUTINAS_FILE):
        try:
            with open(RUTINAS_FILE, "r", encoding="utf-8") as f:
                guardadas = json.load(f)
        except Exception:
            guardadas = {}
    
    ejercicios_limpios = copy.deepcopy(lista_ejercicios)
    for ej in ejercicios_limpios:
        ej["name"] = limpiar_nombre(ej["name"])
        for s in ej["series"]:
            s["done"] = False
            
    guardadas[nombre] = ejercicios_limpios
    with open(RUTINAS_FILE, "w", encoding="utf-8") as f:
        json.dump(guardadas, f, ensure_ascii=False, indent=2)

def borrar_rutina_personalizada(nombre):
    if os.path.exists(RUTINAS_FILE):
        try:
            with open(RUTINAS_FILE, "r", encoding="utf-8") as f:
                guardadas = json.load(f)
            if nombre in guardadas:
                del guardadas[nombre]
                with open(RUTINAS_FILE, "w", encoding="utf-8") as f:
                    json.dump(guardadas, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
                raw_hist = json.load(f)
                hist_limpio = {}
                for k, v in raw_hist.items():
                    hist_limpio[limpiar_nombre(k)] = v
                return hist_limpio
        except Exception:
            return {}
    return {}

def guardar_historial_sesion(ejercicios):
    historial = cargar_historial()
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    for ej in ejercicios:
        nombre = limpiar_nombre(ej["name"])
        resumen_series = [
            {"peso": int(s["peso"]), "reps": int(s["reps"]), "descanso": int(s["descanso"])}
            for s in ej["series"]
        ]
        historial[nombre] = {
            "fecha": fecha_hoy,
            "series": resumen_series
        }
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)

def cargar_credenciales_guardadas():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"email": "", "password": ""}

def guardar_credenciales(email, password):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"email": email, "password": password}, f, ensure_ascii=False)

def obtener_cliente_garmin(email, password, mfa_code=None):
    """Manejo de sesión de Garmin con soporte de MFA y persistencia de tokens"""
    if Garmin is None:
        raise Exception("Librería garminconnect no instalada en requirements.txt")
        
    client = Garmin(email, password)
    
    # Si ya tenemos tokens guardados, intentar usarlos
    if os.path.exists(GARMIN_TOKENS_FILE) and not mfa_code:
        try:
            with open(GARMIN_TOKENS_FILE, "r", encoding="utf-8") as f:
                token_data = json.load(f)
            client.login(token_data)
            return client, None
        except Exception:
            pass

    # Login estándar o con código MFA
    try:
        if mfa_code:
            client.login(mfa_code=mfa_code)
        else:
            client.login()
            
        # Guardar tokens para futuras sesiones
        try:
            tokens = client.garth.dumps()
            with open(GARMIN_TOKENS_FILE, "w", encoding="utf-8") as f:
                json.dump(tokens, f)
        except Exception:
            pass
            
        return client, None
    except GarminConnectMFAError:
        return None, "MFA_REQUIRED"
    except Exception as e:
        msg = str(e)
        if "MFA" in msg or "code" in msg.lower():
            return None, "MFA_REQUIRED"
        raise e

def crear_payload_garmin(nombre, ejercicios):
    steps = []
    order = 1
    for ej in ejercicios:
        nom = limpiar_nombre(ej["name"])
        for s_num, s in enumerate(ej["series"]):
            steps.append({
                "type": "WorkoutRepeatStep",
                "stepId": order,
                "stepOrder": order,
                "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "reps"},
                "endConditionValue": int(s["reps"]),
                "description": f"{nom} - S{s_num+1}/{len(ej['series'])} @ {int(s['peso'])}kg"
            })
            order += 1
            
            steps.append({
                "type": "WorkoutStep",
                "stepId": order,
                "stepOrder": order,
                "stepType": {"stepTypeId": 4, "stepTypeKey": "rest"},
                "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                "endConditionValue": int(s["descanso"]),
                "description": f"Descanso {int(s['descanso'])}s"
            })
            order += 1
            
    return {
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
        "workoutName": nombre,
        "workoutSegments": [{"segmentOrder": 1, "workoutSteps": steps}]
    }

# Inicialización
todas_las_rutinas = cargar_todas_las_rutinas()
historial_marcas = cargar_historial()
cred_guardadas = cargar_credenciales_guardadas()
catalogo_ejercicios = cargar_catalogo_completo()

if "pantalla" not in st.session_state:
    st.session_state.pantalla = "inicio"

if "rutina_activa" not in st.session_state:
    st.session_state.rutina_activa = "Torso Completo (Fuerza)"

if "ejercicios" not in st.session_state:
    ej_iniciar = copy.deepcopy(todas_las_rutinas[st.session_state.rutina_activa])
    for ej in ej_iniciar:
        ej["name"] = limpiar_nombre(ej["name"])
    st.session_state.ejercicios = ej_iniciar

if "email_garmin" not in st.session_state:
    st.session_state.email_garmin = cred_guardadas.get("email", "")

if "pass_garmin" not in st.session_state:
    st.session_state.pass_garmin = cred_guardadas.get("password", "")

if "esperando_mfa" not in st.session_state:
    st.session_state.esperando_mfa = False

# Variables del temporizador
if "timer_segundos" not in st.session_state:
    st.session_state.timer_segundos = 0
if "timer_id" not in st.session_state:
    st.session_state.timer_id = 0


# ==============================================================================
# PANTALLA 1: INICIO Y PREPARACIÓN
# ==============================================================================
if st.session_state.pantalla == "inicio":
    st.title("⚡ Biostrength")
    st.caption("Preparación del entrenamiento")
    
    # 1. Credenciales Garmin
    with st.expander("🔑 Credenciales Garmin Connect", expanded=False):
        email_in = st.text_input("Email", value=st.session_state.email_garmin, placeholder="tu_email@ejemplo.com")
        pass_in = st.text_input("Contraseña", value=st.session_state.pass_garmin, type="password")
        
        if st.button("💾 Guardar credenciales en este móvil", use_container_width=True):
            guardar_credenciales(email_in, pass_in)
            st.session_state.email_garmin = email_in
            st.session_state.pass_garmin = pass_in
            # Limpiar tokens viejos si se cambian credenciales
            if os.path.exists(GARMIN_TOKENS_FILE):
                os.remove(GARMIN_TOKENS_FILE)
            st.success("¡Credenciales guardadas!")

    st.write("---")
    
    # 2. Selección de Rutina existente
    st.subheader("📋 Elige la Rutina de Hoy")
    nombres_rutinas = list(todas_las_rutinas.keys())
    
    for r_nom in nombres_rutinas:
        es_activa = (r_nom == st.session_state.rutina_activa)
        clase = "btn-rutina" if es_activa else "btn-rutina-inactiva"
        icono = "▶ " if es_activa else ""
        st.markdown(f'<div class="{clase}">', unsafe_allow_html=True)
        if st.button(f"{icono}{r_nom}", key=f"lobby_r_{r_nom}", use_container_width=True):
            st.session_state.rutina_activa = r_nom
            nuevos_ejs = copy.deepcopy(todas_las_rutinas[r_nom])
            for ej in nuevos_ejs:
                ej["name"] = limpiar_nombre(ej["name"])
            st.session_state.ejercicios = nuevos_ejs
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    
    # Botón Gigante de Comienzo
    st.markdown('<div class="btn-empezar">', unsafe_allow_html=True)
    if st.button(f"🚀 EMPEZAR: {st.session_state.rutina_activa.upper()}", use_container_width=True):
        st.session_state.pantalla = "entreno"
        st.session_state.timer_segundos = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Eliminar rutina si es personalizada
    if st.session_state.rutina_activa not in RUTINAS_DEFECTO:
        st.write("")
        if st.button(f"🗑 Eliminar rutina '{st.session_state.rutina_activa}'", use_container_width=True):
            borrar_rutina_personalizada(st.session_state.rutina_activa)
            st.session_state.rutina_activa = "Torso Completo (Fuerza)"
            st.session_state.ejercicios = copy.deepcopy(todas_las_rutinas["Torso Completo (Fuerza)"])
            st.success("Rutina eliminada.")
            st.rerun()

    st.write("---")

    # 3. CREAR NUEVA RUTINA PERSONALIZADA
    with st.expander("➕ Crear Nueva Rutina Personalizada", expanded=False):
        nom_nueva = st.text_input("Nombre de la nueva rutina:", placeholder="Ej: Torso + Brazos", key="nueva_rut_nombre")
        
        st.markdown("**Selecciona los ejercicios (agrupados por músculo):**")
        maquinas_elegidas = []
        for ej_k, ej_desc in catalogo_ejercicios.items():
            if st.checkbox(f"{ej_k} — {ej_desc}", key=f"chk_nueva_{ej_k}"):
                maquinas_elegidas.append(ej_k)
        
        col_ns, col_np, col_nr = st.columns(3)
        with col_ns:
            n_ser_default = st.number_input("Series/ej", min_value=1, max_value=6, value=3, format="%d", key="ns_def")
        with col_np:
            n_pes_default = st.number_input("Kg base", min_value=0, max_value=250, value=30, format="%d", key="np_def")
        with col_nr:
            n_rep_default = st.number_input("Reps", min_value=1, max_value=30, value=10, format="%d", key="nr_def")
            
        if st.button("💾 Guardar y Seleccionar Rutina", use_container_width=True):
            if not nom_nueva.strip():
                st.error("Escribe un nombre para la rutina.")
            elif not maquinas_elegidas:
                st.error("Selecciona al menos un ejercicio.")
            else:
                lista_nueva = []
                for m_nom_raw in maquinas_elegidas:
                    m_nom = limpiar_nombre(m_nom_raw)
                    p_base = n_pes_default
                    if m_nom in historial_marcas and historial_marcas[m_nom]["series"]:
                        p_base = historial_marcas[m_nom]["series"][-1]["peso"]
                        
                    series_m = [
                        {"peso": int(p_base), "reps": int(n_rep_default), "descanso": 90, "done": False}
                        for _ in range(int(n_ser_default))
                    ]
                    lista_nueva.append({"name": m_nom, "series": series_m})
                
                guardar_rutina_personalizada(nom_nueva.strip(), lista_nueva)
                st.session_state.rutina_activa = nom_nueva.strip()
                st.session_state.ejercicios = copy.deepcopy(lista_nueva)
                st.success(f"¡Rutina '{nom_nueva}' creada y lista!")
                st.rerun()

    # 4. AÑADIR OTRO EJERCICIO LIBRE AL CATÁLOGO
    with st.expander("🆕 Añadir Otro Ejercicio al Catálogo", expanded=False):
        c_grp, c_ej1, c_ej2 = st.columns([1.2, 1.5, 1.5])
        with c_grp:
            grupo_sel = st.selectbox("Grupo:", ["[Pecho]", "[Espalda]", "[Hombro]", "[Pierna]", "[Bíceps]", "[Tríceps]", "[Abdomen]", "[Otro]"])
        with c_ej1:
            nuevo_ej_nom = st.text_input("Nombre:", placeholder="Ej: Press Francés", key="custom_ej_name")
        with c_ej2:
            nuevo_ej_desc = st.text_input("Descripción:", placeholder="Ej: Barra Z en banco", key="custom_ej_desc")
            
        if st.button("➕ Guardar en mi lista de ejercicios", use_container_width=True):
            if not nuevo_ej_nom.strip():
                st.error("Escribe el nombre del ejercicio.")
            else:
                desc = nuevo_ej_desc.strip() if nuevo_ej_desc.strip() else "Ejercicio personalizado"
                nombre_con_grupo = f"{grupo_sel} {limpiar_nombre(nuevo_ej_nom.strip())}"
                guardar_ejercicio_en_catalogo(nombre_con_grupo, desc)
                st.success(f"¡'{nombre_con_grupo}' añadido al catálogo!")
                st.rerun()

    # 5. Récords / Historial
    with st.expander("📈 Ver mis marcas anteriores", expanded=False):
        if not historial_marcas:
            st.caption("Aún no tienes marcas registradas.")
        else:
            for m_nom, m_dat in historial_marcas.items():
                st.markdown(f"**{m_nom}** *({m_dat['fecha']})*")
                res_str = " • ".join([f"S{i+1}: {s['peso']}kg × {s['reps']}" for i, s in enumerate(m_dat['series'])])
                st.caption(res_str)


# ==============================================================================
# PANTALLA 2: ENTRENAMIENTO EN VIVO
# ==============================================================================
elif st.session_state.pantalla == "entreno":
    
    # Barra superior
    c_tit, c_vol = st.columns([3, 1.2])
    with c_tit:
        st.title("⚡ Biostrength")
    with c_vol:
        st.write("")
        if st.button("⬅ Salir", use_container_width=True):
            st.session_state.pantalla = "inicio"
            st.session_state.timer_segundos = 0
            st.rerun()

    st.subheader(f"🏋️ {st.session_state.rutina_activa}")

    # ==========================================================================
    # TEMPORIZADOR DE DESCANSO
    # ==========================================================================
    if st.session_state.timer_segundos > 0:
        timer_secs = st.session_state.timer_segundos
        t_id = st.session_state.timer_id
        
        st.components.v1.html(f"""
        <!-- t_id: {t_id} -->
        <div id="rest-box" style="
            background: linear-gradient(135deg, #111827 0%, #030712 100%);
            border: 2px solid #38bdf8;
            box-shadow: 0 4px 16px rgba(56, 189, 248, 0.4);
            border-radius: 14px;
            padding: 12px;
            text-align: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="font-size: 15px; font-weight: 800; color: #94a3b8; text-transform: uppercase;">
                ⏱️ Descanso en curso
            </div>
            <div id="tdisp" style="
                font-size: 54px;
                font-weight: 900;
                color: #ffffff;
                line-height: 1.1;
                margin: 4px 0;
                font-variant-numeric: tabular-nums;
            ">--:--</div>
            
            <div style="width: 100%; background: #1f2937; border-radius: 6px; height: 8px; overflow: hidden;">
                <div id="tbar" style="width: 100%; height: 100%; background: #38bdf8; transition: width 1s linear;"></div>
            </div>
        </div>

        <script>
        (function() {{
            var total = {timer_secs};
            var rem = total;
            var disp = document.getElementById('tdisp');
            var bar = document.getElementById('tbar');

            var actx = null;
            function beep(f, dur, dly) {{
                setTimeout(function() {{
                    try {{
                        if (!actx) {{ actx = new (window.AudioContext || window.webkitAudioContext)(); }}
                        if (actx.state === 'suspended') {{ actx.resume(); }}
                        var osc = actx.createOscillator();
                        var g = actx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(f, actx.currentTime);
                        g.gain.setValueAtTime(0.3, actx.currentTime);
                        g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + dur);
                        osc.connect(g);
                        gain = null;
                        osc.connect(actx.destination);
                        osc.start();
                        osc.stop(actx.currentTime + dur);
                    }} catch(e) {{}}
                }}, dly);
            }}

            function tripleBeep() {{
                beep(880, 0.15, 0);
                beep(880, 0.15, 300);
                beep(1760, 0.6, 600);
            }}

            function fmt(s) {{
                var m = Math.floor(s / 60);
                var sec = s % 60;
                return (m < 10 ? '0' : '') + m + ':' + (sec < 10 ? '0' : '') + sec;
            }}

            function refresh() {{
                disp.innerText = fmt(rem);
                var pct = Math.max(0, (rem / total) * 100);
                bar.style.width = pct + '%';
                if (rem <= 5) {{
                    bar.style.background = '#22c55e';
                    disp.style.color = '#4ade80';
                }}
            }}

            refresh();
            var iv = setInterval(function() {{
                rem--;
                if (rem <= 0) {{
                    clearInterval(iv);
                    refresh();
                    disp.innerText = "¡A POR ELLO!";
                    tripleBeep();
                }} else {{
                    refresh();
                }}
            }}, 1000);
        }})();
        </script>
        """, height=125)

        st.markdown('<div class="btn-saltar-descanso">', unsafe_allow_html=True)
        if st.button("⏭️ Saltar / Quitar Descanso", use_container_width=True, key=f"skip_btn_{t_id}"):
            st.session_state.timer_segundos = 0
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Barra de progreso general
    total_series = sum(len(e["series"]) for e in st.session_state.ejercicios)
    total_completadas = sum(sum(1 for s in e["series"] if s.get("done", False)) for e in st.session_state.ejercicios)
    progreso = total_completadas / total_series if total_series > 0 else 0.0
    st.progress(progreso, text=f"Progreso: {total_completadas}/{total_series} series ({int(progreso*100)}%)")

    # Lista de ejercicios en sesión
    for e_idx, ej in enumerate(st.session_state.ejercicios):
        nom_ejercicio = limpiar_nombre(ej["name"])
        ej["name"] = nom_ejercicio
        
        st.markdown(
            f'''<div class="cabecera-maquina">
                <span>🏋️ {nom_ejercicio}</span>
                <span style="font-size:18px; font-weight:700; color:#93c5fd;">({len(ej["series"])} series)</span>
            </div>''',
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="cuerpo-maquina">', unsafe_allow_html=True)
        
        if nom_ejercicio in historial_marcas:
            ultimo = historial_marcas[nom_ejercicio]
            detalles = " | ".join([f"S{i+1}: {s['peso']}kg×{s['reps']}" for i, s in enumerate(ultimo["series"])])
            st.markdown(f'<div class="last-record-tag">📌 Último ({ultimo["fecha"]}): {detalles}</div>', unsafe_allow_html=True)
        
        for s_idx, s in enumerate(ej["series"]):
            col_chk, col_p, col_r, col_d, col_x = st.columns([1.5, 2.2, 2.0, 2.1, 1.0])
            
            with col_chk:
                is_done = s.get("done", False)
                chk_label = f"S{s_idx+1}"
                nuevo_done = st.checkbox(chk_label, value=is_done, key=f"chk_{e_idx}_{s_idx}")
                
                if nuevo_done != is_done:
                    s["done"] = nuevo_done
                    if nuevo_done:
                        st.session_state.timer_segundos = int(s["descanso"])
                        st.session_state.timer_id = int(time.time() * 1000)
                    else:
                        st.session_state.timer_segundos = 0
                    st.rerun()

            # SI ESTÁ HECHA: Blanco puro + marco verde neón
            if s["done"]:
                with col_p:
                    st.markdown('<p class="lbl-col" style="color:#4ade80 !important;">Kg</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="caja-hecha">{int(round(s["peso"]))}</div>', unsafe_allow_html=True)
                with col_r:
                    st.markdown('<p class="lbl-col" style="color:#4ade80 !important;">Reps</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="caja-hecha">{int(s["reps"])}</div>', unsafe_allow_html=True)
                with col_d:
                    st.markdown('<p class="lbl-col" style="color:#4ade80 !important;">Desc(s)</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="caja-hecha">{int(s["descanso"])}</div>', unsafe_allow_html=True)

            # SI ESTÁ PENDIENTE: Inputs de edición
            else:
                with col_p:
                    s["peso"] = st.number_input(
                        "Kg", min_value=0, max_value=300, 
                        value=int(round(s["peso"])), step=1, format="%d", key=f"p_{e_idx}_{s_idx}"
                    )
                with col_r:
                    s["reps"] = st.number_input(
                        "Reps", min_value=1, max_value=50, 
                        value=int(s["reps"]), step=1, format="%d", key=f"r_{e_idx}_{s_idx}"
                    )
                with col_d:
                    s["descanso"] = st.number_input(
                        "Desc(s)", min_value=15, max_value=300, 
                        value=int(s["descanso"]), step=15, format="%d", key=f"d_{e_idx}_{s_idx}"
                    )
            
            with col_x:
                st.markdown('<div class="btn-del-serie">', unsafe_allow_html=True)
                if st.button("✕", key=f"del_s_{e_idx}_{s_idx}"):
                    ej["series"].pop(s_idx)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.write("")
        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            if st.button(f"➕ Añadir Serie", key=f"add_s_{e_idx}", use_container_width=True):
                last_p = int(round(ej["series"][-1]["peso"])) if ej["series"] else 40
                last_r = int(ej["series"][-1]["reps"]) if ej["series"] else 10
                last_d = int(ej["series"][-1]["descanso"]) if ej["series"] else 90
                ej["series"].append({"peso": last_p, "reps": last_r, "descanso": last_d, "done": False})
                st.rerun()
        with btn_c2:
            if st.button(f"🗑️ Quitar Ejercicio", key=f"del_ej_{e_idx}", use_container_width=True):
                st.session_state.ejercicios.pop(e_idx)
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. AÑADIR EJERCICIO A LA SESIÓN
    st.write("---")
    with st.expander("➕ Añadir ejercicio a esta sesión", expanded=False):
        opciones_todos = [f"{k} — {v}" for k, v in catalogo_ejercicios.items()]
        opciones_todos.append("✨ Escribir otro ejercicio nuevo...")
        
        sel_item = st.selectbox("Elige o escribe ejercicio (ordenado por grupo):", opciones_todos)
        
        nombre_final = ""
        if sel_item == "✨ Escribir otro ejercicio nuevo...":
            nombre_final = st.text_input("Nombre del ejercicio libre:", placeholder="Ej: Fondos en suelo", key="free_ej_input").strip()
            desc_libre = st.text_input("Descripción / Músculo:", placeholder="Ej: Pectoral / Tríceps", key="free_ej_desc").strip()
        else:
            raw_nom = sel_item.split(" — ")[0]
            nombre_final = limpiar_nombre(raw_nom)

        def_peso, def_reps, def_series, def_desc = 30, 10, 3, 90
        if nombre_final in historial_marcas and historial_marcas[nombre_final]["series"]:
            prev_s = historial_marcas[nombre_final]["series"]
            def_peso = int(round(prev_s[-1]["peso"]))
            def_reps = int(prev_s[-1]["reps"])
            def_series = len(prev_s)
            def_desc = int(prev_s[-1]["descanso"])
        
        c_ns, c_np, c_nr, c_nd = st.columns(4)
        n_series = c_ns.number_input("Nº series", min_value=1, max_value=8, value=def_series, format="%d", key="ent_s")
        n_peso = c_np.number_input("Kg", min_value=0, max_value=250, value=def_peso, step=1, format="%d", key="ent_p")
        n_reps = c_nr.number_input("Reps", min_value=1, max_value=30, value=def_reps, format="%d", key="ent_r")
        n_desc = c_nd.number_input("Descanso (s)", min_value=15, max_value=300, value=def_desc, step=15, format="%d", key="ent_d")
        
        if st.button("Añadir a la Sesión", use_container_width=True):
            if not nombre_final:
                st.error("Por favor, introduce el nombre del ejercicio.")
            else:
                if sel_item == "✨ Escribir otro ejercicio nuevo...":
                    guardar_ejercicio_en_catalogo(f"[Otro] {nombre_final}", desc_libre if desc_libre else "Ejercicio libre")
                
                nuevas_series = [{"peso": int(n_peso), "reps": int(n_reps), "descanso": int(n_desc), "done": False} for _ in range(int(n_series))]
                st.session_state.ejercicios.append({"name": nombre_final, "series": nuevas_series})
                st.rerun()

    # Actualizar la plantilla
    with st.expander("💾 Guardar cambios en esta plantilla", expanded=False):
        if st.button(f"Sobrescribir '{st.session_state.rutina_activa}' con estos ejercicios", use_container_width=True):
            guardar_rutina_personalizada(st.session_state.rutina_activa, st.session_state.ejercicios)
            st.success("¡Plantilla actualizada!")

    # Finalizar sesión
    st.write("---")
    col_fin1, col_fin2 = st.columns([1, 1])
    with col_fin1:
        if st.button("💾 Guardar Marcas", use_container_width=True):
            guardar_historial_sesion(st.session_state.ejercicios)
            st.success("¡Marcas de hoy guardadas!")
            
    with col_fin2:
        btn_garmin = st.button("⚡ Enviar a Garmin", use_container_width=True)

    # INTERFAZ PARA CÓDIGO DE SEGURIDAD (MFA)
    if st.session_state.esperando_mfa:
        st.warning("📩 Garmin ha enviado un código de seguridad a tu móvil o email.")
        codigo_mfa_in = st.text_input("Introduce el código de verificación:", placeholder="Ej: 123456", key="mfa_box")
        if st.button("🔑 Validar Código y Conectar con Garmin", use_container_width=True):
            if not codigo_mfa_in.strip():
                st.error("Por favor, escribe el código recibido.")
            else:
                with st.spinner("Validando código y guardando autorización..."):
                    try:
                        client, mfa_status = obtener_cliente_garmin(
                            st.session_state.email_garmin,
                            st.session_state.pass_garmin,
                            mfa_code=codigo_mfa_in.strip()
                        )
                        if client:
                            st.session_state.esperando_mfa = False
                            payload = crear_payload_garmin(f"Biostrength - {st.session_state.rutina_activa}", st.session_state.ejercicios)
                            client.upload_workout(payload)
                            st.success("¡Código validado! Entrenamiento enviado a Garmin.")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("El código introducido no es válido o ha caducado. Vuelve a pulsar 'Enviar a Garmin'.")
                    except Exception as err:
                        st.error(f"Error al validar código: {str(err)}")

    if btn_garmin:
        email_g = st.session_state.email_garmin
        pass_g = st.session_state.pass_garmin
        
        if Garmin is None:
            st.error("Falta la librería de Garmin. Asegúrate de tener 'garminconnect' en el archivo requirements.txt.")
        elif not email_g or not pass_g:
            st.error("No hay credenciales de Garmin guardadas. Vuelve al Inicio para introducirlas.")
        elif not st.session_state.ejercicios:
            st.error("No hay ejercicios para enviar.")
        else:
            with st.spinner("Conectando con Garmin Connect..."):
                try:
                    guardar_historial_sesion(st.session_state.ejercicios)
                    
                    client, mfa_status = obtener_cliente_garmin(email_g, pass_g)
                    
                    if mfa_status == "MFA_REQUIRED":
                        st.session_state.esperando_mfa = True
                        st.rerun()
                    elif client:
                        payload = crear_payload_garmin(f"Biostrength - {st.session_state.rutina_activa}", st.session_state.ejercicios)
                        client.upload_workout(payload)
                        st.success(f"¡Entrenamiento '{st.session_state.rutina_activa}' enviado con éxito a tu Garmin!")
                        st.balloons()
                except Exception as err:
                    msg = str(err)
                    if "MFA" in msg or "code" in msg.lower():
                        st.session_state.esperando_mfa = True
                        st.rerun()
                    else:
                        st.error(f"Error al conectar con Garmin: {msg}")
