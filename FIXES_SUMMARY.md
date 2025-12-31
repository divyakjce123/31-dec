# Warehouse API Field Validation Fixes

## Problem
The frontend was sending data with field names that didn't match what the backend expected, causing 422 validation errors:

- `body.workstation_configs.0.aisle_space: Field required`
- `body.workstation_configs.0.left_side_config.deep: Field required`
- `body.workstation_configs.0.right_side_config.deep: Field required`

## Root Cause
Field name mismatches between frontend and backend:

1. **Frontend sent**: `aisle_width` → **Backend expected**: `aisle_space`
2. **Frontend sent**: `aisle_width_unit` → **Backend expected**: `aisle_space_unit`  
3. **Frontend sent**: `depth` → **Backend expected**: `deep`

## Solution
Updated the backend API models to match frontend field names:

### Backend Changes (`backend/main.py`)
- Changed `WorkstationConfig.aisle_width` → `aisle_space`
- Changed `WorkstationConfig.aisle_width_unit` → `aisle_space_unit`
- Changed `SideAisleConfig.depth` → `deep`

### Backend Calculator (`backend/warehouse_calc.py`)
- Updated references from `aisle_width` → `aisle_space`
- Updated references from `aisle_width_unit` → `aisle_space_unit`
- Updated references from `depth` → `deep`

### Frontend Changes (`frontend/src/app/components/warehouse/warehouse.component.ts`)
- Added field mapping in `updateWorkstationConfigs()`:
  - Maps `depth` → `deep` when sending to backend
  - Maps `aisle_width` → `aisle_space` when sending to backend
  - Maps `aisle_width_unit` → `aisle_space_unit` when sending to backend

### Test Updates (`backend/test_warehouse_calc.py`)
- Updated test data to use new field names
- Verified backend functionality with new schema

## Result
- ✅ API validation errors resolved
- ✅ Frontend and backend field names now aligned
- ✅ Warehouse creation requests now succeed
- ✅ All tests pass

The frontend can now successfully create warehouses without validation errors.