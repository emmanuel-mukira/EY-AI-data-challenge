#!/usr/bin/env python3
import os
from snowflake.snowpark import Session

print("Testing Snowflake connection...")
print(f"Account: jfecknb-lwb72940")
print(f"User: EmmanuelMukira")
print(f"Warehouse: COMPUTE_WH")
print(f"Database: USER$EMMANUELMUKIRA")
print(f"Schema: PUBLIC")

try:
    session = Session.builder.configs({
        "account": "jfecknb-lwb72940",
        "user": "EmmanuelMukira",
        "password": "qikcox-kifxe4-xodqIn",
        "warehouse": "COMPUTE_WH",
        "database": "USER$EMMANUELMUKIRA",
        "schema": "PUBLIC"
    }).create()
    
    print("✅ Connected successfully!")
    
    # Test query
    result = session.sql("SELECT CURRENT_USER(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()").collect()
    print(f"User: {result[0]['CURRENT_USER()']}")
    print(f"Warehouse: {result[0]['CURRENT_WAREHOUSE()']}")
    print(f"Database: {result[0]['CURRENT_DATABASE()']}")
    
    session.close()
    print("✅ Session closed")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print(f"Error type: {type(e).__name__}")
