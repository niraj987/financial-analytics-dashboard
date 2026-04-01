import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_synthetic_retail_data(num_rows=250000):
    print(f"Generating synthetic retail dataset with {num_rows} rows for fast processing...")
    os.makedirs('data', exist_ok=True)
    parquet_path = 'data/online_retail_cleaned.parquet'
    
    if os.path.exists(parquet_path):
        print("Data already generated.")
        return pd.read_parquet(parquet_path)
        
    np.random.seed(42)
    
    # 1. Customers
    customer_ids = np.random.randint(10000, 20000, size=5000)
    
    # 2. Products
    products = [
        "WHITE HANGING HEART T-LIGHT HOLDER", "WHITE METAL LANTERN", "CREAM CUPID HEARTS COAT HANGER",
        "KNITTED UNION FLAG HOT WATER BOTTLE", "RED WOOLLY HOTTIE WHITE HEART.", "SET 7 BABUSHKA NESTING BOXES",
        "GLASS STAR FROSTED T-LIGHT HOLDER", "HAND WARMER UNION JACK", "HAND WARMER RED POLKA DOT",
        "ASSORTED COLOUR BIRD ORNAMENT", "POPPY'S PLAYHOUSE BEDROOM", "POPPY'S PLAYHOUSE KITCHEN",
        "FELTCRAFT PRINCESS CHARLOTTE DOLL", "IVORY KNITTED MUG COSY", "BOX OF 6 ASSORTED COLOUR TEASPOONS",
        "BOX OF VINTAGE JIGSAW BLOCKS", "BOX OF VINTAGE ALPHABET BLOCKS", "HOME BUILDING BLOCK WORD",
        "LOVE BUILDING BLOCK WORD", "RECIPE BOX WITH METAL HEART", "DOORMAT NEW ENGLAND",
        "JUMBO BAG RED RETROSPOT", "LUNCH BAG RED RETROSPOT", "JUMBO BAG PINK POLKADOT",
        "PACK OF 72 RETROSPOT CAKE CASES", "PACK OF 60 DINOSAUR CAKE CASES", "PACK OF 60 PINK PAISLEY CAKE CASES"
    ]
    product_prices = np.random.uniform(0.5, 25.0, size=len(products))
    product_dict = dict(zip(products, product_prices))
    
    # 3. Dates (over 2 years to allow seasonality and forecasting)
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2011, 12, 31)
    days_range = (end_date - start_date).days
    
    # Create rows
    selected_products = np.random.choice(products, size=num_rows, 
                                       p=np.random.dirichlet(np.ones(len(products)), size=1)[0])
                                       
    # Inject some seasonality (more sales near christmas)
    chosen_days = np.random.randint(0, days_range, size=num_rows)
    dates = [start_date + timedelta(days=int(d)) for d in chosen_days]
    
    df = pd.DataFrame({
        'Invoice': np.random.randint(500000, 600000, size=num_rows).astype(str),
        'StockCode': np.random.randint(10000, 99999, size=num_rows).astype(str),
        'Description': selected_products,
        'Quantity': np.random.poisson(lam=5, size=num_rows) + 1,
        'InvoiceDate': dates,
        'Price': [product_dict[p] for p in selected_products],
        'Customer ID': np.random.choice(customer_ids, size=num_rows).astype(str),
        'Country': np.random.choice(['United Kingdom', 'Germany', 'France', 'EIRE', 'Spain'], 
                                   p=[0.8, 0.05, 0.05, 0.05, 0.05], size=num_rows)
    })
    
    # Sort by date
    df = df.sort_values('InvoiceDate')
    
    # Make some missing customer IDs
    mask = np.random.rand(num_rows) < 0.1
    df.loc[mask, 'Customer ID'] = np.nan
    
    # Calculate Revenue as requested by models.py
    print("Cleaning and engineering revenue features...")
    df = df.dropna(subset=['Customer ID'])
    df['Revenue'] = df['Quantity'] * df['Price']
    
    # Keep only valid transactions
    df = df[df['Quantity'] > 0]
    
    print(f"Final Synthetic Data Shape: {df.shape}")
    df.to_parquet(parquet_path, index=False)
    print("Saved to parquet.")
    return df

if __name__ == "__main__":
    generate_synthetic_retail_data()
