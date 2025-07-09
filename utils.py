import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

import pandas as pd
import random
from datetime import datetime, timedelta

def generate_dummy_retail_transactions(
    num_transactions=1000,
    max_items_per_transaction=5,
    num_stores=10,
    num_products=50,
    card_id_probability=0.8,
    return_probability=0.05,
    start_date=None,
    end_date=None,
    seed=42
):
    # Set reproducible seed
    random.seed(seed)

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

    # Generate original transactions
    all_records = []
    txn_counter = 1
    for i in range(num_transactions):
        transaction_id = f"txn_{txn_counter:05d}"
        txn_counter += 1
        num_items = random.randint(1, max_items_per_transaction)
        for _ in range(num_items):
            record = generate_transaction_line(transaction_id)
            all_records.append(record)

    df = pd.DataFrame(all_records)

    # Generate returns
    returns = []
    returnable_df = df[df['card_id'].notnull()].copy()
    return_candidates = returnable_df.sample(frac=return_probability, random_state=seed)

    for _, row in return_candidates.iterrows():
        return_qty = random.randint(1, row['item_qty'])
        if return_qty == 0:
            continue

        ratio = return_qty / row['item_qty']
        return_net_spend = round(-row['net_spend_amount'] * ratio, 2)
        return_discount = round(-row['discount_amount'] * ratio, 2)

        return_ddtm = row['ddtm'] + timedelta(days=random.randint(1, 14))
        return_date = return_ddtm.date()

        return_transaction_id = f"txn_{txn_counter:05d}"
        txn_counter += 1

        return_record = {
            "card_id": row['card_id'],
            "transaction_id": return_transaction_id,
            "store_id": row['store_id'],
            "prod_id": row['prod_id'],
            "item_qty": -return_qty,
            "net_spend_amount": return_net_spend,
            "discount_amount": return_discount,
            "ddtm": return_ddtm,
            "date": return_date
        }

        returns.append(return_record)

    df_returns = pd.DataFrame(returns)

    # Combine original and returns
    df_full = pd.concat([df, df_returns], ignore_index=True).sort_values(by="ddtm").reset_index(drop=True)
    df_full['date'] = pd.to_datetime(df_full['ddtm']).dt.date

    return df_full
