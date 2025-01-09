import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style="dark")


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        "order_item_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_item_id": "order_count",
        "price": "revenue"
    }, inplace=True)

    return daily_orders_df
def craete_fav_prodct(all_df):
    fav_prodct = all_df.groupby('product_category').customer_id.nunique().sort_values(ascending=False).reset_index()
    fav_prodct.rename(columns={'customer_id': 'total_customers'}, inplace=True)
    return fav_prodct

def create_bycity(all_df):
    bycity = all_df.groupby('city').customer_id.nunique().sort_values(ascending=False).reset_index()
    bycity.rename(columns={'customer_id': 'total_customers'}, inplace=True)
    return bycity

def create_bystate(all_df):
    bystate = all_df.groupby('state').customer_id.nunique().sort_values(ascending=False).reset_index()
    bystate.rename(columns={'customer_id':'total_customers'}, inplace=True)

    return bystate

def create_fav_payment(all_df):
    fav_payment = all_df.groupby('payment_type').customer_id.nunique().reset_index()
    fav_payment.rename(columns={'customer_id' : 'total_customers'}, inplace=True)

    return fav_payment

def create_seller_bystate(all_df):
    seller_bystate = all_df.groupby('state').seller_id.nunique().sort_values(ascending=False).reset_index()

    seller_bystate.rename(columns={'seller_id':'total_seller'}, inplace=True)

    return seller_bystate

def create_seller_bycity(all_df):
    seller_bycity = all_df.groupby('city').seller_id.nunique().sort_values(ascending=False).reset_index()

    seller_bycity.rename(columns={'seller_id':'total_seller'}, inplace=True)

    return seller_bycity

def create_rfm_df(all_df):
    rfm_df = all_df.groupby(by="customer_id", as_index=False).agg({"order_date": "max", "order_item_id": "nunique", "price": "sum"})
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df['max_order_timestamp'] = rfm_df['max_order_timestamp'].dt.date
    recent_order_date = all_df['order_date'].dt.date.max()
    rfm_df['recency'] = rfm_df['max_order_timestamp'].apply(lambda x: (recent_order_date - x).days)
    rfm_df.drop(columns=['max_order_timestamp'], inplace=True)
    return rfm_df

all_df = pd.read_csv('all_df.csv')

datetime_columns = ["order_date", "delivered_customer_date"]
all_df.sort_values(by="order_date", inplace=True)
all_df.reset_index(inplace=True)



for c in datetime_columns:
    all_df[c] = pd.to_datetime(all_df[c])

min_date = all_df['order_date'].min()
max_date = all_df['order_date'].max()

with st.sidebar:
    st.subheader("Pilih rentang Waktu : ")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df['order_date'] >= str(start_date)) & (all_df['order_date'] <= str(end_date))]

daily_order_df = create_daily_orders_df(main_df)
fav_prodct = craete_fav_prodct(main_df)
bycity = create_bycity(main_df)
bystate = create_bystate(main_df)
fav_payment = create_fav_payment(main_df)
seller_bystate = create_seller_bystate(main_df)
seller_bycity = create_seller_bycity(main_df)

rfm_df = create_rfm_df(main_df)

st.header(" E-Commerce Dashbord")


st.subheader('Daily Orders')
cols1, cols2 = st.columns(2)
with cols1:
    total_order = daily_order_df.order_count.sum()
    st.metric("Total Order", value=total_order)

with cols2:
    revenue = format_currency(daily_order_df.revenue.sum(), "RB", locale='es_CO')
    st.metric("Total Revenue" ,value=revenue)

fig, ax = plt.subplots(figsize=(16,8))
ax.plot(daily_order_df['order_date'], daily_order_df['order_count'], marker='o', linewidth=2, color="#42f59e")
ax.tick_params(axis='y',labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Best & Worst Performing Product")

fig, (ax1,ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))
collors = ['#42f59e','#d5d9de','#d5d9de','#d5d9de','#d5d9de','#d5d9de', '#d5d9de']
sns.barplot(data=fav_prodct.head(5), y='product_category', x='total_customers', palette=collors, ax=ax1)
ax1.set_xlabel(None)
ax1.set_ylabel(None)
ax1.set_title('Kategori Produk Denagna Performa Terbaik', fontsize=30, loc='center')
plt.tick_params(axis='y', labelsize=30)

sns.barplot(data=fav_prodct.sort_values(by='total_customers',ascending=True).head(5), y='product_category', x='total_customers', palette=collors, ax=ax2)
ax2.set_xlabel(None)
ax2.set_ylabel(None)
ax2.invert_xaxis()
ax2.yaxis.set_label_position('right')
ax2.yaxis.tick_right()
ax2.set_title('Kategori Produk Denagna Performa Terburuk', fontsize=30, loc='center')
plt.tick_params(axis='y', labelsize=20)

st.pyplot(fig)

st.subheader('Customer Demographics')
col1, col2 = st.columns(2)

with col1:
    plt.figure(figsize=(10, 8.9))
    collors = ['#42f59e', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de']
    sns.barplot(data=bycity.head(5), y='city', x='total_customers', palette=collors)
    plt.xlabel(None)
    plt.ylabel(None)
    plt.title('Jumlah Berdasarkan Kota', fontsize=30, loc='center')
    plt.tick_params(axis='y', labelsize=20)
    st.pyplot(plt)
with col2:
    plt.figure(figsize=(10, 7.5))
    collors = ['#42f59e', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de']
    sns.barplot(data=bystate.head(5), y='state', x='total_customers', palette=collors)
    plt.xlabel(None)
    plt.ylabel(None)
    plt.title('Jumlah Berdasarkan Negara Bagian', fontsize=30, loc='center')
    plt.tick_params(axis='y', labelsize=20)
    st.pyplot(plt)

st.subheader('Seller Demographics')
col1, col2 = st.columns(2)

with col1:
    plt.figure(figsize=(10, 8.9))
    collors = ['#42f59e', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de']
    sns.barplot(data=seller_bycity.head(5), y='city', x='total_seller', palette=collors)
    plt.xlabel(None)
    plt.ylabel(None)
    plt.title('Jumlah berdasarkan Kota', fontsize=30, loc='center')
    plt.tick_params(axis='y', labelsize=20)
    st.pyplot(plt)
with col2:
    plt.figure(figsize=(10, 7.5))
    collors = ['#42f59e', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de', '#d5d9de']
    sns.barplot(data=seller_bystate.head(5), y='state', x='total_seller', palette=collors)
    plt.xlabel(None)
    plt.ylabel(None)
    plt.title('Jumlah Berdasarkan Negara Bagian', fontsize=30, loc='center')
    plt.tick_params(axis='y', labelsize=20)
    st.pyplot(plt)

st.subheader('Number Payment Method')
plt.figure(figsize=(10,5))
collors = ['#d5d9de', '#42f59e', '#d5d9de','#d5d9de']
sns.barplot(data=fav_payment, y='total_customers', x='payment_type', palette=collors)
plt.xlabel(None)
plt.ylabel(None)
plt.tick_params(axis='x', labelsize=12)

st.pyplot(plt)

st.subheader("Best Customer Based on RFM Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(),1)
    st.metric("Average Recency (days) ", avg_recency)

with col2:
    avg_frequency  = round(rfm_df.frequency.mean(),2)
    st.metric('Average Frequency ', avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "RB", locale='es_CO')
    st.metric("Average Monetary ", avg_monetary)
fig, (ax1,ax2,ax3) = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
collors = ['#42f59e', '#42f59e', '#42f59e', '#42f59e', '#42f59e']
sns.barplot(data=rfm_df.sort_values(by='recency', ascending=True).head(5), y='recency', x='customer_id', palette=collors, ax=ax1)
ax1.set_xlabel(None)
ax1.set_ylabel(None)
ax1.set_title('a', fontsize=30, loc='center')
ax1.set_title('Berdasarkan recency', fontsize=30, loc='center')
ax1.tick_params(axis='x', labelsize=10,  rotation=60)

sns.barplot(data=rfm_df.sort_values(by='frequency', ascending=False).head(5), y='frequency', x='customer_id', palette=collors, ax=ax2)
ax2.set_xlabel(None)
ax2.set_ylabel(None)
ax2.invert_xaxis()
ax2.yaxis.set_label_position('right')
ax2.yaxis.tick_right()
ax2.set_title('Berdasarkan Frekuensi', fontsize=30, loc='center')
ax2.tick_params(axis='x', labelsize=10,  rotation=60)

sns.barplot(data=rfm_df.sort_values(by='monetary', ascending=False).head(5), y='monetary', x='customer_id', palette=collors, ax=ax3)
ax3.set_xlabel(None)
ax3.set_ylabel(None)
ax3.invert_xaxis()
ax3.yaxis.set_label_position('right')
ax3.yaxis.tick_right()
ax3.set_title('Berdasarkan Monetary', fontsize=30, loc='center')
ax3.tick_params(axis='x', labelsize=10,  rotation=60)
st.pyplot(fig)







