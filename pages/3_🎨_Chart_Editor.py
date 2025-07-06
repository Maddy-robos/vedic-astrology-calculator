import streamlit as st
import json
import os
import sys
import math
import pandas as pd
from datetime import datetime

# Add project root and CoreLibrary to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'CoreLibrary'))

from chart_visualization import NorthIndianChart

# Set page config
st.set_page_config(
    page_title="Chart Position Editor",
    page_icon="🎨",
    layout="wide"
)

# Title
st.title("🎨 North Indian Chart Position Editor")
st.markdown("""
Visually adjust the positions of houses in your North Indian chart. 
Use the controls on the left to move house positions, and see the changes in real-time on the right.
""")

# Initialize session state
if 'chart_config' not in st.session_state:
    # Load current config
    config_path = os.path.join(project_root, 'Config', 'chart_positions.json')
    try:
        with open(config_path, 'r') as f:
            st.session_state.chart_config = json.load(f)
    except:
        st.session_state.chart_config = {}

if 'selected_house' not in st.session_state:
    st.session_state.selected_house = 1

if 'show_grid' not in st.session_state:
    st.session_state.show_grid = True

# Sample chart data for testing
sample_planets = {
    1: ['Su'],
    2: ['Mo', 'Me'],
    3: ['Ma'],
    4: ['Ju', 'Ve'],
    5: [],
    6: ['Sa'],
    7: ['Ra'],
    8: [],
    9: ['Ke'],
    10: ['Ve'],
    11: [],
    12: ['Me', 'Ju']
}

# Sidebar controls
with st.sidebar:
    st.header("🎛️ Chart Editor Controls")
    
    # House selector
    selected_house = st.selectbox(
        "Select House to Edit",
        options=list(range(1, 13)),
        index=st.session_state.selected_house - 1,
        format_func=lambda x: f"House {x} ({'Square' if x in [1,4,7,10] else 'Triangle'})"
    )
    st.session_state.selected_house = selected_house
    
    st.divider()
    
    # Position controls for selected house
    st.subheader(f"📍 House {selected_house} Position")
    
    # Get current position
    house_str = str(selected_house)
    current_config = st.session_state.chart_config.get('house_centers', {})
    current_pos = current_config.get(house_str, {'x': 0.5, 'y': 0.5})
    
    # X Position slider
    new_x = st.slider(
        "X Position",
        min_value=0.0,
        max_value=2.0,
        value=current_pos['x'],
        step=0.05,
        help="Horizontal position (0.5 = center)"
    )
    
    # Y Position slider
    new_y = st.slider(
        "Y Position", 
        min_value=0.0,
        max_value=2.0,
        value=current_pos['y'],
        step=0.05,
        help="Vertical position (0.5 = center)"
    )
    
    # Area size controls
    st.subheader(f"📏 House {selected_house} Area Size")
    
    current_areas = st.session_state.chart_config.get('house_areas', {})
    current_area = current_areas.get(house_str, {'width': 0.3, 'height': 0.3})
    
    new_width = st.slider(
        "Area Width",
        min_value=0.1,
        max_value=1.0,
        value=current_area['width'],
        step=0.05,
        help="Width of the house area"
    )
    
    new_height = st.slider(
        "Area Height",
        min_value=0.1,
        max_value=1.0,
        value=current_area['height'],
        step=0.05,
        help="Height of the house area"
    )
    
    # Update config if values changed
    if (new_x != current_pos['x'] or new_y != current_pos['y'] or 
        new_width != current_area['width'] or new_height != current_area['height']):
        
        # Update house centers
        if 'house_centers' not in st.session_state.chart_config:
            st.session_state.chart_config['house_centers'] = {}
        
        st.session_state.chart_config['house_centers'][house_str] = {
            'x': new_x,
            'y': new_y,
            'type': current_pos.get('type', 'triangle')
        }
        
        # Update house areas
        if 'house_areas' not in st.session_state.chart_config:
            st.session_state.chart_config['house_areas'] = {}
            
        st.session_state.chart_config['house_areas'][house_str] = {
            'width': new_width,
            'height': new_height,
            'max_cols': current_area.get('max_cols', 2),
            'max_rows': current_area.get('max_rows', 2)
        }
    
    st.divider()
    
    # Display options
    st.subheader("🔧 Display Options")
    
    show_sample_planets = st.checkbox(
        "Show Sample Planets",
        value=True,
        help="Display sample planets for testing positions"
    )
    
    chart_size = st.slider(
        "Chart Size",
        min_value=300,
        max_value=600,
        value=500,
        step=50,
        help="Size of the chart preview"
    )
    
    st.divider()
    
    # Action buttons
    st.subheader("💾 Save/Load")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Config", type="primary"):
            # Save to file
            config_path = os.path.join(project_root, 'Config', 'chart_positions.json')
            try:
                # Update metadata
                st.session_state.chart_config['last_modified'] = datetime.now().isoformat()
                st.session_state.chart_config['version'] = '1.0'
                
                with open(config_path, 'w') as f:
                    json.dump(st.session_state.chart_config, f, indent=2)
                st.success("✅ Configuration saved!")
            except Exception as e:
                st.error(f"❌ Error saving: {str(e)}")
    
    with col2:
        if st.button("🔄 Reset to Default"):
            # Load default config
            chart = NorthIndianChart()
            st.session_state.chart_config = chart._get_default_config()
            st.success("✅ Reset to defaults!")
            st.rerun()
    
    # Quick presets
    st.subheader("⚡ Quick Presets")
    
    if st.button("🎯 Center All Houses"):
        # Center all houses around the middle
        for i in range(1, 13):
            if 'house_centers' not in st.session_state.chart_config:
                st.session_state.chart_config['house_centers'] = {}
            
            angle = (i - 1) * 30  # 30 degrees apart
            radius = 0.6
            x = 1.0 + radius * 0.5 * math.cos(math.radians(angle))
            y = 1.0 + radius * 0.5 * math.sin(math.radians(angle))
            
            st.session_state.chart_config['house_centers'][str(i)] = {
                'x': x,
                'y': y,
                'type': 'square' if i in [1,4,7,10] else 'triangle'
            }
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📊 Position Summary")
    
    # Show current positions for all houses
    config_centers = st.session_state.chart_config.get('house_centers', {})
    
    position_data = []
    for i in range(1, 13):
        house_str = str(i)
        pos = config_centers.get(house_str, {'x': 0.5, 'y': 0.5})
        house_type = "🟩 Square" if i in [1,4,7,10] else "🔺 Triangle"
        
        position_data.append({
            'House': f"{i} {house_type}",
            'X': f"{pos['x']:.2f}",
            'Y': f"{pos['y']:.2f}",
            'Selected': "👈" if i == selected_house else ""
        })
    
    # Display as table
    df = pd.DataFrame(position_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Export current config
    st.subheader("📤 Export Configuration")
    
    config_json = json.dumps(st.session_state.chart_config, indent=2)
    st.download_button(
        label="📥 Download Config JSON",
        data=config_json,
        file_name=f"chart_positions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

with col2:
    st.subheader("🖼️ Live Chart Preview")
    
    try:
        # Create chart with current config
        chart = NorthIndianChart(width=chart_size, height=chart_size)
        
        # Update with current positions
        chart.config = st.session_state.chart_config
        chart._calculate_house_centers()
        
        # Generate chart
        planets_to_show = sample_planets if show_sample_planets else {}
        
        svg_string = chart.generate_chart(
            lagna_sign='Aries',
            house_planets=planets_to_show,
            chart_title=f"Editing House {selected_house}"
        )
        
        # Highlight selected house
        if selected_house in chart.house_centers:
            x, y = chart.house_centers[selected_house]
            area = chart.house_areas[selected_house]
            
            # Add highlight rectangle
            highlight = f'''
            <rect x="{x - area['width']/2}" y="{y - area['height']/2}" 
                  width="{area['width']}" height="{area['height']}" 
                  fill="yellow" opacity="0.3" stroke="red" stroke-width="2"/>
            '''
            
            # Insert highlight before closing </svg>
            svg_string = svg_string.replace('</svg>', highlight + '</svg>')
        
        # Display chart
        st.markdown(svg_string, unsafe_allow_html=True)
        
        # Show coordinates
        if selected_house in chart.house_centers:
            x, y = chart.house_centers[selected_house]
            st.info(f"🎯 House {selected_house} is at pixel position: ({x:.0f}, {y:.0f})")
    
    except Exception as e:
        st.error(f"Error generating chart: {str(e)}")
        st.code(str(e))

# Instructions
st.markdown("---")
with st.expander("📖 How to Use This Editor"):
    st.markdown("""
    ### 🎯 Quick Start
    1. **Select a house** from the dropdown in the sidebar
    2. **Adjust X/Y positions** using the sliders  
    3. **Modify area size** if needed
    4. **See changes instantly** in the preview
    5. **Save your configuration** when satisfied
    
    ### 🏠 House Layout Guide
    - **Houses 1, 4, 7, 10**: Should be squares (center positions)
    - **Other houses**: Should be triangles around the edges
    - **Anti-clockwise order**: 1→2→3→4→5→6→7→8→9→10→11→12
    
    ### 📊 Position Values
    - **X/Y = 1.0**: Center of chart
    - **X/Y = 0.5**: Quarter position
    - **X/Y = 1.5**: Three-quarter position
    - **X/Y = 2.0**: Edge of chart
    
    ### 💡 Tips
    - Use **sample planets** to see how planets will be positioned
    - **Yellow highlight** shows the currently selected house
    - **Save frequently** to preserve your changes
    - Use **Quick Presets** for rapid layout changes
    """)