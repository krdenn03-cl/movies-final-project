import streamlit as st
import pandas as pd
import plotly.express as px
import json


st.set_page_config(page_title="Movie Finance Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('tmdb_5000_movies.csv')
    df = df[(df['revenue'] > 0) & (df['budget'] > 0)]
    def extract_genre(json_str):
        try:
            genres = json.loads(json_str)
            return genres[0]['name'] if genres else 'Unknown'
        except: return 'Unknown'
    
    df['primary_genre'] = df['genres'].apply(extract_genre)
    df['profit'] = df['revenue'] - df['budget']
    df['ROI'] = (df['profit'] / df['budget']) * 100
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['year'] = df['release_date'].dt.year

    df['bgt_catgr'] = pd.qcut(
        df['budget'],
        q=3,
        labels=['low', 'med', 'high']
    )

    return df

df = load_data()

st.title("Movie Financial and Genre Dashboard")

selected_genres = st.multiselect(
    "Select Genres to Compare:",
    options=sorted(df['primary_genre'].unique()),
    default=['Action', 'Drama', 'Comedy']
)
year_range = st.slider(
    "Pick a year range:",
    int(df['year'].min()),
    int(df['year'].max()),
    (int(df['year'].min()), int(df['year'].max()))
)

selected_budgets = st.multiselect(
    "Pick which budget category:",
    options=['low', 'med', 'high'],
    default=['low', 'med', 'high']
)
filtered_df = df[
    (df['primary_genre'].isin(selected_genres)) & 
    (df['year'] >= year_range[0]) &
    (df['year'] <= year_range[1]) & 
    (df['bgt_catgr'].isin(selected_budgets))
]
col1, col2 = st.columns(2)

with col1:
    st.subheader("Budget vs. Revenue (Interactive)")
    fig1 = px.scatter(filtered_df, x="budget", y="revenue", 
                     color="primary_genre", hover_name="original_title",
                     size="popularity", log_x=True, log_y=True,
                     labels={"budget": "Budget in USD", "revenue": "Revenue in USD"},
                     template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Net Profit Distribution by Genre")
    fig2 = px.box(filtered_df, x="primary_genre", y="profit", 
                 color="primary_genre",
                 labels={"profit": "Net Profit in USD", "primary_genre": "Genre"},
                 template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("Average Return on Investment over Time")
roi_trend = filtered_df.groupby(['year', 'primary_genre'])['ROI'].mean().reset_index()
fig3 = px.line(roi_trend, x="year", y="ROI", color="primary_genre",
              labels={"ROI": "Average ROI"},
              template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Budget categories and average revenue")
budget_rev = filtered_df.groupby('bgt_catgr')['revenue'].mean().reset_index()
fig4 = px.bar( budget_rev, x='bgt_catgr', y='revenue', color='bgt_catgr', labels={'bgt_catgr': 'budget category', 'revenue': 'average revenue'}, title='Budget categories and average revenue'
)
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Budget categories and revnue")
fig5 = px.scatter(filtered_df,x='budget',y='revenue', color='bgt_catgr', hover_name='title',hover_data=['year', 'profit', 'ROI'], log_x=True,log_y=True,labels={'budget': 'budget', 'revenue': 'revenue'},title='Budget categories and revenue'
)
st.plotly_chart(fig5, use_container_width=True)


if st.checkbox('Show Raw Data Summary'):
    st.write(filtered_df[['original_title', 'budget', 'revenue', 'profit', 'ROI']].head(10))
