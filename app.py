import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import time
import random
from streamlit_echarts import st_echarts
import pandas as pd

# Page config for professional look
st.set_page_config(
    page_title="Advanced Pest Spread Simulator",
    page_icon="🪲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for impressive styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stSlider > div > div > div > div {
        background-color: #FF6B6B;
    }
    </style>
""", unsafe_allow_html=True)

# Title with impressive styling
st.markdown('<h1 class="main-header">🧬 Advanced Pest Spread Modeling<br><small>using Cellular Automata & Environmental Dynamics</small></h1>', unsafe_allow_html=True)

# Sidebar with organized sections
with st.sidebar:
    st.header("🌱 **Simulation Controls**")
    grid_size = st.slider("📐 Grid Size", 10, 50, 25, help="Size of farmland grid")
    
    st.header("🎯 **Initial Infection**")
    col1, col2 = st.columns(2)
    with col1:
        infect_x = st.slider("X Position", 0, grid_size-1, grid_size//2)
    with col2:
        infect_y = st.slider("Y Position", 0, grid_size-1, grid_size//2)
    
    st.header("🌪️ **Environmental Factors**")
    wind_direction = st.selectbox("Wind Direction", ["None", "North", "South", "East", "West"])
    humidity = st.slider("💧 Humidity (0-1)", 0.0, 1.0, 0.3, 0.05)
    crop_density = st.slider("🌾 Crop Density (0-1)", 0.0, 1.0, 0.4, 0.05)
    
    st.header("🔧 **Model Parameters**")
    neighborhood = st.selectbox("Neighborhood", ["Moore", "VonNeumann"])
    base_prob = st.slider("Base Spread Prob", 0.1, 0.4, 0.25, 0.01)
    
    st.header("⏱️ **Simulation**")
    steps = st.slider("Simulation Steps", 1, 50, 15)

# Initialize grid
@st.cache_data
def init_grid(size, x, y):
    grid = np.zeros((size, size))
    grid[x, y] = 1
    return grid

grid = init_grid(grid_size, infect_x, infect_y)

# Improved neighbors function
def get_neighbors(grid, x, y, mode):
    if mode == "Moore":
        directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    else:  # VonNeumann
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
    
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
            neighbors.append((nx, ny))
    return neighbors

# Advanced spread function with wind vector
def spread(grid, wind_dir, hum, crop_dens, base_p, neigh_mode):
    new_grid = grid.copy()
    wind_boost = {"North": (-1,0), "South": (1,0), "East": (0,1), "West": (0,-1), "None": (0,0)}
    wx, wy = wind_boost[wind_dir]
    
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if grid[i,j] == 1:
                neighbors = get_neighbors(grid, i, j, neigh_mode)
                for nx, ny in neighbors:
                    if grid[nx, ny] == 0:
                        prob = base_p + hum * 0.2 + crop_dens * 0.2
                        
                        # Directional wind boost
                        if (nx - i, ny - j) == (wx, wy):
                            prob += 0.15
                        
                        if random.random() < prob:
                            new_grid[nx, ny] = 1
    return new_grid

# Run simulation
simulation_grid = grid.copy()
inf_history = [np.sum(grid)]
for step in range(steps):
    simulation_grid = spread(simulation_grid, wind_direction, humidity, crop_density, base_prob, neighborhood)
    inf_history.append(np.sum(simulation_grid))

# Main dashboard layout
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.metric("🦗 Total Infected Cells", np.sum(simulation_grid), delta=f"{inf_history[-1] - inf_history[0]}")
    
with col2:
    perc = (np.sum(simulation_grid) / (grid_size**2)) * 100
    st.metric("📊 Infestation %", f"{perc:.1f}%", delta=f"+{perc:.1f}%")
    
with col3:
    st.metric("🌪️ Spread Rate", f"{(inf_history[-1]/inf_history[-2]*100-100):+.1f}%", delta_color="inverse")

# Current state heatmap
fig_current = px.imshow(grid, color_continuous_scale='YlOrRd', title="Initial Infection")
fig_current.update_layout(height=400)
st.plotly_chart(fig_current, use_container_width=True)

fig_sim = px.imshow(simulation_grid, color_continuous_scale='YlOrRd', title=f"After {steps} Steps")
fig_sim.update_layout(height=400)
st.plotly_chart(fig_sim, use_container_width=True)

# Infection over time chart
df_history = pd.DataFrame({"Step": range(len(inf_history)), "Infected": inf_history})
fig_line = px.line(df_history, x="Step", y="Infected", title="Infestation Growth Over Time",
                   markers=True, color_discrete_sequence=['#FF6B6B'])
fig_line.update_layout(height=400)
st.plotly_chart(fig_line, use_container_width=True)

# Animation section
st.subheader("🎬 Real-time Animated Simulation")
animate_steps = st.slider("Animation Frames", 1, 30, 12)
if st.button("🚀 Run Animation", type="primary"):
    animation_grid = grid.copy()
    placeholder = st.empty()
    for step in range(animate_steps):
        animation_grid = spread(animation_grid, wind_direction, humidity, crop_density, base_prob, neighborhood)
        fig_anim = px.imshow(animation_grid, color_continuous_scale='YlOrRd',
                           title=f"Step {step+1}/{animate_steps} | Infected: {np.sum(animation_grid)}")
        fig_anim.update_layout(height=500)
        placeholder.plotly_chart(fig_anim, use_container_width=True)
        time.sleep(0.4)

# Prediction section
with st.expander("🔮 High-Risk Prediction (Future Steps)"):
    future_steps = st.slider("Predict Steps Ahead", 5, 50, 20)
    pred_grid = grid.copy()
    for _ in range(future_steps):
        pred_grid = spread(pred_grid, wind_direction, humidity, crop_density, base_prob, neighborhood)
    risk_perc = (np.sum(pred_grid) / (grid_size**2)) * 100
    st.success(f"**Predicted Risk: {risk_perc:.1f}%** infestation")
    
    fig_pred = px.imshow(pred_grid, color_continuous_scale='YlOrRd', title=f"Predicted After {future_steps} Steps")
    st.plotly_chart(fig_pred, use_container_width=True)

# Technical specs footer
with st.expander("📋 Model Specifications"):
    st.info(f"""
    **🧮 Cellular Automata Model Details:**
    - **Neighborhood:** {neighborhood} ({8 if neighborhood=='Moore' else 4} neighbors)
    - **Base Probability:** {base_prob:.2f}
    - **Factors:** Humidity ({humidity:.2f}), Crop Density ({crop_density:.2f})
    - **Wind Vector:** {wind_direction} (+15% boost in direction)
    - **Grid:** {grid_size}×{grid_size} = {grid_size**2} cells
    """)

st.markdown("---")
st.markdown("*Powered by Advanced Cellular Automata | Optimized for Precision Agriculture*")
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef");
        background-size: cover;
        background-position: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)