import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="GeoSol Goals Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Geographic Solutions - Goals Dashboard")
st.markdown("Track progress toward yearly financial goals and monitor accounts receivable.")

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

# Goal input
default_goal = 80000
yearly_goal = st.sidebar.number_input(
    "Yearly Goal ($)",
    min_value=0,
    value=default_goal,
    step=1000,
    help="Set your yearly revenue goal"
)

# File uploader
st.sidebar.header("📁 Data Upload")
uploaded_file = st.sidebar.file_uploader(
    "Upload Excel or CSV file",
    type=["xlsx", "xls", "csv"],
    help="Upload your accounts receivable data"
)

# Use sample data option
use_sample = st.sidebar.checkbox("Use sample data", value=True)

# Function to load data
@st.cache_data
def load_data(file, use_sample_data=False):
    """Load data from uploaded file or sample data"""
    if use_sample_data:
        # Load sample data
        df = pd.read_csv('sample_data.csv')
    elif file is not None:
        # Load uploaded file
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
    else:
        return None
    
    # Data preprocessing
    # Convert date columns to datetime
    date_columns = ['Date Sent', 'Payment Received Date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Ensure Amount is numeric
    if 'Amount' in df.columns:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    # Fill NaN in Payment Received with 'No'
    if 'Payment Received' in df.columns:
        df['Payment Received'] = df['Payment Received'].fillna('No')
    
    return df

# Load the data
df = load_data(uploaded_file, use_sample)

if df is not None and not df.empty:
    # Year filter
    available_years = sorted(df['Year'].dropna().unique()) if 'Year' in df.columns else []
    
    if available_years:
        selected_year = st.sidebar.selectbox(
            "Select Year",
            available_years,
            index=len(available_years) - 1  # Default to most recent year
        )
        
        # Filter data by selected year
        df_filtered = df[df['Year'] == selected_year].copy()
    else:
        st.warning("No 'Year' column found in data. Showing all data.")
        df_filtered = df.copy()
        selected_year = "All"
    
    # Calculate key metrics
    # Payments received (Payment Received = Yes)
    payments_received = df_filtered[df_filtered['Payment Received'].fillna('').str.upper() == 'YES']['Amount'].sum()
    
    # Outstanding AR (Payment Received = No)
    outstanding_ar = df_filtered[df_filtered['Payment Received'].fillna('').str.upper() == 'NO']['Amount'].sum()
    
    # Progress percentage
    progress_percentage = (payments_received / yearly_goal * 100) if yearly_goal > 0 else 0
    
    # Remaining to goal
    remaining_to_goal = max(0, yearly_goal - payments_received)
    
    # Display key metrics
    st.header(f"📈 Year {selected_year} Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Payments Received",
            f"${payments_received:,.2f}",
            delta=f"{progress_percentage:.1f}% of goal"
        )
    
    with col2:
        st.metric(
            "Outstanding AR",
            f"${outstanding_ar:,.2f}",
            delta=f"{len(df_filtered[df_filtered['Payment Received'].fillna('').str.upper() == 'NO'])} invoices"
        )
    
    with col3:
        st.metric(
            "Yearly Goal",
            f"${yearly_goal:,.2f}"
        )
    
    with col4:
        st.metric(
            "Remaining to Goal",
            f"${remaining_to_goal:,.2f}"
        )
    
    # Progress bar
    st.subheader("Goal Progress")
    progress_bar_col1, progress_bar_col2 = st.columns([3, 1])
    
    with progress_bar_col1:
        # Create progress bar using plotly
        fig_progress = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=payments_received,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Progress to ${yearly_goal:,.0f} Goal"},
            delta={'reference': yearly_goal, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, yearly_goal * 1.2]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, yearly_goal * 0.5], 'color': "lightgray"},
                    {'range': [yearly_goal * 0.5, yearly_goal], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': yearly_goal
                }
            }
        ))
        fig_progress.update_layout(height=300)
        st.plotly_chart(fig_progress, use_container_width=True)
    
    with progress_bar_col2:
        st.markdown("### Status")
        if progress_percentage >= 100:
            st.success(f"🎉 Goal achieved!")
        elif progress_percentage >= 75:
            st.info(f"💪 {100 - progress_percentage:.1f}% to go!")
        elif progress_percentage >= 50:
            st.warning(f"📊 Halfway there!")
        else:
            st.warning(f"🚀 Keep going!")
        
        st.markdown(f"**Progress:** {progress_percentage:.1f}%")
    
    # Monthly breakdown
    st.header("📅 Monthly Breakdown")
    
    # Extract month from Payment Received Date for payments received
    df_payments = df_filtered[
        (df_filtered['Payment Received'].fillna('').str.upper() == 'YES') & 
        (df_filtered['Payment Received Date'].notna())
    ].copy()
    
    if not df_payments.empty:
        df_payments['Month'] = df_payments['Payment Received Date'].dt.month
        df_payments['Month_Name'] = df_payments['Payment Received Date'].dt.strftime('%B')
        
        # Group by month
        monthly_summary = df_payments.groupby(['Month', 'Month_Name'])['Amount'].sum().reset_index()
        monthly_summary = monthly_summary.sort_values('Month')
        
        # Calculate monthly target (assuming equal distribution)
        monthly_target = yearly_goal / 12
        monthly_summary['Target'] = monthly_target
        monthly_summary['Difference'] = monthly_summary['Amount'] - monthly_target
        
        # Display monthly chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_monthly = go.Figure()
            
            fig_monthly.add_trace(go.Bar(
                x=monthly_summary['Month_Name'],
                y=monthly_summary['Amount'],
                name='Actual Payments',
                marker_color='lightblue'
            ))
            
            fig_monthly.add_trace(go.Scatter(
                x=monthly_summary['Month_Name'],
                y=monthly_summary['Target'],
                name='Monthly Target',
                mode='lines+markers',
                line=dict(color='red', dash='dash')
            ))
            
            fig_monthly.update_layout(
                title="Monthly Payments vs Target",
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col2:
            st.markdown("### Monthly Summary")
            st.dataframe(
                monthly_summary[['Month_Name', 'Amount', 'Target', 'Difference']].style.format({
                    'Amount': '${:,.2f}',
                    'Target': '${:,.2f}',
                    'Difference': '${:,.2f}'
                }).background_gradient(subset=['Difference'], cmap='RdYlGn'),
                hide_index=True,
                height=400
            )
        
        # Calculate remaining per month
        months_remaining = 12 - len(monthly_summary)
        if months_remaining > 0 and remaining_to_goal > 0:
            amount_per_month = remaining_to_goal / months_remaining
            st.info(f"💡 To reach the goal, you need approximately **${amount_per_month:,.2f}** per month for the remaining {months_remaining} month(s).")
    else:
        st.info("No payment data available for monthly breakdown.")
    
    # Accounts Receivable details
    st.header("📋 Outstanding Accounts Receivable")
    
    df_outstanding = df_filtered[df_filtered['Payment Received'].fillna('').str.upper() == 'NO'].copy()
    
    if not df_outstanding.empty:
        # Display AR summary
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Show outstanding invoices by client
            ar_by_client = df_outstanding.groupby('Client')['Amount'].sum().reset_index()
            ar_by_client = ar_by_client.sort_values('Amount', ascending=False)
            
            fig_ar = px.bar(
                ar_by_client,
                x='Client',
                y='Amount',
                title='Outstanding AR by Client',
                labels={'Amount': 'Amount ($)', 'Client': 'Client'}
            )
            fig_ar.update_layout(height=400)
            st.plotly_chart(fig_ar, use_container_width=True)
        
        with col2:
            st.markdown("### AR Summary")
            st.dataframe(
                ar_by_client.style.format({'Amount': '${:,.2f}'}),
                hide_index=True,
                height=400
            )
        
        # Detailed AR table
        st.subheader("Detailed Outstanding Invoices")
        display_columns = ['Client', 'Type', 'Quarter', 'Amount', 'Date Sent']
        available_display_columns = [col for col in display_columns if col in df_outstanding.columns]
        
        st.dataframe(
            df_outstanding[available_display_columns].sort_values('Amount', ascending=False).style.format({
                'Amount': '${:,.2f}'
            }),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("🎉 No outstanding accounts receivable!")
    
    # Data overview
    with st.expander("📊 View All Data"):
        st.dataframe(df_filtered, use_container_width=True)
        
        # Download button
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name=f"geosol_goals_{selected_year}.csv",
            mime="text/csv"
        )

else:
    # Show instructions when no data is loaded
    st.info("👈 Please upload a data file or enable 'Use sample data' in the sidebar to get started.")
    
    st.markdown("""
    ### Expected Data Format
    
    Your Excel or CSV file should contain the following columns:
    - **Client**: Client name
    - **Type**: Type of engagement (Contract, Project, etc.)
    - **Year**: Year of the invoice
    - **Quarter**: Quarter (Q1, Q2, Q3, Q4)
    - **Amount**: Invoice amount
    - **Sent**: Whether invoice was sent (Yes/No)
    - **Date Sent**: Date the invoice was sent
    - **Payment Received**: Whether payment was received (Yes/No)
    - **Payment Received Date**: Date the payment was received
    
    ### Sample Data
    
    A sample dataset is included. Enable "Use sample data" in the sidebar to explore the dashboard features.
    """)

# Footer
st.markdown("---")
st.markdown("*GeoSol Goals Dashboard - Track your financial goals and accounts receivable*")
