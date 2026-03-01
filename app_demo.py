import streamlit as st
import json
import os
from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

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
    
    # Юридический дисклеймер
    st.warning("""
    **LEGAL DISCLAIMER:** All consumption figures (kg/m²) are theoretical and based on smooth, non-porous concrete substrates at +20°C. 
    Actual consumption on site may vary significantly due to surface profile (CSP), porosity, wastage, and application methods. 
    This calculation does not include standard waste allowances (typically 5-10%) and is intended for budget estimation purposes only. 
    It does not replace an official quote. Always verify values against the latest official Technical Data Sheet (TDS) before ordering materials.
    """)

# --- 5. INITIALIZATION ---
st.set_page_config(page_title="Flooring AI Consultant", layout="wide")
st.title("🤖 Industrial Flooring AI Consultant")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "type": "text", "content": "Hello! I am your AI Technical Consultant. To recommend the best parking deck flooring system, I need to know a few details. What is the expected winter service temperature in the parking area?"}
    ]

if "project_state" not in st.session_state:
    st.session_state.project_state = {}

with st.sidebar:
    st.header("⚙️ Internal Agent State")
    st.json(st.session_state.project_state)
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.session_state.project_state = {}
        st.rerun()

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
        required_keys = ["temperature", "speed", "life", "uv_resistance", "area_m2"]
        if all(key in st.session_state.project_state for key in required_keys):
            if not any(m.get("type") == "proposal" for m in st.session_state.messages):
                st.success("All requirements collected! Generating Technical Proposal...")
                
                sys_data = find_best_system(st.session_state.project_state)
                area = st.session_state.project_state["area_m2"]
                
                proposal_msg = {
                    "role": "assistant", 
                    "type": "proposal", 
                    "sys_data": sys_data, 
                    "area": area
                }
                st.session_state.messages.append(proposal_msg)
                
                with st.chat_message("assistant"):
                    render_proposal(sys_data, area)
                    
                st.info("You can reset the chat in the sidebar to test another scenario.")