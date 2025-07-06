import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import json
from io import StringIO

# Add project root and CoreLibrary to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'CoreLibrary'))

from chart import Chart
from calculations_helper import CalculationsHelper
from chart_visualization import NorthIndianChart

def format_planetary_data(grahas, house_planets):
    """
    Format planetary data for consistent display in tables.
    
    Args:
        grahas: Dictionary of planetary positions
        house_planets: Dictionary mapping house numbers to planets
        
    Returns:
        List of dictionaries with formatted planetary data
    """
    planetary_data = []
    
    for graha_name, graha_data in grahas.items():
        # Calculate house placement
        house_num = None
        for house, planets in house_planets.items():
            if graha_name in planets:
                house_num = house
                break
        
        # Get nakshatra info
        nakshatra_info = graha_data.get('nakshatra', {})
        if isinstance(nakshatra_info, dict):
            nakshatra_name = nakshatra_info.get('name', 'Unknown')
            nakshatra_pada = nakshatra_info.get('pada', 'Unknown')
            nakshatra_display = f"{nakshatra_name} ({nakshatra_pada})"
        else:
            nakshatra_display = str(nakshatra_info)
        
        # Calculate degrees within sign
        degrees_in_sign = graha_data['longitude'] % 30
        
        # Get dignity (placeholder for now)
        dignity = "Neutral"  # This would need actual dignity calculation
        
        planetary_data.append({
            'Planet': graha_name,
            'Sign': graha_data['rasi'],
            'Degrees': f"{degrees_in_sign:.2f}°",
            'Nakshatra': nakshatra_display,
            'House': house_num if house_num else '-',
            'Dignity': dignity,
            'Retrograde': '↺' if graha_data.get('is_retrograde', False) else '-'
        })
    
    return planetary_data

# Set page config
st.set_page_config(
    page_title="Research Interface - Vedic Astrology",
    page_icon="🔬",
    layout="wide"
)

# Title and description
st.title("🔬 Vedic Astrology Research Interface")
st.markdown("""
Upload a CSV file with birth data to generate and analyze multiple charts at once.
Perfect for research studies, pattern analysis, and batch processing.
""")

# Initialize session state
if 'processed_charts' not in st.session_state:
    st.session_state.processed_charts = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'charts_per_page' not in st.session_state:
    st.session_state.charts_per_page = 10
if 'show_chart_details' not in st.session_state:
    st.session_state.show_chart_details = False
if 'selected_chart_index' not in st.session_state:
    st.session_state.selected_chart_index = None

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    
    # Divisional chart selection
    chart_type = st.selectbox(
        "Select Chart Type",
        options=[
            "D1 - Rasi Chart", 
            "D2 - Hora Chart", 
            "D3 - Drekkana Chart",
            "D9 - Navamsa Chart",
            "D10 - Dasamsa Chart"
        ],
        help="Choose which divisional chart to display"
    )
    
    # Display settings
    st.subheader("Display Options")
    charts_per_row = st.slider("Charts per row", 1, 3, 2)
    st.session_state.charts_per_page = st.selectbox(
        "Charts per page",
        options=[10, 20, 50],
        index=0
    )
    
    # Calculation settings
    st.subheader("Calculation Settings")
    ayanamsa = st.selectbox(
        "Ayanamsa",
        options=["Lahiri", "Raman", "Krishnamurti"],
        index=0
    )
    house_system = st.selectbox(
        "House System",
        options=["Placidus", "Equal", "Whole Sign"],
        index=0
    )

# Main content area
tab1, tab2, tab3 = st.tabs(["📤 Upload Data", "📊 View Charts", "📈 Analysis"])

with tab1:
    st.header("Upload CSV File")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="CSV should contain: name, date, time, latitude, longitude, timezone"
    )
    
    # Sample CSV template
    with st.expander("📋 CSV Format Example"):
        st.markdown("""
        Your CSV file should have the following columns:
        - **name**: Person's name or ID
        - **date**: Birth date (YYYY-MM-DD)
        - **time**: Birth time (HH:MM:SS)
        - **latitude**: Latitude in decimal degrees
        - **longitude**: Longitude in decimal degrees
        - **timezone**: IANA timezone (e.g., Asia/Kolkata) or UTC offset (e.g., +05:30)
        
        Optional columns:
        - **gender**: M/F
        - **place_name**: Birth place name
        - **notes**: Any additional notes
        """)
        
        # Download sample CSV
        sample_data = """name,date,time,latitude,longitude,timezone,place_name
John Doe,1990-05-15,14:30:00,28.6139,77.2090,Asia/Kolkata,New Delhi
Jane Smith,1985-08-22,09:15:00,19.0760,72.8777,Asia/Kolkata,Mumbai
Robert Johnson,1992-12-10,23:45:00,13.0827,80.2707,Asia/Kolkata,Chennai"""
        
        st.download_button(
            label="Download Sample CSV",
            data=sample_data,
            file_name="sample_birth_data.csv",
            mime="text/csv"
        )
    
    # Process uploaded file
    if uploaded_file is not None:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            
            # Display preview
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Validate columns
            required_columns = ['name', 'date', 'time', 'latitude', 'longitude', 'timezone']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
            else:
                st.success(f"✅ Found {len(df)} records with all required columns")
                
                # Process button
                if st.button("🚀 Process Charts", type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    processed_charts = []
                    errors = []
                    
                    for idx, row in df.iterrows():
                        try:
                            # Update progress
                            progress = (idx + 1) / len(df)
                            progress_bar.progress(progress)
                            status_text.text(f"Processing {row['name']} ({idx + 1}/{len(df)})")
                            
                            # Parse datetime
                            birth_date = datetime.strptime(row['date'], '%Y-%m-%d')
                            birth_time = datetime.strptime(row['time'], '%H:%M:%S').time()
                            birth_datetime = datetime.combine(birth_date.date(), birth_time)
                            
                            # Create chart
                            chart = Chart(
                                birth_datetime=birth_datetime,
                                latitude=float(row['latitude']),
                                longitude=float(row['longitude']),
                                timezone_str=row['timezone'],
                                ayanamsa=ayanamsa,
                                house_system=house_system
                            )
                            
                            # Store processed chart
                            chart_data = {
                                'name': row['name'],
                                'chart': chart,
                                'birth_datetime': birth_datetime,
                                'place': row.get('place_name', 'Unknown'),
                                'chart_data': chart.get_chart_summary()
                            }
                            processed_charts.append(chart_data)
                            
                        except Exception as e:
                            errors.append({
                                'row': idx + 1,
                                'name': row.get('name', 'Unknown'),
                                'error': str(e)
                            })
                    
                    # Clear progress
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Store in session state
                    st.session_state.processed_charts = processed_charts
                    
                    # Show results
                    st.success(f"✅ Successfully processed {len(processed_charts)} charts")
                    
                    if errors:
                        with st.expander(f"⚠️ {len(errors)} errors occurred"):
                            for error in errors:
                                st.error(f"Row {error['row']} ({error['name']}): {error['error']}")
                    
                    # Auto-switch to View Charts tab
                    st.info("👉 Switch to the 'View Charts' tab to see the results")
                    
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")

with tab2:
    st.header("View Charts")
    
    if not st.session_state.processed_charts:
        st.info("📤 Please upload and process a CSV file in the 'Upload Data' tab first.")
    else:
        # Pagination
        total_charts = len(st.session_state.processed_charts)
        total_pages = (total_charts - 1) // st.session_state.charts_per_page + 1
        
        # Page navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("◀ Previous", disabled=st.session_state.current_page == 1):
                st.session_state.current_page -= 1
        with col2:
            st.markdown(f"<h4 style='text-align: center'>Page {st.session_state.current_page} of {total_pages}</h4>", 
                       unsafe_allow_html=True)
        with col3:
            if st.button("Next ▶", disabled=st.session_state.current_page == total_pages):
                st.session_state.current_page += 1
        
        # Calculate page indices
        start_idx = (st.session_state.current_page - 1) * st.session_state.charts_per_page
        end_idx = min(start_idx + st.session_state.charts_per_page, total_charts)
        
        # Display charts in grid
        charts_to_display = st.session_state.processed_charts[start_idx:end_idx]
        
        # Create columns for grid layout
        for i in range(0, len(charts_to_display), charts_per_row):
            cols = st.columns(charts_per_row)
            
            for j in range(charts_per_row):
                if i + j < len(charts_to_display):
                    chart_info = charts_to_display[i + j]
                    
                    with cols[j]:
                        # Chart container
                        with st.container():
                            st.markdown(f"### {chart_info['name']}")
                            st.caption(f"{chart_info['birth_datetime'].strftime('%Y-%m-%d %H:%M')} | {chart_info['place']}")
                            
                            # Get chart data based on selection
                            ascendant = chart_info['chart'].get_ascendant()
                            ascendant_deg = ascendant['longitude']
                            grahas = chart_info['chart'].get_graha_positions()
                            
                            if "D1" in chart_type:
                                # D1 Chart - Display North Indian chart
                                summary = chart_info['chart_data']
                                lagna_sign = summary['ascendant']['rasi']
                                
                                # Get house placements
                                bhava_analysis = chart_info['chart'].get_bhava_analysis()
                                graha_placements = bhava_analysis.get('graha_placements', {})
                                
                                # Convert to house_planets format
                                house_planets = {}
                                for house_str, planets in graha_placements.items():
                                    house_planets[int(house_str)] = planets
                                
                                # Display info
                                info_text = f"**Lagna**: {lagna_sign} {summary['ascendant']['degrees']}"
                                
                            else:
                                # Divisional charts (D2, D3, D9, D10)
                                if "D2" in chart_type:
                                    div_type = "D2"
                                    div_name = "Hora"
                                elif "D3" in chart_type:
                                    div_type = "D3"
                                    div_name = "Drekkana"
                                elif "D9" in chart_type:
                                    div_type = "D9"
                                    div_name = "Navamsa"
                                elif "D10" in chart_type:
                                    div_type = "D10"
                                    div_name = "Dasamsa"
                                
                                # Get divisional house placements using unified method
                                house_planets = CalculationsHelper.get_divisional_house_placements(
                                    div_type, ascendant_deg, grahas
                                )
                                
                                # Get divisional ascendant
                                if div_type == "D2":
                                    lagna_sign = CalculationsHelper.get_hora_rasi(ascendant_deg)
                                elif div_type == "D3":
                                    lagna_sign = CalculationsHelper.get_drekkana_rasi(ascendant_deg)
                                elif div_type == "D9":
                                    lagna_sign = CalculationsHelper.get_navamsa_rasi(ascendant_deg)
                                elif div_type == "D10":
                                    lagna_sign = CalculationsHelper.get_dasamsa_rasi(ascendant_deg)
                                
                                # Display info
                                info_text = f"**{div_name} Lagna**: {lagna_sign}"
                            
                            # Create and display North Indian chart
                            ni_chart = NorthIndianChart(width=350, height=350)
                            svg_string = ni_chart.generate_chart(
                                lagna_sign=lagna_sign,
                                house_planets=house_planets,
                                chart_title=None  # No title for compact display
                            )
                            
                            # Display SVG chart
                            st.markdown(svg_string, unsafe_allow_html=True)
                            
                            # Show chart info
                            st.markdown(info_text)
                            
                            # Add View Details button
                            if st.button(f"🔍 View Details", key=f"details_{i}_{j}"):
                                st.session_state.show_chart_details = True
                                st.session_state.selected_chart_index = start_idx + i + j
                                st.rerun()
                            
                            st.divider()

# Detailed Chart View Modal
if st.session_state.show_chart_details and st.session_state.selected_chart_index is not None:
    selected_chart = st.session_state.processed_charts[st.session_state.selected_chart_index]
    
    st.markdown("---")
    st.markdown("## 🔍 Detailed Chart View")
    
    # Header with chart info and close button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### {selected_chart['name']}")
        st.caption(f"📅 {selected_chart['birth_datetime'].strftime('%B %d, %Y at %H:%M')} | 📍 {selected_chart['place']}")
    
    with col3:
        if st.button("❌ Close Details"):
            st.session_state.show_chart_details = False
            st.session_state.selected_chart_index = None
            st.rerun()
    
    # Chart and planetary details in columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 📊 Chart")
        
        # Display the chart
        ascendant = selected_chart['chart'].get_ascendant()
        ascendant_deg = ascendant['longitude']
        grahas = selected_chart['chart'].get_graha_positions()
        
        if "D1" in chart_type:
            summary = selected_chart['chart_data']
            lagna_sign = summary['ascendant']['rasi']
            bhava_analysis = selected_chart['chart'].get_bhava_analysis()
            graha_placements = bhava_analysis.get('graha_placements', {})
            house_planets = {}
            for house_str, planets in graha_placements.items():
                house_planets[int(house_str)] = planets
        else:
            # Divisional charts
            if "D2" in chart_type:
                div_type = "D2"
                lagna_sign = CalculationsHelper.get_hora_rasi(ascendant_deg)
            elif "D3" in chart_type:
                div_type = "D3"
                lagna_sign = CalculationsHelper.get_drekkana_rasi(ascendant_deg)
            elif "D9" in chart_type:
                div_type = "D9"
                lagna_sign = CalculationsHelper.get_navamsa_rasi(ascendant_deg)
            elif "D10" in chart_type:
                div_type = "D10"
                lagna_sign = CalculationsHelper.get_dasamsa_rasi(ascendant_deg)
            
            house_planets = CalculationsHelper.get_divisional_house_placements(
                div_type, ascendant_deg, grahas
            )
        
        # Generate larger chart for details view
        ni_chart = NorthIndianChart(width=300, height=300)
        svg_string = ni_chart.generate_chart(
            lagna_sign=lagna_sign,
            house_planets=house_planets,
            chart_title=None
        )
        st.markdown(svg_string, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🪐 Planetary Positions")
        
        # Use unified formatting function
        planetary_data = format_planetary_data(grahas, house_planets)
        
        # Display as sortable table
        df = pd.DataFrame(planetary_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Planet': st.column_config.TextColumn('🪐 Planet', width='medium'),
                'Sign': st.column_config.TextColumn('♈ Sign', width='medium'),
                'Degrees': st.column_config.TextColumn('📐 Degrees', width='small'),
                'Nakshatra': st.column_config.TextColumn('⭐ Nakshatra', width='large'),
                'House': st.column_config.TextColumn('🏠 House', width='small'),
                'Dignity': st.column_config.TextColumn('👑 Dignity', width='medium'),
                'Retrograde': st.column_config.TextColumn('↺ Retro', width='small')
            }
        )
        
        # Navigation buttons for browsing charts
        st.markdown("#### 📚 Navigate Charts")
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        
        with nav_col1:
            if st.button("⬅️ Previous Chart", disabled=st.session_state.selected_chart_index == 0):
                st.session_state.selected_chart_index -= 1
                st.rerun()
        
        with nav_col2:
            st.markdown(f"**{st.session_state.selected_chart_index + 1}** of **{len(st.session_state.processed_charts)}**")
        
        with nav_col3:
            if st.button("Next Chart ➡️", disabled=st.session_state.selected_chart_index == len(st.session_state.processed_charts) - 1):
                st.session_state.selected_chart_index += 1
                st.rerun()
    
    st.markdown("---")

with tab3:
    st.header("Analysis Tools")
    
    if not st.session_state.processed_charts:
        st.info("📤 Please upload and process a CSV file first.")
    else:
        st.subheader(f"Dataset: {len(st.session_state.processed_charts)} charts")
        
        # Analysis options
        analysis_type = st.selectbox(
            "Select Analysis Type",
            options=[
                "Planetary Distribution",
                "Sign Occupancy",
                "House Analysis",
                "Yoga Frequency"
            ]
        )
        
        if analysis_type == "Planetary Distribution":
            st.markdown("### Planetary Distribution Analysis")
            
            # Collect planet positions
            planet_signs = {planet: [] for planet in CalculationsHelper.GRAHAS}
            
            for chart_info in st.session_state.processed_charts:
                grahas = chart_info['chart'].get_graha_positions()
                for graha, data in grahas.items():
                    if graha in planet_signs:
                        planet_signs[graha].append(data['rasi'])
            
            # Display distribution
            selected_planet = st.selectbox("Select Planet", options=CalculationsHelper.GRAHAS)
            
            if selected_planet in planet_signs:
                sign_counts = pd.Series(planet_signs[selected_planet]).value_counts()
                
                # Create bar chart
                st.bar_chart(sign_counts)
                
                # Show detailed stats
                with st.expander("Detailed Statistics"):
                    st.dataframe(sign_counts.reset_index().rename(
                        columns={'index': 'Sign', 0: 'Count'}
                    ))
        
        elif analysis_type == "Sign Occupancy":
            st.markdown("### Sign Occupancy Analysis")
            st.info("🚧 This feature is under development")
        
        elif analysis_type == "House Analysis":
            st.markdown("### House Analysis")
            st.info("🚧 This feature is under development")
        
        elif analysis_type == "Yoga Frequency":
            st.markdown("### Yoga Frequency Analysis")
            st.info("🚧 This feature is under development")
        
        # Export options
        st.divider()
        st.subheader("Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export to JSON"):
                # Prepare export data
                export_data = []
                for chart_info in st.session_state.processed_charts:
                    export_data.append({
                        'name': chart_info['name'],
                        'birth_datetime': chart_info['birth_datetime'].isoformat(),
                        'place': chart_info['place'],
                        'chart_summary': chart_info['chart_data'],
                        'planets': chart_info['chart'].get_graha_positions(),
                        'houses': chart_info['chart'].get_bhavas()
                    })
                
                json_str = json.dumps(export_data, indent=2, default=str)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"vedic_charts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Export to Excel"):
                # Prepare Excel export data
                with st.spinner("Preparing Excel export..."):
                    try:
                        from io import BytesIO
                        import pandas as pd
                        from datetime import datetime
                        
                        # Create Excel file in memory
                        output = BytesIO()
                        
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            # Overview sheet
                            overview_data = []
                            for chart_info in st.session_state.processed_charts:
                                overview_data.append({
                                    'Name': chart_info['name'],
                                    'Birth Date': chart_info['birth_datetime'].strftime('%Y-%m-%d'),
                                    'Birth Time': chart_info['birth_datetime'].strftime('%H:%M:%S'),
                                    'Place': chart_info['place'],
                                    'Lagna Sign': chart_info['chart_data']['ascendant']['rasi'],
                                    'Lagna Degrees': chart_info['chart_data']['ascendant']['degrees']
                                })
                            
                            overview_df = pd.DataFrame(overview_data)
                            overview_df.to_excel(writer, sheet_name='Overview', index=False)
                            
                            # Planetary positions sheet
                            planet_data = []
                            for chart_info in st.session_state.processed_charts:
                                grahas = chart_info['chart'].get_graha_positions()
                                for graha, data in grahas.items():
                                    planet_data.append({
                                        'Chart': chart_info['name'],
                                        'Planet': graha,
                                        'Sign': data['rasi'],
                                        'Longitude': f"{data['longitude']:.4f}",
                                        'Degrees in Sign': f"{data['longitude'] % 30:.2f}",
                                        'Nakshatra': data['nakshatra'] if isinstance(data['nakshatra'], str) else data['nakshatra'].get('name', 'Unknown'),
                                        'Retrograde': 'Yes' if data.get('is_retrograde', False) else 'No'
                                    })
                            
                            planets_df = pd.DataFrame(planet_data)
                            planets_df.to_excel(writer, sheet_name='Planetary Positions', index=False)
                            
                            # House placements sheet
                            house_data = []
                            for chart_info in st.session_state.processed_charts:
                                bhava_analysis = chart_info['chart'].get_bhava_analysis()
                                graha_placements = bhava_analysis.get('graha_placements', {})
                                
                                for house_str, planets in graha_placements.items():
                                    if planets:  # Only include houses with planets
                                        house_data.append({
                                            'Chart': chart_info['name'],
                                            'House': int(house_str),
                                            'Planets': ', '.join(planets)
                                        })
                            
                            if house_data:
                                houses_df = pd.DataFrame(house_data)
                                houses_df.to_excel(writer, sheet_name='House Placements', index=False)
                            
                            # Divisional charts sheet (D9 example)
                            navamsa_data = []
                            for chart_info in st.session_state.processed_charts:
                                ascendant = chart_info['chart'].get_ascendant()
                                grahas = chart_info['chart'].get_graha_positions()
                                
                                # D9 Lagna
                                d9_lagna = CalculationsHelper.get_navamsa_rasi(ascendant['longitude'])
                                navamsa_data.append({
                                    'Chart': chart_info['name'],
                                    'Planet': 'Lagna',
                                    'D9 Sign': d9_lagna
                                })
                                
                                # D9 planets
                                for graha, data in grahas.items():
                                    d9_sign = CalculationsHelper.get_navamsa_rasi(data['longitude'])
                                    navamsa_data.append({
                                        'Chart': chart_info['name'],
                                        'Planet': graha,
                                        'D9 Sign': d9_sign
                                    })
                            
                            if navamsa_data:
                                navamsa_df = pd.DataFrame(navamsa_data)
                                navamsa_df.to_excel(writer, sheet_name='D9 Navamsa', index=False)
                        
                        # Prepare file for download
                        processed_data = output.getvalue()
                        
                        st.download_button(
                            label="📥 Download Excel File",
                            data=processed_data,
                            file_name=f"vedic_charts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        st.success("✅ Excel file prepared successfully!")
                        
                    except Exception as e:
                        st.error(f"Error creating Excel file: {str(e)}")
                        st.info("Note: Make sure openpyxl is installed for Excel export.")
        
        with col3:
            if st.button("📑 Export to PDF"):
                st.info("🚧 PDF export coming soon!")