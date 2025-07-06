import streamlit as st
import pandas as pd
import os
import sys
import plotly.express as px
import plotly.graph_objects as go

# Add project root and CoreLibrary to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'CoreLibrary'))

from calculations_helper import CalculationsHelper

# Set page config
st.set_page_config(
    page_title="Batch Analysis - Vedic Astrology",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Batch Analysis Tools")
st.markdown("""
Perform statistical analysis and pattern recognition on your processed chart data.
This tool helps identify trends, correlations, and significant patterns across multiple charts.
""")

# Check if charts are available
if 'processed_charts' not in st.session_state or not st.session_state.processed_charts:
    st.warning("⚠️ No processed charts found. Please upload and process data in the Research page first.")
    if st.button("Go to Research Page"):
        st.switch_page("pages/1_🔬_Research.py")
else:
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Date range filter
        st.subheader("Date Range")
        all_dates = [chart['birth_datetime'].date() for chart in st.session_state.processed_charts]
        date_range = st.date_input(
            "Select date range",
            value=(min(all_dates), max(all_dates)),
            min_value=min(all_dates),
            max_value=max(all_dates)
        )
        
        # Gender filter (if available)
        st.subheader("Additional Filters")
        # Placeholder for future filters
        
    # Main content
    st.info(f"Analyzing {len(st.session_state.processed_charts)} charts")
    
    # Analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌟 Planetary Patterns", 
        "🏠 House Analysis", 
        "📐 Aspects & Yogas",
        "📈 Custom Analysis"
    ])
    
    with tab1:
        st.header("Planetary Distribution Analysis")
        
        # Collect all planetary data
        all_planet_data = []
        for chart_info in st.session_state.processed_charts:
            grahas = chart_info['chart'].get_graha_positions()
            for graha, data in grahas.items():
                all_planet_data.append({
                    'Chart': chart_info['name'],
                    'Planet': graha,
                    'Sign': data['rasi'],
                    'Nakshatra': data['nakshatra'] if isinstance(data['nakshatra'], str) else data['nakshatra'].get('name', 'Unknown'),
                    'Degrees': data['longitude'] % 30
                })
        
        df_planets = pd.DataFrame(all_planet_data)
        
        # Planet in Signs Distribution
        st.subheader("Planets in Signs Distribution")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            selected_planet = st.selectbox(
                "Select Planet",
                options=['All'] + list(CalculationsHelper.GRAHAS)
            )
        
        with col1:
            if selected_planet == 'All':
                # Show distribution for all planets
                fig = px.histogram(
                    df_planets,
                    x='Sign',
                    color='Planet',
                    title='Distribution of All Planets across Signs',
                    category_orders={'Sign': CalculationsHelper.RASIS}
                )
            else:
                # Show distribution for selected planet
                planet_df = df_planets[df_planets['Planet'] == selected_planet]
                sign_counts = planet_df['Sign'].value_counts()
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=sign_counts.index,
                        y=sign_counts.values,
                        text=sign_counts.values,
                        textposition='auto',
                    )
                ])
                fig.update_layout(
                    title=f'{selected_planet} Distribution across Signs',
                    xaxis_title='Sign',
                    yaxis_title='Count'
                )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Nakshatra Distribution
        st.subheader("Nakshatra Distribution")
        
        nakshatra_counts = df_planets['Nakshatra'].value_counts().head(27)
        fig_nakshatra = px.bar(
            x=nakshatra_counts.index,
            y=nakshatra_counts.values,
            title='Top Nakshatra Occupancy',
            labels={'x': 'Nakshatra', 'y': 'Count'}
        )
        st.plotly_chart(fig_nakshatra, use_container_width=True)
        
        # Statistical Summary
        with st.expander("📊 Statistical Summary"):
            st.subheader("Sign Occupancy Statistics")
            
            sign_summary = []
            for sign in CalculationsHelper.RASIS:
                sign_data = df_planets[df_planets['Sign'] == sign]
                sign_summary.append({
                    'Sign': sign,
                    'Total Planets': len(sign_data),
                    'Unique Charts': sign_data['Chart'].nunique(),
                    'Most Common Planet': sign_data['Planet'].mode().iloc[0] if not sign_data.empty else 'N/A'
                })
            
            st.dataframe(pd.DataFrame(sign_summary), use_container_width=True)
    
    with tab2:
        st.header("House Analysis")
        
        # Collect house data
        all_house_data = []
        for chart_info in st.session_state.processed_charts:
            bhava_analysis = chart_info['chart'].get_bhava_analysis()
            graha_placements = bhava_analysis.get('graha_placements', {})
            
            for house_num, planets in graha_placements.items():
                for planet in planets:
                    all_house_data.append({
                        'Chart': chart_info['name'],
                        'House': int(house_num),
                        'Planet': planet
                    })
        
        if all_house_data:
            df_houses = pd.DataFrame(all_house_data)
            
            # House Occupancy
            st.subheader("House Occupancy Analysis")
            
            house_counts = df_houses.groupby('House')['Planet'].count().reset_index()
            house_counts.columns = ['House', 'Planet Count']
            
            fig_houses = go.Figure(data=[
                go.Bar(
                    x=house_counts['House'],
                    y=house_counts['Planet Count'],
                    text=house_counts['Planet Count'],
                    textposition='auto',
                    marker_color='lightblue'
                )
            ])
            fig_houses.update_layout(
                title='Total Planetary Occupancy by House',
                xaxis_title='House Number',
                yaxis_title='Total Planet Count',
                xaxis=dict(tickmode='linear', tick0=1, dtick=1)
            )
            st.plotly_chart(fig_houses, use_container_width=True)
            
            # Planet-House Matrix
            st.subheader("Planet-House Distribution Matrix")
            
            pivot_table = df_houses.pivot_table(
                index='Planet',
                columns='House',
                values='Chart',
                aggfunc='count',
                fill_value=0
            )
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=pivot_table.values,
                x=[f'H{i}' for i in pivot_table.columns],
                y=pivot_table.index,
                colorscale='Blues',
                text=pivot_table.values,
                texttemplate='%{text}',
                textfont={"size": 10}
            ))
            fig_heatmap.update_layout(
                title='Planet-House Distribution Heatmap',
                xaxis_title='House',
                yaxis_title='Planet'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("House data not available for analysis")
    
    with tab3:
        st.header("Aspects & Yogas Analysis")
        
        # Collect yoga data
        yoga_summary = {
            'Raj Yogas': 0,
            'Dhana Yogas': 0,
            'Spiritual Yogas': 0,
            'Challenging Yogas': 0
        }
        
        charts_with_yogas = []
        
        for chart_info in st.session_state.processed_charts:
            yogas = chart_info['chart'].find_yogas()
            has_yoga = False
            
            if yogas.get('raj_yogas'):
                yoga_summary['Raj Yogas'] += len(yogas['raj_yogas'])
                has_yoga = True
            if yogas.get('dhana_yogas'):
                yoga_summary['Dhana Yogas'] += len(yogas['dhana_yogas'])
                has_yoga = True
            if yogas.get('spiritual_yogas'):
                yoga_summary['Spiritual Yogas'] += len(yogas['spiritual_yogas'])
                has_yoga = True
            if yogas.get('challenging_yogas'):
                yoga_summary['Challenging Yogas'] += len(yogas['challenging_yogas'])
                has_yoga = True
            
            if has_yoga:
                charts_with_yogas.append(chart_info['name'])
        
        # Yoga Statistics
        st.subheader("Yoga Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of yoga types
            fig_yoga_pie = px.pie(
                values=list(yoga_summary.values()),
                names=list(yoga_summary.keys()),
                title='Distribution of Yoga Types'
            )
            st.plotly_chart(fig_yoga_pie, use_container_width=True)
        
        with col2:
            # Summary metrics
            st.metric("Total Yogas Found", sum(yoga_summary.values()))
            st.metric("Charts with Yogas", len(charts_with_yogas))
            st.metric("Average Yogas per Chart", 
                     f"{sum(yoga_summary.values()) / len(st.session_state.processed_charts):.2f}")
        
        # Detailed Yoga List
        with st.expander("Charts with Significant Yogas"):
            if charts_with_yogas:
                st.write(", ".join(charts_with_yogas[:20]))
                if len(charts_with_yogas) > 20:
                    st.write(f"... and {len(charts_with_yogas) - 20} more")
            else:
                st.write("No significant yogas found in the dataset")
    
    with tab4:
        st.header("Custom Analysis")
        st.markdown("Create your own custom analysis by selecting specific parameters")
        
        # Custom query builder
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_param = st.selectbox(
                "Select Parameter",
                options=[
                    "Planet in Specific Sign",
                    "Planet in Specific House",
                    "Specific Nakshatra",
                    "Retrograde Planets",
                    "Combustion Analysis"
                ]
            )
        
        with col2:
            if analysis_param == "Planet in Specific Sign":
                planet = st.selectbox("Planet", CalculationsHelper.GRAHAS)
                sign = st.selectbox("Sign", CalculationsHelper.RASIS)
                
                if st.button("Analyze"):
                    # Find charts with this combination
                    matching_charts = []
                    for chart_info in st.session_state.processed_charts:
                        grahas = chart_info['chart'].get_graha_positions()
                        if planet in grahas and grahas[planet]['rasi'] == sign:
                            matching_charts.append(chart_info['name'])
                    
                    st.subheader(f"Charts with {planet} in {sign}")
                    st.write(f"Found {len(matching_charts)} charts:")
                    if matching_charts:
                        st.write(", ".join(matching_charts[:50]))
                        if len(matching_charts) > 50:
                            st.write(f"... and {len(matching_charts) - 50} more")
            
            elif analysis_param == "Retrograde Planets":
                if st.button("Find Retrograde Planets"):
                    retrograde_data = []
                    for chart_info in st.session_state.processed_charts:
                        grahas = chart_info['chart'].get_graha_positions()
                        for graha, data in grahas.items():
                            if data.get('is_retrograde', False):
                                retrograde_data.append({
                                    'Chart': chart_info['name'],
                                    'Planet': graha,
                                    'Sign': data['rasi']
                                })
                    
                    if retrograde_data:
                        st.subheader("Retrograde Planets Found")
                        st.dataframe(pd.DataFrame(retrograde_data))
                    else:
                        st.info("No retrograde planets found in the dataset")
        
        # Export analysis results
        st.divider()
        st.subheader("Export Analysis Results")
        
        if st.button("Generate Complete Analysis Report"):
            st.info("🚧 Comprehensive report generation coming soon!")
            st.markdown("""
            The report will include:
            - Executive summary
            - Planetary distribution charts
            - House analysis
            - Yoga frequency
            - Statistical correlations
            - Custom query results
            """)