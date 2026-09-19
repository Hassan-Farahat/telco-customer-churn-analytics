import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

# Page Setup
st.set_page_config(page_title='Customer Churn Dashboard', layout='wide')
st.title('📊 Customer Churn Dashboard')

# Load Data (Cached for performance)
@st.cache_data
def load_data():
    return pd.read_csv('Telco Customer Churn.csv')

df = load_data()

# Sidebar Filters
st.sidebar.header('Filters')

# Contract Filter
selected_contract = st.sidebar.multiselect(
    'Contract Type',
    options=df['Contract'].unique(),
    default=df['Contract'].unique()
)

# Internet Service Filter
selected_internet = st.sidebar.multiselect(
    'Internet Service',
    options=df['InternetService'].unique(),
    default=df['InternetService'].unique()
)

# Payment Method Filter
selected_payment = st.sidebar.multiselect(
    'Payment Method',
    options=df['PaymentMethod'].unique(),
    default=df['PaymentMethod'].unique()
)

# Apply all filters simultaneously
df_filtered = df[
    df['Contract'].isin(selected_contract) &
    df['InternetService'].isin(selected_internet) &
    df['PaymentMethod'].isin(selected_payment)
]

# Guard against empty filter selection
if df_filtered.empty:
    st.warning('⚠️ No data available for the selected filters. Please select at least one option from each filter.')
    st.stop()

# Key Performance Indicators (KPIs)
total_customers = len(df_filtered)
churn_count = (df_filtered['Churn'] == 'Yes').sum()
churn_rate = (churn_count / total_customers) if total_customers > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric('Total Customers', f'{total_customers:,}')
col2.metric('Churned Customers', f'{churn_count:,}')
col3.metric('Churn Rate', f'{churn_rate:.1%}')

st.divider()

# Charts Section
col_left, col_right = st.columns(2)

with col_left:
    st.subheader('Churn Rate Overview')
    fig1, ax1 = plt.subplots(figsize=(5, 3.5))
    
    churn_summary = (
        df_filtered['Churn'].value_counts(normalize=True).reset_index()
    )
    churn_summary.columns = ['Churn', 'Rate']

    bars = sns.barplot(
        data=churn_summary,
        x='Churn',
        y='Rate',
        hue='Churn',
        legend=False,
        ax=ax1,
        palette={'No': '#2b5c8f', 'Yes': '#d95f02'}
    )

    for bar in bars.patches:
        height = bar.get_height()
        if height > 0:
            ax1.annotate(
                f'{height:.1%}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords='offset points',
                ha='center',
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )

    ax1.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax1.set_ylim(0, 1.1)
    ax1.set_ylabel('Percentage', fontsize=10)
    sns.despine()
    st.pyplot(fig1)
    plt.close(fig1)

with col_right:
    st.subheader('Churn by Contract Type')
    fig2, ax2 = plt.subplots(figsize=(5, 3.5))

    contract_summary = (
        df_filtered.groupby('Contract')['Churn']
        .apply(lambda x: (x == 'Yes').mean())
        .reset_index(name='Churn Rate')
    )

    bars2 = sns.barplot(
        data=contract_summary,
        x='Contract',
        y='Churn Rate',
        hue='Contract',
        legend=False,
        ax=ax2,
        palette='Blues_r'
    )

    for bar in bars2.patches:
        height = bar.get_height()
        if height > 0:
            ax2.annotate(
                f'{height:.1%}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords='offset points',
                ha='center',
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )

    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax2.set_ylim(0, 1.1)
    ax2.set_ylabel('Churn Rate', fontsize=10)
    ax2.set_xlabel('Contract Type', fontsize=10)
    sns.despine()
    st.pyplot(fig2)
    plt.close(fig2)

st.divider()

with st.expander('📄 View Raw Data'):
    st.dataframe(df_filtered, use_container_width=True)