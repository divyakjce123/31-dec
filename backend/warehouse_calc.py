import math

class WarehouseCalculator:
    def __init__(self):
        self.conversion_factors = {
            'cm': 1.0, 'm': 100.0, 'km': 100000.0,
            'in': 2.54, 'ft': 30.48, 'yd': 91.44, 'mm': 0.1
        }

        self.MIN_RACK_WIDTH_CM = 1.0
        self.MIN_RACK_LENGTH_CM = 1.0
        self.MIN_FLOOR_HEIGHT_CM = 10.0

    def to_cm(self, value, unit):
        if value is None:
            return 0.0
        try:
            return float(value) * self.conversion_factors.get(unit.lower(), 1.0)
        except ValueError:
            return 0.0

    def create_warehouse_layout(self, config):
        # Debug: Print pallet configs structure
        for i, ws_conf in enumerate(config['workstation_configs']):
            pallets = ws_conf.get('pallet_configs', [])
            print(f"\nWorkstation {i} has {len(pallets)} pallets")
            for j, p in enumerate(pallets):
                print(f"  Pallet {j}: type={p.get('type')}, position={p.get('position', {})}")
        
        wh = config['warehouse_dimensions']

        W = self.to_cm(wh['width'], wh['unit'])
        L = self.to_cm(wh['length'], wh['unit'])
        H = self.to_cm(wh['height'], wh['unit'])
        H_safety = self.to_cm(wh['height_safety_margin'], wh['unit'])

        n_ws = config['num_workstations']
        wg = self.to_cm(config['workstation_gap'], config['workstation_gap_unit'])

        workstation_width = (W - wg * (n_ws - 1)) / n_ws
        workstation_height = H - H_safety

        workstations = []

        for i, ws_conf in enumerate(config['workstation_configs']):
            ws_x = i * (workstation_width + wg)

            aisle_width = self.to_cm(
                ws_conf['aisle_space'],  # Changed from aisle_width to aisle_space
                ws_conf.get('aisle_space_unit', 'cm')  # Changed from aisle_width_unit to aisle_space_unit
            )

            side_width = (workstation_width - aisle_width) / 2

            aisles = []

            # CENTRAL AISLE
            aisles.append({
                "id": f"central-aisle-{i}",
                "type": "central_aisle",
                "position": {"x": ws_x + side_width, "y": 0, "z": 0},
                "dimensions": {
                    "width": aisle_width,
                    "length": L,
                    "height": workstation_height
                }
            })

            # LEFT + RIGHT SIDES
            aisles += self._process_side(
                ws_conf['left_side_config'],
                ws_x,
                side_width,
                L,
                workstation_height,
                i,
                "left"
            )

            aisles += self._process_side(
                ws_conf['right_side_config'],
                ws_x + side_width + aisle_width,
                side_width,
                L,
                workstation_height,
                i,
                "right"
            )

            # ASSIGN PALLETS
            self._assign_pallets(ws_conf.get('pallet_configs', []), aisles)

            workstations.append({
                "id": f"workstation_{i+1}",
                "position": {"x": ws_x, "y": 0, "z": 0},
                "dimensions": {
                    "width": workstation_width,
                    "length": L,
                    "height": H
                },
                "aisles": aisles
            })

        return {
            "warehouse_dimensions": {
                "width": W,
                "length": L,
                "height": H
            },
            "workstations": workstations
        }

    def _process_side(
        self,
        cfg,
        start_x,
        side_width,
        side_length,
        side_height,
        ws_index,
        side_name
    ):
        # Extract wall gaps
        gf = self.to_cm(cfg['gap_front'], cfg['wall_gap_unit'])
        gb = self.to_cm(cfg['gap_back'], cfg['wall_gap_unit'])
        gl = self.to_cm(cfg['gap_left'], cfg['wall_gap_unit'])
        gr = self.to_cm(cfg['gap_right'], cfg['wall_gap_unit'])

        # Calculate available dimensions
        available_width = side_width - gl - gr
        available_length = side_length - gf - gb

        rows = cfg['num_rows']
        floors = cfg['num_floors']
        num_aisle = cfg['num_aisles']
        num_deep = cfg['deep']

        # Extract gaps
        aisle_gaps = [self.to_cm(g, cfg['wall_gap_unit']) for g in cfg.get('aisle_gaps', [])]
        deep_gaps = [self.to_cm(g, cfg['wall_gap_unit']) for g in cfg.get('deep_gaps', [])]
        
        # Pad gaps arrays to correct length
        aisle_gaps += [0.0] * max(0, (num_aisle - 1) - len(aisle_gaps))
        deep_gaps += [0.0] * max(0, (num_deep - 1) - len(deep_gaps))
        
        # Calculate total gaps
        total_aisles_gaps = sum(aisle_gaps) if num_aisle > 1 else 0
        total_deep_gaps = sum(deep_gaps) if num_deep > 1 else 0
        t = total_aisles_gaps + total_deep_gaps

        # Calculate total storage aisles per side
        n_aisle = num_aisle * num_deep

        # Calculate dimensions for each storage aisle
        n_aisle_length = available_length / rows if rows > 0 else 0
        n_aisle_width = (available_width - t) / n_aisle if n_aisle > 0 else 0
        n_aisle_height = side_height / floors if floors > 0 else 0

        aisles = []

        # Generate storage aisles with explicit gap objects for visualization
        for r in range(rows):
            y = gf + r * n_aisle_length
            current_x = start_x + gl
            storage_aisle_counter = 1  # Sequential storage aisle counter

            # Process each aisle group (num_aisle groups)
            for aisle_id in range(1, num_aisle + 1):
                # Process each depth within this aisle group
                for deep_idx in range(num_deep):
                    # Add deep gap before this depth (except for first depth in this aisle group)
                    if deep_idx > 0 and deep_idx - 1 < len(deep_gaps):
                        gap_size = deep_gaps[deep_idx - 1]
                        
                        # Create explicit gap object for visualization as empty space
                        for f in range(floors):
                            aisles.append({
                                "id": f"deep-gap-{ws_index}-{side_name}-{r}-{aisle_id}-{deep_idx}-{f}",
                                "type": "deep_gap",
                                "side": side_name,
                                "position": {
                                    "x": current_x,
                                    "y": y,
                                    "z": f * n_aisle_height
                                },
                                "dimensions": {
                                    "width": gap_size,
                                    "length": n_aisle_length,
                                    "height": n_aisle_height
                                },
                                "gap_info": {
                                    "gap_type": "deep_gap",
                                    "size": gap_size,
                                    "between_storage_aisles": [storage_aisle_counter - 1, storage_aisle_counter],
                                    "description": f"Deep gap {gap_size}cm between storage aisle {storage_aisle_counter - 1} and {storage_aisle_counter}"
                                },
                                "indices": {
                                    "row": r + 1,
                                    "floor": f + 1,
                                    "aisle_group": aisle_id,
                                    "depth_gap_index": deep_idx
                                },
                                "label": f"Deep Gap {gap_size}cm"
                            })
                        current_x += gap_size

                    # Generate storage aisles for all floors at this position
                    for f in range(floors):
                        aisles.append({
                            "id": f"aisle-{ws_index}-{side_name}-{r}-{storage_aisle_counter}-{f}",
                            "type": "storage_aisle",
                            "side": side_name,
                            "position": {
                                "x": current_x,
                                "y": y,
                                "z": f * n_aisle_height
                            },
                            "dimensions": {
                                "width": n_aisle_width,
                                "length": n_aisle_length,
                                "height": n_aisle_height
                            },
                            "indices": {
                                "row": r + 1,
                                "floor": f + 1,
                                "col": storage_aisle_counter,  # Sequential storage aisle number
                                "depth": deep_idx + 1,
                                "aisle": aisle_id  # Aisle group ID (shared by num_deep consecutive storage aisles)
                            },
                            "label": f"Aisle {aisle_id}",  # Label based on aisle group
                            "pallets": []
                        })

                    current_x += n_aisle_width
                    storage_aisle_counter += 1

                # Add aisle gap after this aisle group (except for last aisle group)
                if aisle_id < num_aisle and aisle_id - 1 < len(aisle_gaps):
                    gap_size = aisle_gaps[aisle_id - 1]
                    
                    # Create explicit gap object for visualization as empty space
                    for f in range(floors):
                        aisles.append({
                            "id": f"aisle-gap-{ws_index}-{side_name}-{r}-{aisle_id}-{f}",
                            "type": "aisle_gap",
                            "side": side_name,
                            "position": {
                                "x": current_x,
                                "y": y,
                                "z": f * n_aisle_height
                            },
                            "dimensions": {
                                "width": gap_size,
                                "length": n_aisle_length,
                                "height": n_aisle_height
                            },
                            "gap_info": {
                                "gap_type": "aisle_gap",
                                "size": gap_size,
                                "between_aisle_groups": [aisle_id, aisle_id + 1],
                                "description": f"Aisle gap {gap_size}cm between Aisle {aisle_id} and Aisle {aisle_id + 1}"
                            },
                            "indices": {
                                "row": r + 1,
                                "floor": f + 1,
                                "aisle_gap_index": aisle_id
                            },
                            "label": f"Aisle Gap {gap_size}cm"
                        })
                    current_x += gap_size

        return aisles

    def _assign_pallets(self, pallets, aisles):
        for i, p in enumerate(pallets):
            pos = p.get('position', {})
            if not pos:
                print(f"Warning: Pallet {i} has no position information")
                continue
            
            # Match pallet to aisle using: side, row, floor, depth, col (global aisle index)
            side = pos.get('side')
            row = pos.get('row')
            floor = pos.get('floor')
            depth = pos.get('depth')
            col = pos.get('col')  # Global aisle column index
            
            if not all([side, row is not None, floor is not None, depth is not None, col is not None]):
                print(f"Warning: Pallet {i} has incomplete position: {pos}")
                continue
                
            for aisle in aisles:
                if aisle['type'] != 'storage_aisle':
                    continue
                    
                # Match on all indices
                if (aisle.get('side') == side and
                    aisle['indices']['row'] == row and
                    aisle['indices']['floor'] == floor and
                    aisle['indices']['depth'] == depth and
                    aisle['indices']['col'] == col):
                    
                    aisle['pallets'].append({
                        "type": p.get('type', 'wooden'),
                        "color": p.get('color', '#8B4513'),
                        "dims": {
                            "length": p.get('length_cm', 0),
                            "width": p.get('width_cm', 0),
                            "height": p.get('height_cm', 0)
                        }
                    })
                    break
