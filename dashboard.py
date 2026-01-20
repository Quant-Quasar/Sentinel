import streamlit as st
import json
import glob
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="GAP Due Diligence", layout="wide")

st.title("⚖️ GAP: Autonomous Due Diligence Engine")

# --- SIDEBAR ---
st.sidebar.header("System Status")
if os.path.exists("storage/audit_log.jsonl"):
    with open("storage/audit_log.jsonl", "r") as f:
        logs = [json.loads(line) for line in f]
    st.sidebar.success(f"System Online. Events: {len(logs)}")
    st.sidebar.text(f"Last Update: {logs[-1]['timestamp'].split('T')[1][:8]}")

# --- METRICS ---
context_files = glob.glob("storage/contexts/*.json")
context_files.sort()

total_risks = 0
high_risks = 0

# Pre-calculate totals
for fpath in context_files:
    with open(fpath, "r") as f:
        data = json.load(f)
        risks = data['task_state'].get('identified_risks', [])
        total_risks = max(total_risks, len(risks)) # Assuming cumulative
        high_risks = max(high_risks, len([r for r in risks if r['severity'] == 'HIGH']))

col1, col2, col3 = st.columns(3)
col1.metric("Total Risks Identified", total_risks)
col2.metric("High Severity Risks", high_risks)
col3.metric("Active Agents", "2")

# --- SHIFT VIEWER ---
st.divider()
st.header("🧬 Chain of Custody & Findings")

if context_files:
    selected_shift_index = st.slider("Select Shift Cycle", 0, len(context_files)-1, len(context_files)-1)
    
    with open(context_files[selected_shift_index], "r") as f:
        ctx = json.load(f)
    
    # Header Info
    c1, c2, c3 = st.columns([1, 1, 2])
    c1.markdown(f"**Shift:** `{ctx['shift_cycle']}`")
    c2.markdown(f"**Agent:** `{ctx['previous_agent_id']}`")
    c3.markdown(f"**Confidence:** `{ctx['confidence_score']}`")

    st.info(f"**Executive Summary:** {ctx['task_state'].get('summary', 'No summary')}")

    # RISK TABLE
    risks = ctx['task_state'].get('identified_risks', [])
    
    if risks:
        st.subheader("🚨 Risk Register")
        for r in risks:
            with st.expander(f"{r['severity']} | {r['category']}: {r['description'][:50]}..."):
                st.markdown(f"**Description:** {r['description']}")
                st.markdown("**Evidence:**")
                for ev in r['evidence']:
                    st.markdown(f"> *\"{ev['verbatim_quote']}\"*")
                    st.caption(f"Source: {ev['document_name']} (Page {ev['page_number']})")
    else:
        st.success("No Risks Identified in this shift.")

else:
    st.warning("No data found. Run main.py first.")