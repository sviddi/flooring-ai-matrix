import streamlit as st
import json
import os
from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI
from curing_time_db import CURING_TIMES
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Настройки страницы должны быть первой командой Streamlit!
st.set_page_config(page_title="Flooring AI Consultant", layout="wide")

load_dotenv()

client = OpenAI()

# --- 1. LOAD DATABASE ---
@st.cache_data
def load_db():
    if not os.path.exists("systems_db.json"):
        st.error("Database systems_db.json not found!")
        st.stop()
    with open("systems_db.json", "r", encoding="utf-8") as f:
        return json.load(f)

db = load_db()

# --- 2. DEFINE STATE MODEL ---
class ProjectState(BaseModel):
    temperature: Optional[str] = Field(None, description="Service temperature: '< +5°C' or '> +5°C'")
    speed: Optional[str] = Field(None, description="Installation speed: 'Standard' or 'Accelerated'")
    life: Optional[str] = Field(None, description="Coating life: '< 5 years', '> 5 years', or '> 10 years'")
    uv_resistance: Optional[bool] = Field(None, description="True if UV resistance is required, False if not")
    area_m2: Optional[int] = Field(None, description="Parking area in square meters")
    reply_to_user: str = Field(..., description="Your conversational response or next question to the user")

# --- 3. LOGIC & CALCULATIONS ---
def find_best_system(state: dict):
    if state.get("speed") == "Accelerated":
        return next(s for s in db if s["id"] == "sys_04") 
    elif state.get("uv_resistance") is True:
        return next(s for s in db if s["id"] == "sys_01") 
    elif state.get("uv_resistance") is False and state.get("life") == "< 5 years":
        return next(s for s in db if s["id"] == "sys_03") 
    else:
        return next(s for s in db if s["id"] == "sys_02") 

def calculate_materials(recipe, area):
    calc_result = []
    for layer in recipe:
        x = layer.get("consumption_x_kg_m2")
        y = layer.get("packaging_y_kg")
        if x and y:
            total_kg = round(x * area, 1)
            total_packs = round(total_kg / y)
            calc_result.append(f"- **{layer['layer']}**: ~{x} kg/m² ➔ **{total_kg}kg** (~{total_packs} pcs)")
        else:
            calc_result.append(f"- **{layer['layer']}**: Consumption per TDS")
    return "\n".join(calc_result)

# --- 4. UI RENDERER FOR PROPOSAL CARDS ---
def render_proposal(sys_data, area):
    st.markdown(f"### 🏢 Technical Proposal (Area: {area} m²)")
    st.markdown(f"**Target Performance:** `{sys_data['standard_performance']}`")
    
    cols = st.columns(3)
    
    with cols[0]:
        with st.container(border=True):
            st.error(f"**🔴 Sika Baseline System**")
            st.markdown(f"**{sys_data['sika_system']['name']}**")
            st.markdown(calculate_materials(sys_data['sika_system']['recipe'], area))
            if sys_data['sika_system'].get('technical_note'):
                st.caption(f"_{sys_data['sika_system']['technical_note']}_")
            
    with cols[1]:
        with st.container(border=True):
            st.info(f"**🔵 Mapei Functional Alternative**")
            st.markdown(f"**{sys_data['mapei_analogue']['name']}**")
            st.markdown(calculate_materials(sys_data['mapei_analogue']['recipe'], area))
            if sys_data['mapei_analogue'].get('technical_note'):
                st.caption(f"_{sys_data['mapei_analogue']['technical_note']}_")
            
    with cols[2]:
        with st.container(border=True):
            st.success(f"**🟢 MC-Bauchemie Functional Alternative**")
            if "mc_bauchemie_analogue" in sys_data:
                st.markdown(f"**{sys_data['mc_bauchemie_analogue']['name']}**")
                st.markdown(calculate_materials(sys_data['mc_bauchemie_analogue']['recipe'], area))
                if sys_data['mc_bauchemie_analogue'].get('technical_note'):
                    st.caption(f"_{sys_data['mc_bauchemie_analogue']['technical_note']}_")
            else:
                st.markdown("No direct alternative mapped.")
                
    st.markdown("---")
    st.markdown("#### ⚖️ Engineering Analysis & Nuances")
    st.markdown(f"- **Similarities:** {sys_data['comparison']['similarities']}")
    st.markdown(f"- **Differences:** {sys_data['comparison']['differences_nuances']}")
    st.markdown(f"- **System Selection Reasoning:** {sys_data['comparison']['max_analogue_reasoning']}")
    
    st.warning("""
    **LEGAL DISCLAIMER:** All consumption figures (kg/m²) are theoretical and based on smooth, non-porous concrete substrates at +20°C. 
    Actual consumption on site may vary significantly due to surface profile (CSP), porosity, wastage, and application methods. 
    This calculation does not include standard waste allowances (typically 5-10%) and is intended for budget estimation purposes only. 
    It does not replace an official quote. Always verify values against the latest official Technical Data Sheet (TDS) before ordering materials.
    """)

@st.dialog("Project Schedule", width="large")
def show_schedule_modal(system_name, recipe, area):
    st.markdown(f"### {system_name}")
    
    daily_norm = st.number_input("Application rate (m²/day per crew):", min_value=50, value=1000, step=50)
    
    start_date = datetime.today().replace(hour=8, minute=0, second=0, microsecond=0)
    current_start = start_date
    schedule_data = []
    
    for item in recipe:
        material = item['material']
        layer_name = item['layer']
        
        app_days = area / daily_norm
        
        # Песок наносится параллельно жидкому слою (wet-on-wet)
        if "Broadcast" in layer_name or "Dry shake" in layer_name or "quartz sand" in material.lower():
            if schedule_data:
                actual_start = schedule_data[-1]["Start"]
                actual_end = schedule_data[-1]["End"]
            else:
                actual_start = current_start
                actual_end = current_start + timedelta(days=app_days)
        else:
            actual_start = current_start
            actual_end = actual_start + timedelta(days=app_days)
            
            curing_info = CURING_TIMES.get(material, {})
            wait_hours = curing_info.get("min_overcoating_time_h", 12.0)
            
            # Следующий слой сдвигается ровно на время высыхания первой "захватки"
            current_start = actual_start + timedelta(hours=wait_hours)
            
        schedule_data.append({
            "Layer": layer_name,
            "Material": material,
            "Start": actual_start,
            "End": actual_end
        })
        
    # Рассчитываем финальное время с учетом последней сушки под пешеходную нагрузку (foot traffic)
    max_end_date = max([item["End"] for item in schedule_data])
    last_material = recipe[-1]['material']
    final_cure_h = CURING_TIMES.get(last_material, {}).get("foot_traffic_h", 24.0)
    project_completion = max_end_date + timedelta(hours=final_cure_h)
    
    total_days = (project_completion - start_date).total_seconds() / 86400
    
    st.success(f"**Estimated total execution time (including curing):** ~{total_days:.1f} days")
    
    df = pd.DataFrame(schedule_data)
    fig = px.timeline(
        df, x_start="Start", x_end="End", y="Layer", 
        color="Material", title="Layer-by-layer Execution Schedule",
        text="Material"
    )
    fig.update_yaxes(autorange="reversed") 
    fig.update_layout(xaxis_title="Timeline", yaxis_title="Stages")
    
    st.plotly_chart(fig, use_container_width=True)

# --- 5. INITIALIZATION ---
st.title("🤖 Industrial Flooring AI Consultant")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "type": "text", "content": "Hello! I am your AI Technical Consultant. To recommend the best parking deck flooring system, I need to know a few details. What is the expected winter service temperature in the parking area?"}
    ]

if "project_state" not in st.session_state:
    st.session_state.project_state = {}

# Единый правильный сайдбар без дубликатов
with st.sidebar:
    st.header("⚙️ Internal Agent State")
    st.json(st.session_state.project_state)
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.session_state.project_state = {}
        st.rerun()
        
    proposal_msgs = [m for m in st.session_state.messages if m.get("type") == "proposal"]
    if proposal_msgs:
        st.markdown("---")
        st.header("📅 Apply Schedules")
        
        last_proposal = proposal_msgs[-1]
        sys_data = last_proposal["sys_data"]
        area = last_proposal["area"]
        
        if st.button(f"📊 Schedule: Sika"):
            show_schedule_modal(sys_data['sika_system']['name'], sys_data['sika_system']['recipe'], area)
            
        if st.button(f"📊 Schedule: Mapei"):
            show_schedule_modal(sys_data['mapei_analogue']['name'], sys_data['mapei_analogue']['recipe'], area)
            
        if "mc_bauchemie_analogue" in sys_data:
            if st.button(f"📊 Schedule: MC-Bauchemie"):
                show_schedule_modal(sys_data['mc_bauchemie_analogue']['name'], sys_data['mc_bauchemie_analogue']['recipe'], area)
    
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "proposal":
            render_proposal(msg["sys_data"], msg["area"])
        else:
            st.markdown(msg["content"])

# --- 6. CHAT LOGIC ---
if prompt := st.chat_input("Type your answer here..."):
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    system_prompt = f"""
    You are an expert flooring consultant. Your goal is to collect 5 parameters to select a system:
    1. Temperature (< +5°C or > +5°C)
    2. Speed (Standard or Accelerated)
    3. Life (< 5 years, > 5 years, > 10 years)
    4. UV resistance (Yes/No)
    5. Area (m2)
    
    Current collected state: {json.dumps(st.session_state.project_state)}
    
    Analyze the conversation and update the state. Keep previously collected parameters intact unless the user explicitly changes them.
    If any parameter is missing, ask the user politely for the NEXT missing parameter in your 'reply_to_user'. Ask only one question at a time.
    If all parameters are collected, say "Thank you! I am generating the technical proposal based on your requirements." in 'reply_to_user'.
    """
    
    api_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        if m.get("type") == "text":
            api_messages.append({"role": m["role"], "content": m["content"]})

    with st.spinner("Analyzing your requirements..."):
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=api_messages,
            response_format=ProjectState,
            temperature=0
        )
        
        parsed_result = response.choices[0].message.parsed
        new_state = parsed_result.model_dump(exclude_none=True)
        reply = new_state.pop("reply_to_user", "Processing...")
        st.session_state.project_state.update(new_state)
        
        st.session_state.messages.append({"role": "assistant", "type": "text", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
            
        # --- 7. TRIGGER RECOMMENDATION ---
        # --- 7. TRIGGER RECOMMENDATION ---
        required_keys = ["temperature", "speed", "life", "uv_resistance", "area_m2"]
        if all(key in st.session_state.project_state for key in required_keys):
            if not any(m.get("type") == "proposal" for m in st.session_state.messages):
                
                # Ищем подходящую систему и берем площадь
                sys_data = find_best_system(st.session_state.project_state)
                area = st.session_state.project_state["area_m2"]
                
                # Формируем сообщение с расчетом
                proposal_msg = {
                    "role": "assistant", 
                    "type": "proposal", 
                    "sys_data": sys_data, 
                    "area": area
                }
                
                # Сохраняем в историю чата
                st.session_state.messages.append(proposal_msg)
                
                # Перезагружаем интерфейс, чтобы сайдбар мгновенно увидел новые данные!
                st.rerun()