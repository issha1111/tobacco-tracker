import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# ★★★ ここにGASのウェブアプリURLを貼り付け ★★★
GAS_URL = "https://script.google.com/macros/s/AKfycbxRgq73qkQG8oyGmHn4W8MJpk85bfXtlKlYaiu8U09hibHM_ZYtvs5b6y20BjggprL4/exec"

st.set_page_config(page_title="🚬 タバコ管理", page_icon="🚬", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #0a0a14 0%, #1a1a2e 100%);
        font-family: 'Noto Sans JP', sans-serif;
    }
    
    .main-title {
        text-align: center;
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .date-text {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    
    .stat-card {
        background: linear-gradient(145deg, #1e1e3f 0%, #252545 100%);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 0.5rem;
    }
    
    .stat-number { font-size: 2rem; font-weight: 700; }
    .stat-label { font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.3rem; }
    .stat-price { font-size: 0.85rem; color: #94a3b8; }
    
    .iqos-color { color: #3B82F6; }
    .paper-color { color: #EF4444; }
    .total-color { color: #fbbf24; }
    .white-color { color: #ffffff; }
    
    .dot-container {
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .dot-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        max-width: 320px;
        margin: 0 auto;
    }
    
    .dot {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .dot-iqos { background: #3B82F6; box-shadow: 0 0 12px #3B82F6; }
    .dot-paper { background: #EF4444; box-shadow: 0 0 12px #EF4444; }
    .dot-empty { background: #2a2a3a; }
    
    .legend {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 1rem;
        font-size: 0.8rem;
        color: #94a3b8;
    }
    
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .legend-dot { width: 12px; height: 12px; border-radius: 50%; }
    
    .daily-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .daily-date { color: #94a3b8; font-size: 0.9rem; width: 60px; }
    .daily-dots { display: flex; gap: 4px; flex: 1; justify-content: center; }
    .daily-dot { width: 16px; height: 16px; border-radius: 50%; }
    .daily-dot-iqos { background: #3B82F6; }
    .daily-dot-paper { background: #EF4444; }
    .daily-count { color: white; font-size: 0.9rem; width: 50px; text-align: center; }
    .daily-price { color: #fbbf24; font-size: 0.9rem; width: 70px; text-align: right; }
    
    .monthly-stats {
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .monthly-stats-title { color: white; font-size: 0.9rem; margin-bottom: 1rem; }
    .monthly-stats-grid { display: flex; justify-content: space-around; text-align: center; }
    .monthly-stat-item { flex: 1; }
    .monthly-stat-label { color: #94a3b8; font-size: 0.7rem; margin-bottom: 0.3rem; }
    .monthly-stat-value { color: white; font-size: 1.2rem; font-weight: 700; }
    .monthly-stat-value.highlight { color: #fbbf24; }
    
    .stButton > button { border-radius: 12px; font-weight: 600; padding: 0.5rem 1rem; }
    
    .minus-section {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .minus-label { color: #6b7280; font-size: 0.75rem; text-align: center; margin-bottom: 0.5rem; }
    
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
    .section-title { color: white; font-size: 0.9rem; margin: 1.5rem 0 1rem 0; }
</style>
""", unsafe_allow_html=True)


def fetch_data(action):
    try:
        response = requests.get(f"{GAS_URL}?action={action}", timeout=15)
        return response.json()
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
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


def render_dots(iqos_count, paper_count, max_dots=28):
    dots_html = '<div class="dot-container"><div class="dot-grid">'
    for i in range(max_dots):
        if i < iqos_count:
            dots_html += '<span class="dot dot-iqos"></span>'
        elif i < iqos_count + paper_count:
            dots_html += '<span class="dot dot-paper"></span>'
        else:
            dots_html += '<span class="dot dot-empty"></span>'
    dots_html += '</div>'
    dots_html += '''
        <div class="legend">
            <div class="legend-item"><span class="legend-dot" style="background:#3B82F6;"></span> IQOS</div>
            <div class="legend-item"><span class="legend-dot" style="background:#EF4444;"></span> 紙タバコ</div>
            <div class="legend-item"><span class="legend-dot" style="background:#2a2a3a;"></span> 未使用</div>
        </div>
    '''
    dots_html += '</div>'
    return dots_html


def render_stat_card(value, label, color_class, price=None):
    price_html = f'<div class="stat-price">¥{price:,.1f}</div>' if price is not None else ''
    return f'<div class="stat-card"><div class="stat-label">{label}</div><div class="stat-number {color_class}">{value}</div>{price_html}</div>'


def render_daily_row(date_str, iqos, paper, total_price):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        date_display = dt.strftime('%-m/%-d')
    except:
        date_display = date_str[-5:]
    
    dots_html = ''
    max_display = 10
    iqos_display = min(iqos, max_display)
    paper_display = min(paper, max_display - iqos_display) if iqos < max_display else 0
    
    for _ in range(iqos_display):
        dots_html += '<span class="daily-dot daily-dot-iqos"></span>'
    for _ in range(paper_display):
        dots_html += '<span class="daily-dot daily-dot-paper"></span>'
    
    total = iqos + paper
    return f'<div class="daily-row"><div class="daily-date">{date_display}</div><div class="daily-dots">{dots_html}</div><div class="daily-count">{total}本</div><div class="daily-price">¥{total_price:,.1f}</div></div>'


st.markdown('<div class="main-title">🚬 タバコ管理</div>', unsafe_allow_html=True)
today_str = datetime.now().strftime('%Y年%-m月%-d日（%a）').replace('Mon','月').replace('Tue','火').replace('Wed','水').replace('Thu','木').replace('Fri','金').replace('Sat','土').replace('Sun','日')
st.markdown(f'<div class="date-text">{today_str}</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📅 今日", "📆 週間", "🗓️ 月間"])

with tab1:
    data = fetch_data("getToday")
    if not data:
        data = {"iqos": 0, "paper": 0, "total": 0, "iqosPrice": 0, "paperPrice": 0, "totalPrice": 0}
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ IQOS", use_container_width=True, type="primary", key="btn_add_iqos"):
            add_log("iqos")
            st.rerun()
    with col2:
        if st.button("➕ 紙タバコ", use_container_width=True, type="secondary", key="btn_add_paper"):
            add_log("paper")
            st.rerun()
    
    st.markdown(render_dots(data["iqos"], data["paper"]), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(render_stat_card(f'{data["iqos"]}本', "IQOS", "iqos-color", data["iqosPrice"]), unsafe_allow_html=True)
    with col2:
        st.markdown(render_stat_card(f'{data["paper"]}本', "紙タバコ", "paper-color", data["paperPrice"]), unsafe_allow_html=True)
    with col3:
        st.markdown(render_stat_card(f'{data["total"]}本', "合計", "total-color", data["totalPrice"]), unsafe_allow_html=True)
    
    st.markdown('<div class="minus-section"><div class="minus-label">間違えて押した時はこちらで修正</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➖ IQOS -1", use_container_width=True, key="btn_remove_iqos"):
            remove_log("iqos")
            st.rerun()
    with col2:
        if st.button("➖ 紙タバコ -1", use_container_width=True, key="btn_remove_paper"):
            remove_log("paper")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    data = fetch_data("getWeek")
    if data and data.get("days"):
        summary = data["summary"]
        days = data["days"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(render_stat_card(f'{summary["iqos"]}本', "IQOS (週)", "iqos-color", summary["iqosPrice"]), unsafe_allow_html=True)
        with col2:
            st.markdown(render_stat_card(f'{summary["paper"]}本', "紙タバコ (週)", "paper-color", summary["paperPrice"]), unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📊 週間推移</div>', unsafe_allow_html=True)
        df = pd.DataFrame(days)
        fig_week = go.Figure()
        fig_week.add_trace(go.Bar(name='IQOS', x=df['date'], y=df['iqos'], marker_color='#3B82F6'))
        fig_week.add_trace(go.Bar(name='紙タバコ', x=df['date'], y=df['paper'], marker_color='#EF4444'))
        fig_week.update_layout(barmode='stack', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#ffffff'), margin=dict(l=20,r=20,t=30,b=20), height=250, legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="center",x=0.5), xaxis=dict(gridcolor='rgba(255,255,255,0.1)'), yaxis=dict(gridcolor='rgba(255,255,255,0.1)'))
        st.plotly_chart(fig_week, use_container_width=True, key="chart_week")
        
        st.markdown('<div class="section-title">📋 日別詳細</div>', unsafe_allow_html=True)
        daily_html = '<div style="background:rgba(255,255,255,0.03);border-radius:16px;padding:1rem;">'
        for day in reversed(days):
            daily_html += render_daily_row(day['date'], day['iqos'], day['paper'], day['totalPrice'])
        daily_html += '</div>'
        st.markdown(daily_html, unsafe_allow_html=True)
        
        st.markdown(render_stat_card(f'¥{summary["totalPrice"]:,.1f}', "週間合計金額", "total-color"), unsafe_allow_html=True)
    else:
        st.info("📊 データがありません。記録を始めましょう！")

with tab3:
    data = fetch_data("getMonth")
    if data and data.get("days"):
        summary = data["summary"]
        days = data["days"]
        num_days = len(days) if days else 1
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(render_stat_card(f'{summary["iqos"]}本', "IQOS (月)", "iqos-color", summary["iqosPrice"]), unsafe_allow_html=True)
        with col2:
            st.markdown(render_stat_card(f'{summary["paper"]}本', "紙タバコ (月)", "paper-color", summary["paperPrice"]), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(render_stat_card(f'{summary["total"]}本', "合計 (月)", "white-color"), unsafe_allow_html=True)
        with col2:
            st.markdown(render_stat_card(f'¥{summary["totalPrice"]:,.0f}', "総額 (月)", "total-color"), unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📊 月間推移</div>', unsafe_allow_html=True)
        df = pd.DataFrame(days)
        fig_month = go.Figure()
        fig_month.add_trace(go.Bar(name='IQOS', x=df['date'], y=df['iqos'], marker_color='#3B82F6'))
        fig_month.add_trace(go.Bar(name='紙タバコ', x=df['date'], y=df['paper'], marker_color='#EF4444'))
        fig_month.update_layout(barmode='stack', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#ffffff'), margin=dict(l=20,r=20,t=30,b=20), height=250, legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="center",x=0.5), xaxis=dict(gridcolor='rgba(255,255,255,0.1)',tickangle=45), yaxis=dict(gridcolor='rgba(255,255,255,0.1)'))
        st.plotly_chart(fig_month, use_container_width=True, key="chart_month")
        
        avg_daily = summary["total"] / num_days
        avg_daily_price = summary["totalPrice"] / num_days
        yearly_estimate = summary["totalPrice"] * 12
        
        st.markdown(f'''
            <div class="monthly-stats">
                <div class="monthly-stats-title">📈 月間統計</div>
                <div class="monthly-stats-grid">
                    <div class="monthly-stat-item">
                        <div class="monthly-stat-label">1日平均</div>
                        <div class="monthly-stat-value">{avg_daily:.1f}本</div>
                    </div>
                    <div class="monthly-stat-item">
                        <div class="monthly-stat-label">1日平均金額</div>
                        <div class="monthly-stat-value">¥{avg_daily_price:,.0f}</div>
                    </div>
                    <div class="monthly-stat-item">
                        <div class="monthly-stat-label">年間推定</div>
                        <div class="monthly-stat-value highlight">¥{yearly_estimate:,.0f}</div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.info("📊 データがありません。記録を始めましょう！")
