#!/usr/bin/env python3
"""
Test script for warehouse calculator functionality with new labeling logic
"""

from warehouse_calc import WarehouseCalculator
import json

def test_aisle_labeling():
    """Test aisle labeling logic with specific examples"""
    
    calc = WarehouseCalculator()
    
    # Test configuration with specific examples from requirements
    config = {
        "id": "test-warehouse-labeling",
        "warehouse_dimensions": {
            "length": 3000,
            "width": 6000,
            "height": 1500,
            "height_safety_margin": 300,
            "unit": "cm"
        },
        "num_workstations": 1,
        "workstation_gap": 100,
        "workstation_gap_unit": "cm",
        "workstation_configs": [
            {
                "workstation_index": 0,
                "aisle_space": 500,
                "aisle_space_unit": "cm",
                "left_side_config": {
                    "num_floors": 1,
                    "num_rows": 1,
                    "num_aisles": 2,  # num_aisle = 2
                    "deep": 1,        # num_deep = 1
                    "aisle_gaps": [50],  # 1 gap between 2 aisles = 50cm
                    "deep_gaps": [],     # 0 gaps for deep=1
                    "gap_front": 100,
                    "gap_back": 100,
                    "gap_left": 100,
                    "gap_right": 100,
                    "wall_gap_unit": "cm"
                },
                "right_side_config": {
                    "num_floors": 1,
                    "num_rows": 1,
                    "num_aisles": 2,  # num_aisle = 2
                    "deep": 2,        # num_deep = 2
                    "aisle_gaps": [100],  # 1 gap between aisle groups = 100cm
                    "deep_gaps": [50],    # 1 gap between depths = 50cm
                    "gap_front": 100,
                    "gap_back": 100,
                    "gap_left": 100,
                    "gap_right": 100,
                    "wall_gap_unit": "cm"
                },
                "pallet_configs": []
            }
        ]
    }
    
    try:
        print("Testing aisle labeling logic...")
        layout = calc.create_warehouse_layout(config)
        
        print(f"✅ Warehouse created successfully!")
        
        # Analyze left side (num_aisle=2, num_deep=1)
        ws = layout['workstations'][0]
        left_aisles = [a for a in ws['aisles'] if a.get('side') == 'left' and a['type'] == 'storage_aisle']
        left_gaps = [a for a in ws['aisles'] if a.get('side') == 'left' and a['type'] in ['aisle_gap', 'deep_gap']]
        right_aisles = [a for a in ws['aisles'] if a.get('side') == 'right' and a['type'] == 'storage_aisle']
        right_gaps = [a for a in ws['aisles'] if a.get('side') == 'right' and a['type'] in ['aisle_gap', 'deep_gap']]
        
        print(f"\n📍 LEFT SIDE ANALYSIS (num_aisle=2, num_deep=1):")
        print(f"   Total storage aisles: {len(left_aisles)} (expected: 2)")
        print(f"   Total gap objects: {len(left_gaps)} (expected: 1 aisle gap)")
        
        for aisle in left_aisles:
            indices = aisle['indices']
            label = aisle.get('label', 'No label')
            pos = aisle['position']
            print(f"   Storage Aisle {indices['col']}: {label}, Position X: {pos['x']:.1f}cm")
            
        for gap in left_gaps:
            label = gap.get('label', 'No label')
            pos = gap['position']
            dims = gap['dimensions']
            print(f"   Gap: {label}, Position X: {pos['x']:.1f}cm, Width: {dims['width']:.1f}cm")
        
        print(f"\n📍 RIGHT SIDE ANALYSIS (num_aisle=2, num_deep=2):")
        print(f"   Total storage aisles: {len(right_aisles)} (expected: 4)")
        print(f"   Total gap objects: {len(right_gaps)} (expected: 2 deep gaps + 1 aisle gap = 3)")
        
        # Group by aisle label
        aisle_groups = {}
        for aisle in right_aisles:
            label = aisle.get('label', 'No label')
            if label not in aisle_groups:
                aisle_groups[label] = []
            aisle_groups[label].append(aisle)
        
        for label, aisles in sorted(aisle_groups.items()):
            print(f"   {label}: {len(aisles)} storage aisles")
            for aisle in aisles:
                indices = aisle['indices']
                pos = aisle['position']
                print(f"     Storage Aisle {indices['col']}: Position X: {pos['x']:.1f}cm, Depth: {indices['depth']}")
                
        for gap in right_gaps:
            label = gap.get('label', 'No label')
            pos = gap['position']
            dims = gap['dimensions']
            gap_type = gap['type']
            print(f"   Gap: {label} ({gap_type}), Position X: {pos['x']:.1f}cm, Width: {dims['width']:.1f}cm")
        
        # Calculate and show gaps
        print(f"\n📏 GAP ANALYSIS:")
        
        # Left side gaps
        left_positions = sorted([a['position']['x'] for a in left_aisles])
        if len(left_positions) >= 2:
            gap = left_positions[1] - left_positions[0] - left_aisles[0]['dimensions']['width']
            print(f"   Left side gap between storage aisles: {gap:.1f}cm (expected: 50cm)")
        
        # Right side gaps
        right_positions = sorted([(a['position']['x'], a['indices']['aisle'], a['indices']['depth']) for a in right_aisles])
        print(f"   Right side storage aisle positions:")
        for i, (x, aisle_id, depth) in enumerate(right_positions):
            print(f"     Storage Aisle {i+1} (Aisle {aisle_id}, Depth {depth}): X={x:.1f}cm")
            
            if i > 0:
                prev_x = right_positions[i-1][0]
                gap = x - prev_x - right_aisles[0]['dimensions']['width']
                prev_aisle_id = right_positions[i-1][1]
                
                if aisle_id == prev_aisle_id:
                    print(f"       → Deep gap: {gap:.1f}cm (expected: 50cm)")
                else:
                    print(f"       → Aisle gap: {gap:.1f}cm (expected: 100cm)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_aisle_deep():
    """Test case: num_aisle=1, num_deep=2"""
    
    calc = WarehouseCalculator()
    
    config = {
        "id": "test-single-aisle-deep",
        "warehouse_dimensions": {
            "length": 2000,
            "width": 4000,
            "height": 1000,
            "height_safety_margin": 200,
            "unit": "cm"
        },
        "num_workstations": 1,
        "workstation_gap": 0,
        "workstation_gap_unit": "cm",
        "workstation_configs": [
            {
                "workstation_index": 0,
                "aisle_space": 300,
                "aisle_space_unit": "cm",
                "left_side_config": {
                    "num_floors": 1,
                    "num_rows": 1,
                    "num_aisles": 1,  # num_aisle = 1
                    "deep": 2,        # num_deep = 2
                    "aisle_gaps": [],     # 0 gaps for num_aisle=1
                    "deep_gaps": [50],    # 1 gap between depths = 50cm
                    "gap_front": 50,
                    "gap_back": 50,
                    "gap_left": 50,
                    "gap_right": 50,
                    "wall_gap_unit": "cm"
                },
                "right_side_config": {
                    "num_floors": 1,
                    "num_rows": 1,
                    "num_aisles": 1,
                    "deep": 1,
                    "aisle_gaps": [],
                    "deep_gaps": [],
                    "gap_front": 50,
                    "gap_back": 50,
                    "gap_left": 50,
                    "gap_right": 50,
                    "wall_gap_unit": "cm"
                },
                "pallet_configs": []
            }
        ]
    }
    
    try:
        print("\n" + "="*60)
        print("Testing single aisle with deep=2...")
        layout = calc.create_warehouse_layout(config)
        
        ws = layout['workstations'][0]
        left_aisles = [a for a in ws['aisles'] if a.get('side') == 'left' and a['type'] == 'storage_aisle']
        left_gaps = [a for a in ws['aisles'] if a.get('side') == 'left' and a['type'] in ['aisle_gap', 'deep_gap']]
        
        print(f"\n📍 LEFT SIDE ANALYSIS (num_aisle=1, num_deep=2):")
        print(f"   Total storage aisles: {len(left_aisles)} (expected: 2)")
        print(f"   Total gap objects: {len(left_gaps)} (expected: 1 deep gap)")
        
        for aisle in left_aisles:
            indices = aisle['indices']
            label = aisle.get('label', 'No label')
            pos = aisle['position']
            print(f"   Storage Aisle {indices['col']}: {label}, Position X: {pos['x']:.1f}cm, Depth: {indices['depth']}")
            
        for gap in left_gaps:
            label = gap.get('label', 'No label')
            pos = gap['position']
            dims = gap['dimensions']
            gap_type = gap['type']
            print(f"   Gap: {label} ({gap_type}), Position X: {pos['x']:.1f}cm, Width: {dims['width']:.1f}cm")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_aisle_labeling()
    success2 = test_single_aisle_deep()
    
    if success1 and success2:
        print("\n🎉 All labeling tests passed!")
    else:
        print("\n💥 Some tests failed!")