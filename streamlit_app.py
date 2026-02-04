import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# ★★★ ここにGASのウェブアプリURLを貼り付け ★★★
GAS_URL = "https://script.google.com/macros/s/AKfycbxRgq73qkQG8oyGmHn4W8MJpk85bfXtlKlYaiu8U09hibHM_ZYtvs5b6y20BjggprL4/exec"

st.set_page_config(page_title="🚬 タバコ管理", page_icon="🚬", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%); }
    .stat-card {
        background: linear-gradient(145deg, #1e1e3f 0%, #2a2a4a 100%);
        border-radius: 20px; padding: 1.5rem; text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1rem;
    }
    .stat-number { font-size: 2.5rem; font-weight: 700; }
    .stat-label { font-size: 0.9rem; color: #94a3b8; }
    .iqos-color { color: #3B82F6; }
    .paper-color { color: #EF4444; }
    .total-color { color: #fbbf24; }
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)

def fetch_data(action):
    try:
        response = requests.get(f"{GAS_URL}?action={action}", timeout=10)
        return response.json()
    except:
        return None

def add_log(tobacco_type):
    try:
        requests.post(GAS_URL, json={"action": "addLog", "type": tobacco_type, "count": 1}, timeout=10)
    except:
        pass

def remove_log(tobacco_type):
    try:
        requests.post(GAS_URL, json={"action": "removeLog", "type": tobacco_type, "count": 1}, timeout=10)
    except:
        pass

def stat_card(value, label, color_class, price=None):
    price_html = f'<div style="color:#94a3b8;font-size:0.9rem;">¥{price:,.1f}</div>' if price else ''
    return f'<div class="stat-card"><div class="stat-label">{label}</div><div class="stat-number {color_class}">{value}</div>{price_html}</div>'

st.markdown('<h1 style="text-align:center;color:white;">🚬 タバコ管理</h1>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📅 今日", "📆 週間", "🗓️ 月間"])

with tab1:
    data = fetch_data("getToday") or {"iqos": 0, "paper": 0, "total": 0, "iqosPrice": 0, "paperPrice": 0, "totalPrice": 0}
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ IQOS", use_container_width=True, type="primary"):
            add_log("iqos")
            st.rerun()
    with col2:
        if st.button("➕ 紙タバコ", use_container_width=True, type="secondary"):
            add_log("paper")
            st.rerun()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(stat_card(f'{data["iqos"]}本', "IQOS", "iqos-color", data["iqosPrice"]), unsafe_allow_html=True)
    with col2:
        st.markdown(stat_card(f'{data["paper"]}本', "紙タバコ", "paper-color", data["paperPrice"]), unsafe_allow_html=True)
    with col3:
        st.markdown(stat_card(f'{data["total"]}本', "合計", "total-color", data["totalPrice"]), unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<p style='color:#6b7280;text-align:center;font-size:0.8rem;'>間違えた時の修正</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➖ IQOS -1", use_container_width=True):
            remove_log("iqos")
            st.rerun()
    with col2:
        if st.button("➖ 紙タバコ -1", use_container_width=True):
            remove_log("paper")
            st.rerun()

with tab2:
    data = fetch_data("getWeek")
    if data and data.get("days"):
        summary = data["summary"]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(stat_card(f'{summary["iqos"]}本', "IQOS (週)", "iqos-color", summary["iqosPrice"]), unsafe_allow_html=True)
        with col2:
            st.markdown(stat_card(f'{summary["paper"]}本', "紙タバコ (週)", "paper-color", summary["paperPrice"]), unsafe_allow_html=True)
        
        df = pd.DataFrame(data["days"])
        fig = go.Figure()
        fig.add_trace(go.Bar(name='IQOS', x=df['date'], y=df['iqos'], marker_color='#3B82F6'))
        fig.add_trace(go.Bar(name='紙タバコ', x=df['date'], y=df['paper'], marker_color='#EF4444'))
        fig.update_layout(barmode='stack', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                          font=dict(color='#ffffff'), margin=dict(l=20,r=20,t=40,b=20), height=300,
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(stat_card(f'¥{summary["totalPrice"]:,.1f}', "週間合計金額", "total-color"), unsafe_allow_html=True)
    else:
        st.info("データがありません。記録を始めましょう！")

with tab3:
    data = fetch_data("getMonth")
    if data and data.get("days"):
        summary = data["summary"]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(stat_card(f'{summary["iqos"]}本', "IQOS (月)", "iqos-color", summary["iqosPrice"]), unsafe_allow_html=True)
        with col2:
            st.markdown(stat_card(f'{summary["paper"]}本', "紙タバコ (月)", "paper-color", summary["paperPrice"]), unsafe_allow_html=True)
        
        df = pd.DataFrame(data["days"])
        fig = go.Figure()
        fig.add_trace(go.Bar(name='IQOS', x=df['date'], y=df['iqos'], marker_color='#3B82F6'))
        fig.add_trace(go.Bar(name='紙タバコ', x=df['date'], y=df['paper'], marker_color='#EF4444'))
        fig.update_layout(barmode='stack', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='#ffffff'), margin=dict(l=20,r=20,t=40,b=20), height=300,
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(stat_card(f'{summary["total"]}本', "月間合計", "total-color"), unsafe_allow_html=True)
        with col2:
            st.markdown(stat_card(f'¥{summary["totalPrice"]:,.1f}', "月間合計金額", "total-color"), unsafe_allow_html=True)
        
        avg_daily = summary["total"] / max(len(data["days"]), 1)
        yearly_estimate = summary["totalPrice"] * 12
        st.markdown(f'<p style="color:#94a3b8;text-align:center;">1日平均: {avg_daily:.1f}本 ｜ 年間推定: ¥{yearly_estimate:,.0f}</p>', unsafe_allow_html=True)
    else:
        st.info("データがありません。記録を始めましょう！")
