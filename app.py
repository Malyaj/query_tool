import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

def generate_dummy_retail_transactions(
    num_transactions=1000,
    max_items_per_transaction=5,
    num_stores=10,
    num_products=50,
    card_id_probability=0.8,
    start_date=None,
    end_date=None
):
    # Set default date range to past year if not provided
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()

    def random_date(start, end):
        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)

    def generate_transaction_line(transaction_id):
        store_id = f"store_{random.randint(1, num_stores)}"
        prod_id = f"prod_{random.randint(1, num_products)}"
        item_qty = random.randint(1, 5)
        base_price = round(random.uniform(5, 100), 2)
        discount = round(base_price * item_qty * random.uniform(0, 0.3), 2)
        net_spend = round(base_price * item_qty - discount, 2)
        ddtm = random_date(start_date, end_date)
        date = ddtm.date()

        card_id = f"card_{random.randint(1000, 9999)}" if random.random() < card_id_probability else None

        return {
            "card_id": card_id,
            "transaction_id": transaction_id,
            "store_id": store_id,
            "prod_id": prod_id,
            "item_qty": item_qty,
            "net_spend_amount": net_spend,
            "discount_amount": discount,
            "ddtm": ddtm,
            "date": date
        }

    all_records = []
    for i in range(num_transactions):
        transaction_id = f"txn_{i+1:05d}"
        num_items = random.randint(1, max_items_per_transaction)
        for _ in range(num_items):
            record = generate_transaction_line(transaction_id)
            all_records.append(record)

    df = pd.DataFrame(all_records)
    return df

df = generate_dummy_retail_transactions(num_transactions=500)
# Optionally save to CSV
df.to_csv("dummy_retail_transactions.csv", index=False)

data = pd.read_csv("dummy_retail_transactions.csv")
st.dataframe(data.head(4))

st.set_page_config(page_title="Query Tool", layout="wide")

col1, col2 = st.columns([1, 4])  # narrow left col, wider right col
with col1:
    # Multi-select dropdown for metrics
    metrics_options = ['spend', 'units', 'visits']
    metrics_selected = st.multiselect("Select Metrics:"
                                      , metrics_options
                                      )
    aggregations = []
    if 'spend' in metrics_selected:
        aggregations.append(('spend', 'net_spend_amount', sum))
    if 'units' in metrics_selected:
        aggregations.append(('units', 'item_qty', sum))
    if 'visits' in metrics_selected:
        aggregations.append(('visits', 'transaction_id', pd.Series.nunique))

    include_refund = ['Include Refunds', 'Exclude Refunds']
    include_refund_choice = st.radio("Choose an option:", options)

    if include_refund_choice == include_refund_choice[-1]:
        data = data['net_spend_amount']>=0.0

st.write(f"You selected: {choice}")
with col2:
    # Execute each aggregation and store the result
    result = {alias: func(data[col]) for alias, col, func in aggregations}
    # Convert result to a single-row DataFrame
    agg_df = pd.DataFrame([result])
    # Show DataFrame
    st.subheader("Data Table:")
    st.dataframe(agg_df)  # Interactive table
