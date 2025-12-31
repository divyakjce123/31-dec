#!/usr/bin/env python3
"""
Test script for warehouse calculator functionality
"""

from warehouse_calc import WarehouseCalculator
import json

def test_basic_warehouse():
    """Test basic warehouse creation with pallets"""
    
    calc = WarehouseCalculator()
    
    # Test configuration matching the frontend structure
    config = {
        "id": "test-warehouse-1",
        "warehouse_dimensions": {
            "length": 3000,
            "width": 6000,
            "height": 1500,
            "height_safety_margin": 300,
            "unit": "cm"
        },
        "num_workstations": 2,
        "workstation_gap": 100,
        "workstation_gap_unit": "cm",
        "workstation_configs": [
            {
                "workstation_index": 0,
                "aisle_space": 500,  # Changed from aisle_width to aisle_space
                "aisle_space_unit": "cm",  # Changed from aisle_width_unit to aisle_space_unit
                "left_side_config": {
                    "num_floors": 3,
                    "num_rows": 2,
                    "num_aisles": 2,
                    "deep": 1,  # Changed from depth to deep
                    "aisle_gaps": [50],  # 1 gap between 2 aisles
                    "deep_gaps": [],    # 0 gaps for depth=1
                    "gap_front": 100,
                    "gap_back": 100,
                    "gap_left": 100,
                    "gap_right": 100,
                    "wall_gap_unit": "cm"
                },
                "right_side_config": {
                    "num_floors": 3,
                    "num_rows": 2,
                    "num_aisles": 2,
                    "deep": 2,  # Changed from depth to deep
                    "aisle_gaps": [50],  # 1 gap between 2 aisles
                    "deep_gaps": [75],   # 1 gap between 2 depths
                    "gap_front": 100,
                    "gap_back": 100,
                    "gap_left": 100,
                    "gap_right": 100,
                    "wall_gap_unit": "cm"
                },
                "pallet_configs": [
                    {
                        "type": "wooden",
                        "weight": 1200,
                        "length_cm": 120,
                        "width_cm": 80,
                        "height_cm": 15,
                        "color": "#8B4513",
                        "position": {
                            "floor": 1,
                            "row": 1,
                            "col": 1,
                            "depth": 1,
                            "side": "left"
                        }
                    },
                    {
                        "type": "plastic",
                        "weight": 800,
                        "length_cm": 100,
                        "width_cm": 100,
                        "height_cm": 12,
                        "color": "#1E90FF",
                        "position": {
                            "floor": 1,
                            "row": 1,
                            "col": 1,
                            "depth": 1,
                            "side": "right"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        print("Testing warehouse calculation...")
        layout = calc.create_warehouse_layout(config)
        
        print(f"✅ Warehouse created successfully!")
        print(f"   Dimensions: {layout['warehouse_dimensions']}")
        print(f"   Workstations: {len(layout['workstations'])}")
        
        # Check workstation details
        for i, ws in enumerate(layout['workstations']):
            print(f"\n   Workstation {i+1}:")
            print(f"     Aisles: {len(ws['aisles'])}")
            
            # Count storage aisles and pallets
            storage_aisles = [a for a in ws['aisles'] if a['type'] == 'storage_aisle']
            total_pallets = sum(len(a.get('pallets', [])) for a in storage_aisles)
            
            print(f"     Storage aisles: {len(storage_aisles)}")
            print(f"     Total pallets: {total_pallets}")
            
            # Show pallet positions
            for aisle in storage_aisles:
                if aisle.get('pallets'):
                    indices = aisle['indices']
                    print(f"       Aisle {indices['col']} (R{indices['row']}, F{indices['floor']}, {aisle['side']}): {len(aisle['pallets'])} pallets")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_warehouse()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")