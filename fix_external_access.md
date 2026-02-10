# Fix External Access Integration for Satellite Data

## Problem
External Access Integration (EAI) setup fails or PyPI access is blocked, preventing installation of satellite data packages:
- `pystac-client`
- `planetary-computer` 
- `odc-stac`

## Root Cause
The EAI integration is not properly configured to allow PyPI and external API access.

## Solutions (Try in Order)

### Option 1: Use Existing Integration
If you have an existing integration (like `emmanuel-mukira`), select it when prompted instead of creating a new one.

### Option 2: Create Proper EAI Integration
```sql
-- Create the integration with correct syntax
CREATE OR REPLACE EXTERNAL API INTEGRATION DATA_CHALLENGE_EXTERNAL_ACCESS
API_PROVIDER = 'AWS_API_GATEWAY'
API_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/SnowflakeAPIAccess'
API_ALLOWED_PREFIXES = ('https://pypi.org/', 'https://planetarycomputer.microsoft.com/')
ENABLED = TRUE;
```

### Option 3: Manual Network Rules
```sql
-- Create network rule for PyPI
CREATE OR REPLACE NETWORK RULE PYPI_NETWORK_RULE
MODE = 'EGRESS'
TYPE = 'HOST_PORT'
VALUE_LIST = ('pypi.org', 'files.pythonhosted.org');

-- Create network rule for Planetary Computer
CREATE OR REPLACE NETWORK RULE PLANETARY_COMPUTER_RULE
MODE = 'EGRESS'
TYPE = 'HOST_PORT'
VALUE_LIST = ('planetarycomputer.microsoft.com');

-- Create integration with network rules
CREATE OR REPLACE EXTERNAL API INTEGRATION DATA_CHALLENGE_EXTERNAL_ACCESS
ALLOWED_NETWORK_RULES = (PYPI_NETWORK_RULE, PLANETARY_COMPUTER_RULE)
ENABLED = TRUE;
```

### Option 4: Use Snowflake's Pre-built Environment
Some Snowflake environments have these packages pre-installed. Check with:
```python
import pkg_resources
installed_packages = [d.project_name for d in pkg_resources.working_set]
print('pystac-client' in installed_packages)
print('planetary-computer' in installed_packages)
```

## Verification
After setup, test with:
```python
# Test PyPI access
!pip install requests

# Test satellite packages
import pystac_client
import planetary_computer
from odc.stac import stac_load
print("✓ All satellite packages working!")
```

## When to Use This Fix
Use this fix when you want to:
- Add Landsat satellite data features
- Access TerraClimate dataset
- Process external geospatial data
- Enhance models with satellite-derived indices (NDVI, NDWI, etc.)

## Timeline
Implement this fix **after** getting the baseline benchmark working, typically on Day 2-3 of the roadmap when adding advanced features.
