from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Float, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Database setup
engine = create_engine('postgresql://postgres:root@localhost/postgres')
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()

# Define tables
pairs = Table('pairs', metadata,
              Column('pair_address', String, primary_key=True),
              Column('token0_address', String),
              Column('token1_address', String),
              Column('token0_reserve', Float),
              Column('token1_reserve', Float),
              Column('last_update_timestamp', DateTime))

transactions = Table('transactions', metadata,
                     Column('transaction_hash', String, primary_key=True),
                     Column('pair_address', String),
                     Column('block_number', Integer),
                     Column('timestamp', DateTime),
                     Column('amount0', Float),
                     Column('amount1', Float))

metadata.create_all(engine) # Creates tables if they don't exist

# Example insertion (this should be part of your transaction processing logic)
new_pair_data = {
    'pair_address': '0xExamplePairAddress',
    'token0_address': '0xExampleToken0Address',
    'token1_address': '0xExampleToken1Address',
    'token0_reserve': 1000.0,  # Example reserve amounts
    'token1_reserve': 500.0,
    'last_update_timestamp': datetime.now()
}

new_transaction_data = {
    'transaction_hash': '0xExampleTransactionHash',
    'pair_address': '0xExamplePairAddress',
    'block_number': 12345678,
    'timestamp': datetime.now(),
    'swap_type': 'BUY',
    'amount0': 100.0,
    'amount1': 50.0
}

# Insert new pair data
session.execute(pairs.insert(), new_pair_data)
# Insert new transaction data
session.execute(transactions.insert(), new_transaction_data)
session.commit()
