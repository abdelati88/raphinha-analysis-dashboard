import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch
import os

# ============== 1. Page Configuration ==============
st.set_page_config(
    page_title="Raphinha vs Real Madrid",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme CSS
st.markdown("""
<style>
    .stApp { background-color: #121212; color: white; }
    section[data-testid="stSidebar"] { background-color: #1a1a1a; border-right: 1px solid #333; }
    div[data-testid="stMetric"] {
        background-color: #222;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] { color: #888; font-size: 0.8rem; }
    div[data-testid="stMetricValue"] { color: #00d4ff; font-size: 1.4rem; font-weight: bold; }
    h1, h2, h3 { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ============== 2. Logic Functions ==============

def calculate_progressive(row):
    if row.get('outcome', False) == False:
        return False

    start_x = row.get('x', 0)
    end_x = row.get('end_x', 0)
    end_y = row.get('end_y', 0)
    
    dist_gain = end_x - start_x
    box_x_line = 83
    in_box_y = (21 <= end_y <= 79)
    
    ends_in_box = (end_x >= box_x_line) and in_box_y
    starts_outside_box = (start_x < box_x_line)
    
    if ends_in_box and starts_outside_box and (dist_gain > 0): return True
    if start_x <= 50: return dist_gain >= 15
    else: return dist_gain >= 10

# ============== 3. Load Data ==============
@st.cache_data
def load_data():
    try:
        with open('raphina_stats.json', 'r', encoding='utf-8') as f: stats = json.load(f)
        with open('raphinha_data.json', 'r', encoding='utf-8') as f: events = json.load(f)
        with open('raphinha_heat.json', 'r', encoding='utf-8') as f: 
            heat_raw = json.load(f)
            heat = heat_raw.get("heatmap", heat_raw)
        with open('shot.json', 'r', encoding='utf-8') as f: 
            shot_raw = json.load(f)
            shots = shot_raw.get("shotmap", shot_raw)
        return stats, events, heat, shots
    except Exception:
        return None, None, None, None

stats_json, events_json, heat_list, shots_list = load_data()

# ============== 4. Data Processing (Fixed Order) ==============
if stats_json:
    # 4.1 General Stats
    stats = stats_json.get('statistics', {})
    player_info = stats_json.get('player', {})
    player_name = player_info.get('name', 'Player')
    
    # 4.2 Initialize DataFrames (Empty by default to avoid NameError)
    df_passes = pd.DataFrame()
    df_shots = pd.DataFrame()
    df_dribbles = pd.DataFrame()
    df_def = pd.DataFrame()
    df_heat = pd.DataFrame()

    # 4.3 Process Passes
    if 'passes' in events_json:
        df_passes = pd.DataFrame(events_json['passes'])
        if not df_passes.empty:
            df_passes['x'] = df_passes['playerCoordinates'].apply(lambda i: i.get('x'))
            df_passes['y'] = df_passes['playerCoordinates'].apply(lambda i: i.get('y'))
            df_passes['end_x'] = df_passes['passEndCoordinates'].apply(lambda i: i.get('x'))
            df_passes['end_y'] = df_passes['passEndCoordinates'].apply(lambda i: i.get('y'))
            
            if 'outcome' not in df_passes.columns: df_passes['outcome'] = False
            else: df_passes['outcome'] = df_passes['outcome'].fillna(False)
            
            df_passes['is_progressive'] = df_passes.apply(calculate_progressive, axis=1)

    # 4.4 Process Shots
    if shots_list:
        df_shots = pd.DataFrame(shots_list)
    if not df_shots.empty:
        df_shots['x'] = df_shots['playerCoordinates'].apply(lambda i: 100 - i.get('x')) 
        
        df_shots['y'] = df_shots['playerCoordinates'].apply(lambda i: 100 - i.get('y'))
    # 4.5 Process Dribbles (Fixing the Error Source)
    if 'dribbles' in events_json:
        df_dribbles = pd.DataFrame(events_json['dribbles'])
        if not df_dribbles.empty:
            df_dribbles['x'] = df_dribbles['playerCoordinates'].apply(lambda i: i.get('x'))
            df_dribbles['y'] = df_dribbles['playerCoordinates'].apply(lambda i: i.get('y'))
            if 'outcome' not in df_dribbles.columns: df_dribbles['outcome'] = False
            else: df_dribbles['outcome'] = df_dribbles['outcome'].fillna(False)

    # 4.6 Process Defensive & Heatmap
    if 'defensive' in events_json:
        df_def = pd.DataFrame(events_json['defensive'])
        if not df_def.empty:
            df_def['x'] = df_def['playerCoordinates'].apply(lambda i: i.get('x'))
            df_def['y'] = df_def['playerCoordinates'].apply(lambda i: i.get('y'))
            
    if heat_list:
        df_heat = pd.DataFrame(heat_list)

    # ============== 5. Sidebar Controls ==============
    st.sidebar.title("📊 Raphinha Stats & Highlights")
    st.sidebar.markdown("---")
    
    viz_type = st.sidebar.radio(
        "Select Visualization:",
        ["Heatmap", "Pass Map", "Shot Map", "Dribble Map", "Defensive Map"]
    )
    st.sidebar.markdown("---")
    
    # Visualization specific filters
    filter_choice = "All"
    
    if viz_type == "Pass Map":
        st.sidebar.subheader("Pass Filters")
        filter_choice = st.sidebar.radio("Filter By:", ["All", "Successful", "Missed", "Crosses", "Key Passes", "Progressive"])
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Legend:**\n🟨 Key Pass\n🟦 Cross\n🟣 Progressive\n🟩 Successful\n🟥 Missed")
        
    elif viz_type == "Shot Map":
        st.sidebar.subheader("Shot Filters")
        if not df_shots.empty:
            shot_types = ["All"] + list(df_shots['shotType'].unique())
            filter_choice = st.sidebar.selectbox("Result:", shot_types)
        st.sidebar.markdown("---")
        st.sidebar.success("⭐ Goal")
        st.sidebar.info("🔵 Saved")
        st.sidebar.error("❌ Miss")
        
    elif viz_type == "Dribble Map":
        st.sidebar.success("✅ Successful")
        st.sidebar.error("❌ Failed") 

    
    
    # 1. Calculate values
    total_passes = stats.get('totalPass', 0)
    acc_passes = stats.get('accuratePass', 0)
    pass_acc_pct = round((acc_passes / total_passes * 100), 1) if total_passes > 0 else 0
    
    total_dribbles = len(df_dribbles) if not df_dribbles.empty else 0
    succ_dribbles = len(df_dribbles[df_dribbles['outcome'] == True]) if not df_dribbles.empty else 0
    
    possession_lost = stats.get('possessionLostCtrl', 0)
    prog_count = len(df_passes[df_passes['is_progressive']]) if not df_passes.empty else 0
    
    goals_count = len(df_shots[df_shots['shotType'] == 'goal']) if not df_shots.empty else 0
    total_shots = len(df_shots) if not df_shots.empty else 0
    key_passes = stats.get('keyPass', 0)
    assists = stats.get('goalAssist', 0)

    # 2. Define Metrics Lists
    row1_metrics = []
    row2_metrics = []

    row1_metrics.append({"label": "Rating", "value": stats.get('rating', '-')})
    
    if total_shots > 0 or goals_count > 0:
        row1_metrics.append({"label": "Goals / Shots", "value": f"{goals_count} / {total_shots}"})
        
    if key_passes > 0 or assists > 0:
        row1_metrics.append({"label": "Key Pass / Assist", "value": f"{key_passes} / {assists}"})

    if total_passes > 0:
        row1_metrics.append({"label": "Total Passes", "value": total_passes})

    # --- Row 2: Technical Stats (Accuracy, Dribbles, Possession, Progression) ---
    row2_metrics.append({"label": "Accurate Passes", "value": f"{acc_passes} ({pass_acc_pct}%)"})

    if total_dribbles > 0:
        row2_metrics.append({"label": "Dribbles", "value": f"{succ_dribbles} / {total_dribbles}"})

    if possession_lost > 0:
        row2_metrics.append({"label": "Possession Lost", "value": possession_lost})
    
    if prog_count > 0:
        row2_metrics.append({"label": "Progression pass", "value": prog_count})

    # 3. Render Row 1
    if row1_metrics:
        cols1 = st.columns(len(row1_metrics))
        for col, metric in zip(cols1, row1_metrics):
            col.metric(metric["label"], metric["value"])
    
    # 4. Render Row 2 (if exists)
    if row2_metrics:
        st.markdown("") # Small spacer
        cols2 = st.columns(len(row2_metrics))
        for col, metric in zip(cols2, row2_metrics):
            col.metric(metric["label"], metric["value"])
    
    st.markdown("---")
    # ============== 7. Visualizations ==============
    
    # --- Pass Map ---
    if viz_type == "Pass Map":
        fig, ax = plt.subplots(figsize=(8, 5.5), constrained_layout=True)
        fig.set_facecolor('#121212')
        pitch = Pitch(pitch_type='opta', pitch_color='#1e1e1e', line_color='#555', linewidth=1)
        pitch.draw(ax=ax)
        
        if not df_passes.empty:
            viz = df_passes.copy()
            # Filters
            if filter_choice == "Successful": viz = viz[viz['outcome'] == True]
            elif filter_choice == "Missed": viz = viz[viz['outcome'] == False]
            elif filter_choice == "Key Passes": viz = viz[viz['keypass'] == True]
            elif filter_choice == "Progressive": viz = viz[viz['is_progressive'] == True]
            elif filter_choice == "Crosses":
                if 'eventActionType' in viz.columns: viz = viz[viz['eventActionType'] == 'cross']

            # Plotting logic
            if filter_choice == "Crosses":
                succ_cross = viz[viz['outcome'] == True]
                pitch.arrows(succ_cross.x, succ_cross.y, succ_cross.end_x, succ_cross.end_y, width=3, color='#00BFFF', alpha=0.9, ax=ax, label='Successful Cross')
                miss_cross = viz[viz['outcome'] == False]
                pitch.arrows(miss_cross.x, miss_cross.y, miss_cross.end_x, miss_cross.end_y, width=2, color='#F44336', alpha=0.6, ax=ax, label='Missed Cross')
                ax.legend(facecolor='#1e1e1e', edgecolor='white', labelcolor='white', loc='upper left')

            elif filter_choice == "All":
                normal = viz[(viz['keypass'] == False) & (viz['is_progressive'] == False) & (viz['outcome'] == True) & (viz['eventActionType'] != 'cross')]
                pitch.arrows(normal.x, normal.y, normal.end_x, normal.end_y, width=2, color='#4CAF50', alpha=0.2, ax=ax)
                missed = viz[viz['outcome'] == False]
                pitch.arrows(missed.x, missed.y, missed.end_x, missed.end_y, width=2, color='#F44336', alpha=0.4, ax=ax)
                crosses = viz[(viz['eventActionType'] == 'cross') & (viz['outcome'] == True) & (viz['keypass'] == False)]
                pitch.arrows(crosses.x, crosses.y, crosses.end_x, crosses.end_y, width=3, color='#00BFFF', alpha=0.8, ax=ax)
                prog = viz[(viz['is_progressive'] == True) & (viz['keypass'] == False)]
                pitch.arrows(prog.x, prog.y, prog.end_x, prog.end_y, width=3, color='#9C27B0', alpha=0.9, ax=ax)
                kp = viz[viz['keypass'] == True]
                pitch.arrows(kp.x, kp.y, kp.end_x, kp.end_y, width=4, color='#FFD700', zorder=3, ax=ax)
            else:
                c_map = {"Successful": "#4CAF50", "Missed": "#F44336", "Key Passes": "#FFD700", "Progressive": "#9C27B0"}
                pitch.arrows(viz.x, viz.y, viz.end_x, viz.end_y, width=3, color=c_map.get(filter_choice, "white"), ax=ax)
        st.pyplot(fig, use_container_width=True)

    # --- Shot Map ---
    elif viz_type == "Shot Map":
        fig, ax = plt.subplots(figsize=(6, 8), constrained_layout=True)
        fig.set_facecolor('#121212')
        pitch = VerticalPitch(pitch_type='opta', pitch_color='#1e1e1e', line_color='#555', half=True)
        pitch.draw(ax=ax)
        
        if not df_shots.empty:
            s_viz = df_shots.copy()
            if filter_choice != "All": s_viz = s_viz[s_viz['shotType'] == filter_choice]
            
            g = s_viz[s_viz['shotType'] == 'goal']
            pitch.scatter(g.x, g.y, s=400, marker='*', c='#00ff00', edgecolors='white', ax=ax)
            s = s_viz[s_viz['shotType'].isin(['save', 'saved'])]
            pitch.scatter(s.x, s.y, s=200, marker='o', c='#38b6ff', edgecolors='white', ax=ax)
            m = s_viz[s_viz['shotType'].isin(['miss', 'block', 'blocked'])]
            pitch.scatter(m.x, m.y, s=200, marker='x', c='#ff3838', linewidth=2, ax=ax)
        st.pyplot(fig, use_container_width=True)

    # --- Heatmap ---
    elif viz_type == "Heatmap":
        fig, ax = plt.subplots(figsize=(8, 5.5), constrained_layout=True)
        fig.set_facecolor('#121212')
        pitch = Pitch(pitch_type='opta', pitch_color='#1e1e1e', line_color='#555')
        pitch.draw(ax=ax)
        if not df_heat.empty:
            pitch.kdeplot(df_heat['x'], df_heat['y'], ax=ax, fill=True, levels=100, cmap='hot', alpha=0.8)
        st.pyplot(fig, use_container_width=True)

    # --- Dribble Map ---
    elif viz_type == "Dribble Map":
        fig, ax = plt.subplots(figsize=(8, 5.5), constrained_layout=True)
        fig.set_facecolor('#121212')
        pitch = Pitch(pitch_type='opta', pitch_color='#1e1e1e', line_color='#555')
        pitch.draw(ax=ax)
        
        if not df_dribbles.empty:
            succ = df_dribbles[df_dribbles['outcome'] == True]
            pitch.scatter(succ.x, succ.y, s=300, marker='^', c='#00ff00', edgecolors='white', ax=ax, zorder=3)
            fail = df_dribbles[df_dribbles['outcome'] == False]
            pitch.scatter(fail.x, fail.y, s=300, marker='v', c='#ff3838', edgecolors='white', ax=ax, zorder=3)
            ax.set_title("Dribbling Map", color='white', fontsize=15)
        else:
            st.info("No dribbles recorded.")
        st.pyplot(fig, use_container_width=True)

    # --- Defensive Map ---
    elif viz_type == "Defensive Map":
        fig, ax = plt.subplots(figsize=(8, 5.5), constrained_layout=True)
        fig.set_facecolor('#121212')
        pitch = Pitch(pitch_type='opta', pitch_color='#1e1e1e', line_color='#555')
        pitch.draw(ax=ax)
        
        if not df_def.empty:
            actions_map = {
                'tackle': {'color': '#FF9800', 'marker': 'D', 'label': 'Tackle'},
                'clearance': {'color': '#F44336', 'marker': 'X', 'label': 'Clearance'},
                'ball-recovery': {'color': '#03A9F4', 'marker': 'o', 'label': 'Recovery'},
                'interception': {'color': '#9C27B0', 'marker': 's', 'label': 'Interception'},
                'block': {'color': '#607D8B', 'marker': '^', 'label': 'Block'}
            }
            legend_elements = []
            for action_type in df_def['eventActionType'].unique():
                clean_type = str(action_type).lower().strip()
                config = actions_map.get(clean_type, {'color': 'white', 'marker': 'h', 'label': clean_type.title()})
                subset = df_def[df_def['eventActionType'] == action_type]
                pitch.scatter(subset.x, subset.y, s=250, marker=config['marker'], c=config['color'], edgecolors='white', linewidth=1.5, alpha=0.9, ax=ax, zorder=3)
                
                from matplotlib.lines import Line2D
                legend_elements.append(Line2D([0], [0], marker=config['marker'], color='w', label=config['label'], markerfacecolor=config['color'], markersize=10, markeredgecolor='white'))
            
            ax.legend(handles=legend_elements, facecolor='#121212', edgecolor='#555', labelcolor='white', loc='upper left', framealpha=0.8, fontsize=10)
            ax.set_title("Defensive Actions", color='white', fontsize=15)
        st.pyplot(fig, use_container_width=True)

    # ============== 8. Video Section ==============
    st.markdown("---")
    st.subheader("🎥 Match Highlights")
    
    with st.expander("▶️ Watch Video", expanded=True):
        video_path = "raphinha.mp4" 
        
        if os.path.exists(video_path):
            st.video(video_path)
        else:
            st.error(f"⚠️ Video not found: {video_path}")    
    
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📬 Connect with Me")
    
    github_url = "https://github.com/abdelati88"
    linkedin_url = "https://www.linkedin.com/in/abdelati88"
    
    st.sidebar.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <a href="{linkedin_url}" target="_blank">
                <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" width="130" />
            </a>
            <a href="{github_url}" target="_blank">
                <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" width="120" />
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    

    st.sidebar.caption("© 2026 abdelati88")



