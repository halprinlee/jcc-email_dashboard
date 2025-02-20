import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(layout="wide", page_title="Marketing Calendar")
st.image("/workspaces/jcc-member_experience_dashboard/JCC-Logo-2-Color.png", width=450)
# Configure CSS Styles 

st.markdown("""
<style>
    /* Main page container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 300px;
        max-width: 400px;
        background-color: #f8f9fa;  /* Light background */
    }

    /* Sidebar content */
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        padding: 2rem 1rem;
    }

    /* Sidebar header */
    [data-testid="stSidebar"] h3 {
        color: #005899;  /* JCC Blue */
        border-bottom: 2px solid #27AAE1;  /* Light Blue border */
        padding-bottom: 0.5rem;
    }

     /* Target the multiselect container */
    .stMultiSelect {
        background-color: white;
    }

    /* Style the selected items/tags */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #005899 !important;
        border-radius: 4px !important;
        margin: 0.2rem !important;
        padding: 0.25rem 0.75rem !important;
    }

    /* Category-specific colors */
    .stMultiSelect [data-baseweb="tag"][data-testid*="Eblast"] {
        background-color: #27AAE1 !important;
    }

    .stMultiSelect [data-baseweb="tag"][data-testid*="Expected Marketing Need"] {
        background-color: #F58226 !important;
    }

    .stMultiSelect [data-baseweb="tag"][data-testid*="Member Engage"] {
        background-color: #A2D4AD !important;
        color: black !important;
    }

    .stMultiSelect [data-baseweb="tag"][data-testid*="Marketing Brief"] {
        background-color: #005899 !important;
    }

    .stMultiSelect [data-baseweb="tag"][data-testid*="Social"] {
        background-color: #EFC337 !important;
        color: black !important;
    }

    .stMultiSelect [data-baseweb="tag"][data-testid*="Other"] {
        background-color: #D3D3D3 !important;
        color: black !important;
    }

    /* Style the close button (x) */
    .stMultiSelect [data-baseweb="tag"] span[role="button"] {
        color: white !important;
    }

    /* Dark text for light backgrounds */
    .stMultiSelect [data-baseweb="tag"][data-testid*="Member Engage"] span[role="button"],
    .stMultiSelect [data-baseweb="tag"][data-testid*="Social"] span[role="button"],
    .stMultiSelect [data-baseweb="tag"][data-testid*="Other"] span[role="button"] {
        color: black !important;
    }

    /* Headers */
    h1 {
        color: #005899;  /* JCC Blue */
        font-size: 2rem !important;
        font-weight: bold !important;
    }

    h3 {
        color: #27AAE1;  /* Light Blue */
        font-size: 1.5rem !important;
        padding-bottom: 1rem !important;
    }

    /* Form fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border-color: #A2D4AD;  /* Teal Green */
    }

    .stSelectbox > div > div > div {
        border-radius: 8px;
        border-color: #A2D4AD;
    }

    /* Submit button */
    .stButton > button {
        background-color: #005899;  /* JCC Blue */
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
        font-weight: bold;
    }

    .stButton > button:hover {
        background-color: #27AAE1;  /* Light Blue */
        border: none;
    }

    /* Success/Error messages */
    .stAlert {
        padding: 1rem;
        border-radius: 8px;
    }

    /* Timeline container */
    [data-testid="stPlotlyChart"] > div {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 1rem;
    }

    /* Card-like containers */
    .css-1r6slb0 {  /* Streamlit's default container class */
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Date input fields */
    .stDateInput > div > div > input {
        border-radius: 8px;
        border-color: #A2D4AD;
    }

    /* Multiselect dropdown */
    .stMultiSelect > div > div > div {
        border-radius: 8px;
        border-color: #A2D4AD;
    }

    /* Search box */
    .stTextInput input {
        font-size: 1rem;
        padding: 0.5rem;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Function to load data
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        required_columns = ["Event Name", "Category", "Date", "End Date"]
        if not all(col in df.columns for col in required_columns):
            st.error("Error: The CSV file is missing required columns. Ensure it has 'Event Name', 'Category', 'Date', and 'End Date'.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Function to load categories
@st.cache_data
def load_categories(categories_file):
    try:
        categories_df = pd.read_csv(categories_file)
        if "Category" not in categories_df.columns:
            st.warning("Categories file doesn't have a 'Category' column. Using default categories.")
            return ["Expected Marketing Need", "Member Engage", "Other"]
        categories = categories_df["Category"].dropna().unique().tolist()
        if not categories:  # If the list is empty
            return ["Expected Marketing Need", "Member Engage", "Other"]
        return categories
    except Exception as e:
        st.warning(f"Error loading categories file: {str(e)}. Using default categories.")
        return ["Expected Marketing Need", "Member Engage", "Other"]

# Define JCC Brand Colors
JCC_COLORS = {
    "Marketing Brief": "#005899",  # JCC Blue
    "Eblast": "#27AAE1",  # Light Blue
    "Expected Marketing Need": "#F58226",  # Bright Orange
    "Member Engage": "#A2D4AD",  # Teal Green
    "Social": "#EFC337",  # Yellow
    "Other": "#D3D3D3"  # Light Grey (default)
}

def process_dataframe(df):
    # Convert date columns to datetime format
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df["End Date"] = pd.to_datetime(df["End Date"], errors='coerce')
    
    # Handle missing end dates
    df.loc[df["End Date"].isna(), "End Date"] = df["Date"]
    
    # Identify single-day events
    df["Single_Day"] = df["Date"] == df["End Date"]
    
    # Add color mapping
    df["Category_Color"] = df["Category"].map(JCC_COLORS).fillna("#D3D3D3")
    
    return df

def create_timeline(filtered_df):
    if filtered_df.empty:
        st.warning("No events found matching the selected filters.")
        return

    # Create shortened names for better display
    filtered_df["Short Name"] = filtered_df["Event Name"].apply(
        lambda x: str(x)[:30] + '...' if len(str(x)) > 30 else str(x)
    )

    fig = px.timeline(
        filtered_df,
        x_start="Date",
        x_end="End Date",
        y="Short Name",
        color="Category",
        color_discrete_map=JCC_COLORS,
        title="Marketing Calendar",
        height=max(400, len(filtered_df) * 40)  # Dynamic height based on number of events
    )

    # Customize layout
    fig.update_layout(
        showlegend=True,
        xaxis_rangeslider_visible=False,
        yaxis={
            'categoryorder': 'total ascending',
            'side': 'top',  # Move labels to top
            'title': None,  # Remove y-axis title
            'showgrid': False  # Remove horizontal grid lines
        },
        xaxis={
            'showgrid': True,  # Keep vertical grid lines
            'gridcolor': '#E5E5E5'  # Light gray grid lines
        },
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white"),
        margin=dict(t=100, b=20),  # Add more space at top for labels
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.02,  # Position above the chart
            xanchor="center",
            x=0.5
        )
    )

    # Add markers for single-day events
    for i, row in filtered_df[filtered_df["Single_Day"]].iterrows():
        fig.add_annotation(
            x=row["Date"],
            y=row["Short Name"],
            text="⬢",
            showarrow=False,
            font=dict(size=16, color=JCC_COLORS.get(row["Category"], "#D3D3D3"))
        )

    st.plotly_chart(fig, use_container_width=True)

def main():
    # Load data
    file_path = "/workspaces/jcc-member_experience_dashboard/Updated_Marketing_Calendar.csv"
    categories_file = "/workspaces/jcc-member_experience_dashboard/allowed_categories.csv"
    
    df = load_data(file_path)
    if df is None:
        return

    allowed_categories = load_categories(categories_file)
    
    # Process dataframe
    df = process_dataframe(df)

    # Sidebar filters
    with st.sidebar:
        st.write("### Filters")
        search_query = st.text_input("Search", "").strip()
        
        category_filter = st.multiselect(
            "Filter by Category",
            options=sorted(df["Category"].dropna().unique()),
            default=sorted(df["Category"].dropna().unique())
        )
        
        # Date range selector with better defaults
        default_start_date = datetime.today() - timedelta(days=14)
        default_end_date = datetime.today() + timedelta(days=14)  # Show future events by default
        date_range = st.date_input(
            "Select Date Range",
            [default_start_date, default_end_date],
            min_value=df["Date"].min().date(),
            max_value=df["Date"].max().date()
        )

    # Display title with the selected date range

    if len(date_range) == 2:
        start_date, end_date = date_range
    st.title(f"Marketing Calendar ({start_date.strftime('%x')} to {end_date.strftime('%x')})") 

    # Apply filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Event Name"].astype(str).str.contains(search_query, case=False, na=False)
        ]
    
    filtered_df = filtered_df[filtered_df["Category"].isin(category_filter)]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["Date"].dt.date >= start_date) &
            (filtered_df["Date"].dt.date <= end_date)
        ]

    # Create timeline visualization
    create_timeline(filtered_df)

    # Submission form
    st.write("### Submit a New Event")
    with st.form("new_event_form"):
        col1, col2 = st.columns(2)
        with col1:
            event_name = st.text_input("Event Name")
            category = st.selectbox("Category", options=allowed_categories)
        with col2:
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date", value=start_date)

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if not event_name:
                st.error("Please enter an event name.")
            elif end_date < start_date:
                st.error("End date cannot be before start date.")
            elif category not in allowed_categories:
                st.error("Invalid category! Please select from the available options.")
            else:
                try:
                    new_event = {
                        "Event Name": event_name,
                        "Category": category,
                        "Date": start_date,
                        "End Date": end_date
                    }
                    df_new = pd.concat([df, pd.DataFrame([new_event])], ignore_index=True)
                    df_new.to_csv(file_path, index=False)
                    st.success("Event Added to Calendar - Remember to Brief for Marketing Input")
                    st.markdown("[Click Here to Submit a Brief ↱](https://www.wrike.com/form/eyJhY2NvdW50SWQiOjYwNjQ3MjUsInRhc2tGb3JtSWQiOjkyNTU5OH0JNDg5MzY1OTc3OTI3NwljOWYyZDQxZDU0NzdmOGMyNzAwNDAwNzMxOWVlNjE5MWZkYTcxOTljMzNmNDExZjM5YWNhMjg3ZjIyY2JkMzM0)")
                    st.rerun()  # Refresh the page to show the new event
                except Exception as e:
                    st.error(f"Error saving event: {str(e)}")

if __name__ == "__main__":
    main()