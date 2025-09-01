import math
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps

calculators_bp = Blueprint('calculators', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@calculators_bp.route('/')
@login_required
def index():
    """Lista todas as calculadoras disponíveis"""
    calculators = [
        {
            'name': 'Estruturas de Concreto',
            'description': 'Cálculos para vigas, pilares e lajes de concreto armado',
            'icon': 'fas fa-building',
            'route': 'calculators.concrete_structures'
        },
        {
            'name': 'Materiais de Construção',
            'description': 'Cálculo de quantidades de materiais (concreto, aço, agregados)',
            'icon': 'fas fa-cubes',
            'route': 'calculators.materials'
        },
        {
            'name': 'Geotecnia e Fundações',
            'description': 'Capacidade de carga, recalques e dimensionamento de fundações',
            'icon': 'fas fa-mountain',
            'route': 'calculators.geotechnics'
        },
        {
            'name': 'Hidráulica',
            'description': 'Cálculos de vazão, perda de carga e dimensionamento de tubulações',
            'icon': 'fas fa-tint',
            'route': 'calculators.hydraulics'
        },
        {
            'name': 'Custos e Orçamentos',
            'description': 'Estimativas de custos, BDI e cronograma físico-financeiro',
            'icon': 'fas fa-calculator',
            'route': 'calculators.costs'
        },
        {
            'name': 'Fórmulas de Resistência dos Materiais',
            'description': 'Tensão, deformação, lei de Hooke, flexão e outras fórmulas fundamentais',
            'icon': 'fas fa-cogs',
            'route': 'calculators.material_resistance'
        },
        {
            'name': 'Fórmulas de Engenharia Civil',
            'description': 'Todas as 20 fórmulas fundamentais organizadas por categoria: estruturas, concreto, hidráulica, geotecnia',
            'icon': 'fas fa-graduation-cap',
            'route': 'calculators.civil_engineering_formulas'
        }
    ]
    return render_template('calculators/index.html', calculators=calculators)

@calculators_bp.route('/concrete-structures', methods=['GET', 'POST'])
@login_required
def concrete_structures():
    """Calculadoras para estruturas de concreto"""
    results = {}
    
    if request.method == 'POST':
        calc_type = request.form.get('calc_type')
        
        if calc_type == 'beam_moment':
            # Cálculo de momento fletor em viga
            load = float(request.form.get('load', 0))
            length = float(request.form.get('length', 0))
            
            if load and length:
                # Viga simplesmente apoiada com carga uniformemente distribuída
                max_moment = (load * length**2) / 8
                results['beam_moment'] = {
                    'max_moment': max_moment,
                    'load': load,
                    'length': length
                }
        
        elif calc_type == 'column_load':
            # Cálculo de carga em pilar
            fck = float(request.form.get('fck', 0))  # Resistência do concreto
            area = float(request.form.get('area', 0))  # Área da seção
            
            if fck and area:
                # Carga máxima aproximada (sem armadura)
                max_load = 0.85 * fck * area / 1000  # Em kN
                results['column_load'] = {
                    'max_load': max_load,
                    'fck': fck,
                    'area': area
                }
        
        elif calc_type == 'slab_thickness':
            # Espessura mínima de laje
            span = float(request.form.get('span', 0))
            slab_type = request.form.get('slab_type', 'solid')
            
            if span:
                if slab_type == 'solid':
                    min_thickness = span / 40  # Para lajes maciças
                elif slab_type == 'ribbed':
                    min_thickness = span / 50  # Para lajes nervuradas
                else:
                    min_thickness = span / 35  # Para outras lajes
                
                results['slab_thickness'] = {
                    'min_thickness': min_thickness * 100,  # Em cm
                    'span': span,
                    'slab_type': slab_type
                }
    
    return render_template('calculators/concrete_structures.html', results=results)

@calculators_bp.route('/materials', methods=['GET', 'POST'])
@login_required
def materials():
    """Calculadoras para materiais de construção"""
    results = {}
    
    if request.method == 'POST':
        calc_type = request.form.get('calc_type')
        
        if calc_type == 'concrete_volume':
            # Cálculo de volume de concreto
            length = float(request.form.get('length', 0))
            width = float(request.form.get('width', 0))
            height = float(request.form.get('height', 0))
            
            if length and width and height:
                volume = length * width * height
                # Materiais necessários (traço 1:2:3)
                cement_bags = volume * 7  # sacos de 50kg
                sand_m3 = volume * 0.5
                gravel_m3 = volume * 0.8
                
                results['concrete_volume'] = {
                    'volume': volume,
                    'cement_bags': cement_bags,
                    'sand_m3': sand_m3,
                    'gravel_m3': gravel_m3
                }
        
        elif calc_type == 'steel_weight':
            # Peso do aço por diâmetro
            diameter = float(request.form.get('diameter', 0))
            length = float(request.form.get('length', 0))
            quantity = int(request.form.get('quantity', 1))
            
            if diameter and length:
                # Peso específico do aço = 7850 kg/m³
                area = math.pi * (diameter/1000)**2 / 4  # Área em m²
                weight_per_meter = area * 7850  # kg/m
                total_weight = weight_per_meter * length * quantity
                
                results['steel_weight'] = {
                    'weight_per_meter': weight_per_meter,
                    'total_weight': total_weight,
                    'diameter': diameter,
                    'length': length,
                    'quantity': quantity
                }
        
        elif calc_type == 'mortar_volume':
            # Volume de argamassa para alvenaria
            wall_area = float(request.form.get('wall_area', 0))
            joint_thickness = float(request.form.get('joint_thickness', 1.0))
            
            if wall_area:
                # Aproximadamente 30% da área em juntas
                mortar_volume = wall_area * (joint_thickness/100) * 0.3
                # Traço 1:3 (cimento:areia)
                cement_bags = mortar_volume * 8  # sacos de 50kg
                sand_m3 = mortar_volume * 0.6
                
                results['mortar_volume'] = {
                    'mortar_volume': mortar_volume,
                    'cement_bags': cement_bags,
                    'sand_m3': sand_m3,
                    'wall_area': wall_area
                }
    
    return render_template('calculators/materials.html', results=results)

@calculators_bp.route('/geotechnics', methods=['GET', 'POST'])
@login_required
def geotechnics():
    """Calculadoras para geotecnia e fundações"""
    results = {}
    
    if request.method == 'POST':
        calc_type = request.form.get('calc_type')
        
        if calc_type == 'bearing_capacity':
            # Capacidade de carga do solo
            cohesion = float(request.form.get('cohesion', 0))
            friction_angle = float(request.form.get('friction_angle', 0))
            unit_weight = float(request.form.get('unit_weight', 18))
            depth = float(request.form.get('depth', 1))
            width = float(request.form.get('width', 1))
            
            if friction_angle:
                # Fórmulas de Terzaghi (simplificadas)
                phi_rad = math.radians(friction_angle)
                
                # Fatores de capacidade de carga
                Nq = math.exp(math.pi * math.tan(phi_rad)) * (math.tan(math.pi/4 + phi_rad/2))**2
                Nc = (Nq - 1) / math.tan(phi_rad) if friction_angle > 0 else 5.14
                Ng = 2 * (Nq - 1) * math.tan(phi_rad)
                
                # Capacidade de carga última
                qu = cohesion * Nc + unit_weight * depth * Nq + 0.5 * unit_weight * width * Ng
                
                # Capacidade admissível (fator de segurança = 3)
                qa = qu / 3
                
                results['bearing_capacity'] = {
                    'ultimate_capacity': qu,
                    'allowable_capacity': qa,
                    'safety_factor': 3,
                    'cohesion': cohesion,
                    'friction_angle': friction_angle
                }
        
        elif calc_type == 'pile_capacity':
            # Capacidade de estaca
            diameter = float(request.form.get('diameter', 0))
            length = float(request.form.get('length', 0))
            tip_resistance = float(request.form.get('tip_resistance', 0))
            shaft_resistance = float(request.form.get('shaft_resistance', 0))
            
            if diameter and length:
                area_tip = math.pi * (diameter/2)**2
                perimeter = math.pi * diameter
                
                # Capacidade de ponta
                Qp = tip_resistance * area_tip
                
                # Capacidade lateral
                Qs = shaft_resistance * perimeter * length
                
                # Capacidade total
                Qt = Qp + Qs
                
                # Capacidade admissível
                Qa = Qt / 2  # Fator de segurança = 2
                
                results['pile_capacity'] = {
                    'tip_capacity': Qp,
                    'shaft_capacity': Qs,
                    'total_capacity': Qt,
                    'allowable_capacity': Qa,
                    'diameter': diameter,
                    'length': length
                }
    
    return render_template('calculators/geotechnics.html', results=results)

@calculators_bp.route('/hydraulics', methods=['GET', 'POST'])
@login_required
def hydraulics():
    """Calculadoras para hidráulica"""
    results = {}
    
    if request.method == 'POST':
        calc_type = request.form.get('calc_type')
        
        if calc_type == 'pipe_flow':
            # Vazão em tubulações
            diameter = float(request.form.get('diameter', 0)) / 1000  # Converter mm para m
            velocity = float(request.form.get('velocity', 0))
            
            if diameter and velocity:
                area = math.pi * (diameter/2)**2
                flow_rate = area * velocity * 1000  # L/s
                flow_rate_m3h = flow_rate * 3.6  # m³/h
                
                results['pipe_flow'] = {
                    'flow_rate_ls': flow_rate,
                    'flow_rate_m3h': flow_rate_m3h,
                    'diameter_mm': diameter * 1000,
                    'velocity': velocity,
                    'area': area
                }
        
        elif calc_type == 'head_loss':
            # Perda de carga
            length = float(request.form.get('length', 0))
            diameter = float(request.form.get('diameter', 0)) / 1000  # mm para m
            flow_rate = float(request.form.get('flow_rate', 0)) / 1000  # L/s para m³/s
            roughness = float(request.form.get('roughness', 0.1)) / 1000  # mm para m
            
            if length and diameter and flow_rate:
                # Fórmula de Hazen-Williams (simplificada)
                C = 130  # Coeficiente para tubos novos
                area = math.pi * (diameter/2)**2
                velocity = flow_rate / area
                
                # Perda de carga unitária (m/m)
                hf_unit = 10.65 * (flow_rate ** 1.85) / (C ** 1.85 * diameter ** 4.87)
                
                # Perda de carga total
                hf_total = hf_unit * length
                
                results['head_loss'] = {
                    'unit_loss': hf_unit,
                    'total_loss': hf_total,
                    'velocity': velocity,
                    'length': length,
                    'diameter_mm': diameter * 1000
                }
    
    return render_template('calculators/hydraulics.html', results=results)

@calculators_bp.route('/costs', methods=['GET', 'POST'])
@login_required
def costs():
    """Calculadoras para custos e orçamentos"""
    results = {}
    
    if request.method == 'POST':
        calc_type = request.form.get('calc_type')
        
        if calc_type == 'bdi_calculation':
            # Cálculo de BDI
            direct_cost = float(request.form.get('direct_cost', 0))
            indirect_cost_percent = float(request.form.get('indirect_cost_percent', 15))
            profit_percent = float(request.form.get('profit_percent', 8))
            tax_percent = float(request.form.get('tax_percent', 15))
            
            if direct_cost:
                # Cálculo do BDI
                bdi = ((1 + indirect_cost_percent/100) * (1 + profit_percent/100) / (1 - tax_percent/100)) - 1
                bdi_percent = bdi * 100
                
                # Preço de venda
                selling_price = direct_cost * (1 + bdi)
                
                results['bdi_calculation'] = {
                    'bdi_percent': bdi_percent,
                    'direct_cost': direct_cost,
                    'selling_price': selling_price,
                    'indirect_cost_percent': indirect_cost_percent,
                    'profit_percent': profit_percent,
                    'tax_percent': tax_percent
                }
        
        elif calc_type == 'unit_cost':
            # Custo unitário de serviço
            material_cost = float(request.form.get('material_cost', 0))
            labor_cost = float(request.form.get('labor_cost', 0))
            equipment_cost = float(request.form.get('equipment_cost', 0))
            productivity = float(request.form.get('productivity', 1))
            
            if productivity:
                total_unit_cost = (material_cost + labor_cost + equipment_cost) / productivity
                
                results['unit_cost'] = {
                    'total_unit_cost': total_unit_cost,
                    'material_cost': material_cost,
                    'labor_cost': labor_cost,
                    'equipment_cost': equipment_cost,
                    'productivity': productivity
                }
        
        elif calc_type == 'schedule_cost':
            # Cronograma físico-financeiro
            total_value = float(request.form.get('total_value', 0))
            duration_months = int(request.form.get('duration_months', 12))
            curve_type = request.form.get('curve_type', 'linear')
            
            if total_value and duration_months:
                schedule = []
                accumulated = 0
                
                for month in range(1, duration_months + 1):
                    monthly_percent = 0  # Valor padrão
                    if curve_type == 'linear':
                        monthly_percent = 100 / duration_months
                    elif curve_type == 's_curve':
                        # Curva S simplificada
                        t = month / duration_months
                        monthly_percent = (3 * t**2 - 2 * t**3) * 100
                        if month > 1:
                            prev_t = (month-1) / duration_months
                            prev_percent = (3 * prev_t**2 - 2 * prev_t**3) * 100
                            monthly_percent = monthly_percent - prev_percent
                    else:
                        monthly_percent = 100 / duration_months  # Fallback para linear
                    
                    monthly_value = total_value * monthly_percent / 100
                    accumulated += monthly_value
                    
                    schedule.append({
                        'month': month,
                        'monthly_percent': monthly_percent,
                        'monthly_value': monthly_value,
                        'accumulated_percent': (accumulated / total_value) * 100,
                        'accumulated_value': accumulated
                    })
                
                results['schedule_cost'] = {
                    'schedule': schedule,
                    'total_value': total_value,
                    'duration_months': duration_months
                }
    
    return render_template('calculators/costs.html', results=results)

@calculators_bp.route('/material-resistance', methods=['GET', 'POST'])
@login_required
def material_resistance():
    """Fórmulas de Resistência dos Materiais - 20 Fórmulas Fundamentais"""
    results = {}
    
    if request.method == 'POST':
        calc_type = request.form.get('calc_type')
        
        if calc_type == 'normal_stress':
            # 1. Tensão Normal (σ = F/A)
            force = float(request.form.get('force', 0))  # N
            area = float(request.form.get('area', 0))  # mm²
            
            if force and area:
                area_m2 = area / 1000000  # Converter mm² para m²
                normal_stress = force / area_m2  # Pa
                normal_stress_mpa = normal_stress / 1000000  # MPa
                
                results['normal_stress'] = {
                    'normal_stress_pa': normal_stress,
                    'normal_stress_mpa': normal_stress_mpa,
                    'force': force,
                    'area_mm2': area,
                    'area_m2': area_m2
                }
        
        elif calc_type == 'deformation':
            # 2. Deformação (ε = ΔL/L₀)
            delta_length = float(request.form.get('delta_length', 0))  # mm
            initial_length = float(request.form.get('initial_length', 0))  # mm
            
            if initial_length:
                deformation = delta_length / initial_length  # adimensional
                deformation_percent = deformation * 100
                
                results['deformation'] = {
                    'deformation': deformation,
                    'deformation_percent': deformation_percent,
                    'delta_length': delta_length,
                    'initial_length': initial_length
                }
        
        elif calc_type == 'hooke_law':
            # 3. Lei de Hooke (σ = E⋅ε)
            elastic_modulus = float(request.form.get('elastic_modulus', 0))  # GPa
            strain = float(request.form.get('strain', 0))  # adimensional
            
            if elastic_modulus and strain:
                stress = elastic_modulus * strain * 1000  # MPa
                
                results['hooke_law'] = {
                    'stress_mpa': stress,
                    'elastic_modulus_gpa': elastic_modulus,
                    'strain': strain
                }
        
        elif calc_type == 'bending_moment':
            # 4. Momento Fletor (M = F⋅d)
            force = float(request.form.get('force', 0))  # N
            distance = float(request.form.get('distance', 0))  # m
            
            if force and distance:
                bending_moment = force * distance  # N.m
                bending_moment_knm = bending_moment / 1000  # kN.m
                
                results['bending_moment'] = {
                    'bending_moment_nm': bending_moment,
                    'bending_moment_knm': bending_moment_knm,
                    'force': force,
                    'distance': distance
                }
        
        elif calc_type == 'moment_inertia':
            # 5. Inércia da Seção (I = b⋅h³/12) - seção retangular
            base = float(request.form.get('base', 0))  # cm
            height = float(request.form.get('height', 0))  # cm
            
            if base and height:
                moment_inertia = (base * height**3) / 12  # cm⁴
                moment_inertia_m4 = moment_inertia / 100000000  # m⁴
                
                results['moment_inertia'] = {
                    'moment_inertia_cm4': moment_inertia,
                    'moment_inertia_m4': moment_inertia_m4,
                    'base': base,
                    'height': height
                }
        
        elif calc_type == 'bending_stress':
            # 6. Tensão de Flexão (σf = M⋅y/I)
            moment = float(request.form.get('moment', 0))  # N.m
            distance_centroid = float(request.form.get('distance_centroid', 0))  # cm
            moment_inertia = float(request.form.get('moment_inertia', 0))  # cm⁴
            
            if moment and distance_centroid and moment_inertia:
                # Converter unidades
                moment_ncm = moment * 100  # N.cm
                bending_stress = (moment_ncm * distance_centroid) / moment_inertia  # N/cm²
                bending_stress_mpa = bending_stress / 10  # MPa
                
                results['bending_stress'] = {
                    'bending_stress_ncm2': bending_stress,
                    'bending_stress_mpa': bending_stress_mpa,
                    'moment': moment,
                    'distance_centroid': distance_centroid,
                    'moment_inertia': moment_inertia
                }
        
        elif calc_type == 'shear_stress':
            # 7. Cisalhamento (τ = V/A)
            shear_force = float(request.form.get('shear_force', 0))  # N
            area = float(request.form.get('area', 0))  # mm²
            
            if shear_force and area:
                area_m2 = area / 1000000  # Converter mm² para m²
                shear_stress = shear_force / area_m2  # Pa
                shear_stress_mpa = shear_stress / 1000000  # MPa
                
                results['shear_stress'] = {
                    'shear_stress_pa': shear_stress,
                    'shear_stress_mpa': shear_stress_mpa,
                    'shear_force': shear_force,
                    'area': area
                }
        
        elif calc_type == 'concrete_fck':
            # 8. Resistência Característica do Concreto (fck = Fruptura/A)
            rupture_force = float(request.form.get('rupture_force', 0))  # N
            area = float(request.form.get('area', 0))  # cm²
            
            if rupture_force and area:
                area_m2 = area / 10000  # Converter cm² para m²
                fck = rupture_force / area_m2  # Pa
                fck_mpa = fck / 1000000  # MPa
                
                results['concrete_fck'] = {
                    'fck_pa': fck,
                    'fck_mpa': fck_mpa,
                    'rupture_force': rupture_force,
                    'area_cm2': area
                }
        
        elif calc_type == 'mortar_mix':
            # 9. Dosagem de Argamassa (Traço 1:a:b)
            cement_bags = float(request.form.get('cement_bags', 1))  # sacos de 50kg
            sand_ratio = float(request.form.get('sand_ratio', 3))  # proporção de areia
            aggregate_ratio = float(request.form.get('aggregate_ratio', 0))  # proporção de agregado (opcional)
            
            if cement_bags and sand_ratio:
                cement_kg = cement_bags * 50
                sand_kg = cement_kg * sand_ratio
                aggregate_kg = cement_kg * aggregate_ratio if aggregate_ratio else 0
                
                results['mortar_mix'] = {
                    'cement_kg': cement_kg,
                    'sand_kg': sand_kg,
                    'aggregate_kg': aggregate_kg,
                    'cement_bags': cement_bags,
                    'sand_ratio': sand_ratio,
                    'aggregate_ratio': aggregate_ratio
                }
        
        elif calc_type == 'abrams_law':
            # 10. Lei de Abrams (fc = K⋅(a/c)^-n)
            k_constant = float(request.form.get('k_constant', 200))  # constante K
            water_cement_ratio = float(request.form.get('water_cement_ratio', 0.5))  # a/c
            n_exponent = float(request.form.get('n_exponent', 2))  # expoente n
            
            if k_constant and water_cement_ratio and n_exponent:
                concrete_strength = k_constant * (water_cement_ratio ** (-n_exponent))
                
                results['abrams_law'] = {
                    'concrete_strength_mpa': concrete_strength,
                    'k_constant': k_constant,
                    'water_cement_ratio': water_cement_ratio,
                    'n_exponent': n_exponent
                }
        
        elif calc_type == 'flow_rate':
            # 11. Vazão (Q = A⋅v)
            area = float(request.form.get('area', 0))  # m²
            velocity = float(request.form.get('velocity', 0))  # m/s
            
            if area and velocity:
                flow_rate = area * velocity  # m³/s
                flow_rate_ls = flow_rate * 1000  # L/s
                flow_rate_m3h = flow_rate * 3600  # m³/h
                
                results['flow_rate'] = {
                    'flow_rate_m3s': flow_rate,
                    'flow_rate_ls': flow_rate_ls,
                    'flow_rate_m3h': flow_rate_m3h,
                    'area': area,
                    'velocity': velocity
                }
        
        elif calc_type == 'continuity_equation':
            # 12. Equação da Continuidade (A₁⋅v₁ = A₂⋅v₂)
            area1 = float(request.form.get('area1', 0))  # m²
            velocity1 = float(request.form.get('velocity1', 0))  # m/s
            area2 = float(request.form.get('area2', 0))  # m²
            velocity2 = float(request.form.get('velocity2', 0))  # m/s
            
            # Calcular a variável que está em branco
            if area1 and velocity1 and area2 and not velocity2:
                velocity2 = (area1 * velocity1) / area2
            elif area1 and velocity1 and velocity2 and not area2:
                area2 = (area1 * velocity1) / velocity2
            elif area2 and velocity2 and area1 and not velocity1:
                velocity1 = (area2 * velocity2) / area1
            elif area2 and velocity2 and velocity1 and not area1:
                area1 = (area2 * velocity2) / velocity1
            
            flow_rate1 = area1 * velocity1 if area1 and velocity1 else 0
            flow_rate2 = area2 * velocity2 if area2 and velocity2 else 0
            
            results['continuity_equation'] = {
                'area1': area1,
                'velocity1': velocity1,
                'area2': area2,
                'velocity2': velocity2,
                'flow_rate1': flow_rate1,
                'flow_rate2': flow_rate2
            }
        
        elif calc_type == 'bernoulli_equation':
            # 13. Equação de Bernoulli (p/γ + v²/2g + z = constante)
            pressure1 = float(request.form.get('pressure1', 0))  # Pa
            velocity1 = float(request.form.get('velocity1', 0))  # m/s
            elevation1 = float(request.form.get('elevation1', 0))  # m
            pressure2 = float(request.form.get('pressure2', 0))  # Pa
            velocity2 = float(request.form.get('velocity2', 0))  # m/s
            elevation2 = float(request.form.get('elevation2', 0))  # m
            specific_weight = float(request.form.get('specific_weight', 9810))  # N/m³ (água)
            
            g = 9.81  # m/s²
            
            # Carga total no ponto 1
            pressure_head1 = pressure1 / specific_weight
            velocity_head1 = (velocity1**2) / (2 * g)
            total_head1 = pressure_head1 + velocity_head1 + elevation1
            
            # Carga total no ponto 2
            pressure_head2 = pressure2 / specific_weight
            velocity_head2 = (velocity2**2) / (2 * g)
            total_head2 = pressure_head2 + velocity_head2 + elevation2
            
            results['bernoulli_equation'] = {
                'total_head1': total_head1,
                'total_head2': total_head2,
                'pressure_head1': pressure_head1,
                'velocity_head1': velocity_head1,
                'pressure_head2': pressure_head2,
                'velocity_head2': velocity_head2,
                'head_difference': abs(total_head1 - total_head2)
            }
        
        elif calc_type == 'reynolds_number':
            # 14. Número de Reynolds (Re = ρ⋅v⋅D/μ)
            density = float(request.form.get('density', 1000))  # kg/m³
            velocity = float(request.form.get('velocity', 0))  # m/s
            diameter = float(request.form.get('diameter', 0))  # m
            dynamic_viscosity = float(request.form.get('dynamic_viscosity', 0.001))  # Pa.s
            
            if velocity and diameter and dynamic_viscosity:
                reynolds = (density * velocity * diameter) / dynamic_viscosity
                
                # Classificação do escoamento
                if reynolds < 2300:
                    flow_type = "Laminar"
                elif reynolds > 4000:
                    flow_type = "Turbulento"
                else:
                    flow_type = "Transição"
                
                results['reynolds_number'] = {
                    'reynolds': reynolds,
                    'flow_type': flow_type,
                    'density': density,
                    'velocity': velocity,
                    'diameter': diameter,
                    'dynamic_viscosity': dynamic_viscosity
                }
        
        elif calc_type == 'manning_formula':
            # 15. Fórmula de Manning (Q = 1/n⋅A⋅R^(2/3)⋅S^(1/2))
            area = float(request.form.get('area', 0))  # m²
            wetted_perimeter = float(request.form.get('wetted_perimeter', 0))  # m
            slope = float(request.form.get('slope', 0))  # m/m
            manning_n = float(request.form.get('manning_n', 0.013))  # coeficiente de rugosidade
            
            if area and wetted_perimeter and slope and manning_n:
                hydraulic_radius = area / wetted_perimeter
                flow_rate = (1 / manning_n) * area * (hydraulic_radius ** (2/3)) * (slope ** 0.5)
                
                results['manning_formula'] = {
                    'flow_rate': flow_rate,
                    'hydraulic_radius': hydraulic_radius,
                    'area': area,
                    'wetted_perimeter': wetted_perimeter,
                    'slope': slope,
                    'manning_n': manning_n
                }
        
        elif calc_type == 'effective_stress':
            # 16. Pressão Efetiva (σ' = σ - u)
            total_stress = float(request.form.get('total_stress', 0))  # kPa
            pore_pressure = float(request.form.get('pore_pressure', 0))  # kPa
            
            if total_stress:
                effective_stress = total_stress - pore_pressure
                
                results['effective_stress'] = {
                    'effective_stress': effective_stress,
                    'total_stress': total_stress,
                    'pore_pressure': pore_pressure
                }
        
        elif calc_type == 'terzaghi_bearing':
            # 17. Capacidade de Carga Terzaghi (q_ult = c⋅Nc + γ⋅Df⋅Nq + 0.5⋅γ⋅B⋅Nγ)
            cohesion = float(request.form.get('cohesion', 0))  # kPa
            unit_weight = float(request.form.get('unit_weight', 18))  # kN/m³
            depth = float(request.form.get('depth', 1))  # m
            width = float(request.form.get('width', 1))  # m
            friction_angle = float(request.form.get('friction_angle', 30))  # graus
            
            if friction_angle:
                phi_rad = math.radians(friction_angle)
                
                # Fatores de capacidade de carga de Terzaghi
                Nq = math.exp(math.pi * math.tan(phi_rad)) * (math.tan(math.pi/4 + phi_rad/2))**2
                Nc = (Nq - 1) / math.tan(phi_rad) if friction_angle > 0 else 5.14
                Ng = 2 * (Nq - 1) * math.tan(phi_rad)
                
                # Capacidade de carga última
                q_ult = cohesion * Nc + unit_weight * depth * Nq + 0.5 * unit_weight * width * Ng
                
                results['terzaghi_bearing'] = {
                    'ultimate_bearing_capacity': q_ult,
                    'Nc': Nc,
                    'Nq': Nq,
                    'Ng': Ng,
                    'cohesion': cohesion,
                    'unit_weight': unit_weight,
                    'depth': depth,
                    'width': width,
                    'friction_angle': friction_angle
                }
        
        elif calc_type == 'elastic_settlement':
            # 18. Assentamento Elástico (S = q⋅B(1-ν²)/E)
            bearing_pressure = float(request.form.get('bearing_pressure', 0))  # kPa
            foundation_width = float(request.form.get('foundation_width', 0))  # m
            poisson_ratio = float(request.form.get('poisson_ratio', 0.3))  # adimensional
            elastic_modulus = float(request.form.get('elastic_modulus', 0))  # kPa
            
            if bearing_pressure and foundation_width and elastic_modulus:
                settlement = (bearing_pressure * foundation_width * (1 - poisson_ratio**2)) / elastic_modulus
                settlement_mm = settlement * 1000  # converter para mm
                
                results['elastic_settlement'] = {
                    'settlement_m': settlement,
                    'settlement_mm': settlement_mm,
                    'bearing_pressure': bearing_pressure,
                    'foundation_width': foundation_width,
                    'poisson_ratio': poisson_ratio,
                    'elastic_modulus': elastic_modulus
                }
        
        elif calc_type == 'specific_weight':
            # 19. Peso Específico (γ = P/V)
            weight = float(request.form.get('weight', 0))  # N
            volume = float(request.form.get('volume', 0))  # m³
            
            if weight and volume:
                specific_weight = weight / volume  # N/m³
                specific_weight_knm3 = specific_weight / 1000  # kN/m³
                
                results['specific_weight'] = {
                    'specific_weight_nm3': specific_weight,
                    'specific_weight_knm3': specific_weight_knm3,
                    'weight': weight,
                    'volume': volume
                }
        
        elif calc_type == 'concrete_volume':
            # 20. Volume de Concreto (V = b⋅h⋅l)
            base = float(request.form.get('base', 0))  # m
            height = float(request.form.get('height', 0))  # m
            length = float(request.form.get('length', 0))  # m
            
            if base and height and length:
                volume = base * height * length  # m³
                volume_liters = volume * 1000  # litros
                
                results['concrete_volume'] = {
                    'volume_m3': volume,
                    'volume_liters': volume_liters,
                    'base': base,
                    'height': height,
                    'length': length
                }
    
    return render_template('calculators/material_resistance.html', results=results)

@calculators_bp.route('/civil-engineering-formulas', methods=['GET', 'POST'])
@login_required
def civil_engineering_formulas():
    """Fórmulas de Engenharia Civil - 20 Fórmulas Organizadas por Categoria"""
    results = {}
    
    if request.method == 'POST':
        calc_type = request.form.get('calc_type')
        
        # ESTRUTURAS E RESISTÊNCIA DOS MATERIAIS
        if calc_type == 'normal_stress':
            # 1. Tensão Normal (σ = F/A)
            force = float(request.form.get('force', 0))  # N
            area = float(request.form.get('area', 0))  # m²
            
            if force and area:
                normal_stress = force / area  # Pa
                normal_stress_mpa = normal_stress / 1000000  # MPa
                
                results['normal_stress'] = {
                    'stress_pa': normal_stress,
                    'stress_mpa': normal_stress_mpa,
                    'force': force,
                    'area': area
                }
        
        elif calc_type == 'deformation':
            # 2. Deformação (ε = ΔL/L₀)
            delta_length = float(request.form.get('delta_length', 0))  # m
            initial_length = float(request.form.get('initial_length', 0))  # m
            
            if initial_length:
                deformation = delta_length / initial_length
                deformation_percent = deformation * 100
                
                results['deformation'] = {
                    'deformation': deformation,
                    'deformation_percent': deformation_percent,
                    'delta_length': delta_length,
                    'initial_length': initial_length
                }
        
        elif calc_type == 'hooke_law':
            # 3. Lei de Hooke (σ = E⋅ε)
            elastic_modulus = float(request.form.get('elastic_modulus', 0))  # Pa
            strain = float(request.form.get('strain', 0))
            
            if elastic_modulus and strain:
                stress = elastic_modulus * strain  # Pa
                stress_mpa = stress / 1000000  # MPa
                
                results['hooke_law'] = {
                    'stress_pa': stress,
                    'stress_mpa': stress_mpa,
                    'elastic_modulus': elastic_modulus,
                    'strain': strain
                }
        
        elif calc_type == 'bending_moment':
            # 4. Momento Fletor (M = F⋅d)
            force = float(request.form.get('force', 0))  # N
            distance = float(request.form.get('distance', 0))  # m
            
            if force and distance:
                moment = force * distance  # N.m
                
                results['bending_moment'] = {
                    'moment': moment,
                    'force': force,
                    'distance': distance
                }
        
        elif calc_type == 'moment_inertia':
            # 5. Inércia da Seção (I = b⋅h³/12)
            base = float(request.form.get('base', 0))  # m
            height = float(request.form.get('height', 0))  # m
            
            if base and height:
                inertia = (base * height**3) / 12  # m⁴
                
                results['moment_inertia'] = {
                    'inertia': inertia,
                    'base': base,
                    'height': height
                }
        
        elif calc_type == 'bending_stress':
            # 6. Tensão de Flexão (σf = M⋅y/I)
            moment = float(request.form.get('moment', 0))  # N.m
            distance_centroid = float(request.form.get('distance_centroid', 0))  # m
            moment_inertia = float(request.form.get('moment_inertia', 0))  # m⁴
            
            if moment and distance_centroid and moment_inertia:
                bending_stress = (moment * distance_centroid) / moment_inertia  # Pa
                bending_stress_mpa = bending_stress / 1000000  # MPa
                
                results['bending_stress'] = {
                    'stress_pa': bending_stress,
                    'stress_mpa': bending_stress_mpa,
                    'moment': moment,
                    'distance_centroid': distance_centroid,
                    'moment_inertia': moment_inertia
                }
        
        elif calc_type == 'shear_stress':
            # 7. Cisalhamento (τ = V/A)
            shear_force = float(request.form.get('shear_force', 0))  # N
            area = float(request.form.get('area', 0))  # m²
            
            if shear_force and area:
                shear_stress = shear_force / area  # Pa
                shear_stress_mpa = shear_stress / 1000000  # MPa
                
                results['shear_stress'] = {
                    'stress_pa': shear_stress,
                    'stress_mpa': shear_stress_mpa,
                    'shear_force': shear_force,
                    'area': area
                }
        
        # CONCRETO E ARGAMASSAS
        elif calc_type == 'concrete_fck':
            # 8. Resistência Característica do Concreto (fck = Fruptura/A)
            rupture_force = float(request.form.get('rupture_force', 0))  # N
            area = float(request.form.get('area', 0))  # m²
            
            if rupture_force and area:
                fck = rupture_force / area  # Pa
                fck_mpa = fck / 1000000  # MPa
                
                results['concrete_fck'] = {
                    'fck_pa': fck,
                    'fck_mpa': fck_mpa,
                    'rupture_force': rupture_force,
                    'area': area
                }
        
        elif calc_type == 'mortar_dosage':
            # 9. Dosagem de Argamassa (Traço 1:a:b)
            cement = float(request.form.get('cement', 1))
            sand_ratio = float(request.form.get('sand_ratio', 3))
            aggregate_ratio = float(request.form.get('aggregate_ratio', 0))
            
            sand = cement * sand_ratio
            aggregate = cement * aggregate_ratio
            
            results['mortar_dosage'] = {
                'cement': cement,
                'sand': sand,
                'aggregate': aggregate,
                'ratio': f"1:{sand_ratio}:{aggregate_ratio}" if aggregate_ratio else f"1:{sand_ratio}"
            }
        
        elif calc_type == 'abrams_law':
            # 10. Lei de Abrams (fc = K⋅(a/c)^-n)
            k_constant = float(request.form.get('k_constant', 200))
            water_cement_ratio = float(request.form.get('water_cement_ratio', 0.5))
            n_exponent = float(request.form.get('n_exponent', 2))
            
            if k_constant and water_cement_ratio and n_exponent:
                concrete_strength = k_constant * (water_cement_ratio ** (-n_exponent))
                
                results['abrams_law'] = {
                    'concrete_strength': concrete_strength,
                    'k_constant': k_constant,
                    'water_cement_ratio': water_cement_ratio,
                    'n_exponent': n_exponent
                }
        
        # HIDRÁULICA E HIDROLOGIA
        elif calc_type == 'flow_rate':
            # 11. Vazão (Q = A⋅v)
            area = float(request.form.get('area', 0))  # m²
            velocity = float(request.form.get('velocity', 0))  # m/s
            
            if area and velocity:
                flow_rate = area * velocity  # m³/s
                
                results['flow_rate'] = {
                    'flow_rate': flow_rate,
                    'area': area,
                    'velocity': velocity
                }
        
        elif calc_type == 'continuity_equation':
            # 12. Equação da Continuidade (A₁⋅v₁ = A₂⋅v₂)
            area1 = float(request.form.get('area1', 0))  # m²
            velocity1 = float(request.form.get('velocity1', 0))  # m/s
            area2 = float(request.form.get('area2', 0))  # m²
            
            if area1 and velocity1 and area2:
                velocity2 = (area1 * velocity1) / area2  # m/s
                
                results['continuity_equation'] = {
                    'area1': area1,
                    'velocity1': velocity1,
                    'area2': area2,
                    'velocity2': velocity2
                }
        
        elif calc_type == 'bernoulli_equation':
            # 13. Equação de Bernoulli (p/γ + v²/2g + z = constante)
            pressure1 = float(request.form.get('pressure1', 0))  # Pa
            velocity1 = float(request.form.get('velocity1', 0))  # m/s
            elevation1 = float(request.form.get('elevation1', 0))  # m
            pressure2 = float(request.form.get('pressure2', 0))  # Pa
            velocity2 = float(request.form.get('velocity2', 0))  # m/s
            elevation2 = float(request.form.get('elevation2', 0))  # m
            specific_weight = float(request.form.get('specific_weight', 9810))  # N/m³
            
            g = 9.81  # m/s²
            
            # Carga total nos pontos
            head1 = pressure1/specific_weight + (velocity1**2)/(2*g) + elevation1
            head2 = pressure2/specific_weight + (velocity2**2)/(2*g) + elevation2
            
            results['bernoulli_equation'] = {
                'head1': head1,
                'head2': head2,
                'head_loss': abs(head1 - head2),
                'pressure1': pressure1,
                'velocity1': velocity1,
                'elevation1': elevation1,
                'pressure2': pressure2,
                'velocity2': velocity2,
                'elevation2': elevation2
            }
        
        elif calc_type == 'reynolds_number':
            # 14. Número de Reynolds (Re = ρ⋅v⋅D/μ)
            density = float(request.form.get('density', 1000))  # kg/m³
            velocity = float(request.form.get('velocity', 0))  # m/s
            diameter = float(request.form.get('diameter', 0))  # m
            viscosity = float(request.form.get('viscosity', 0.001))  # Pa.s
            
            if velocity and diameter and viscosity:
                reynolds = (density * velocity * diameter) / viscosity
                
                if reynolds < 2300:
                    flow_type = "Laminar"
                elif reynolds > 4000:
                    flow_type = "Turbulento"
                else:
                    flow_type = "Transição"
                
                results['reynolds_number'] = {
                    'reynolds': reynolds,
                    'flow_type': flow_type,
                    'density': density,
                    'velocity': velocity,
                    'diameter': diameter,
                    'viscosity': viscosity
                }
        
        elif calc_type == 'manning_formula':
            # 15. Fórmula de Manning (Q = 1/n⋅A⋅R^(2/3)⋅S^(1/2))
            area = float(request.form.get('area', 0))  # m²
            wetted_perimeter = float(request.form.get('wetted_perimeter', 0))  # m
            slope = float(request.form.get('slope', 0))  # m/m
            manning_n = float(request.form.get('manning_n', 0.013))
            
            if area and wetted_perimeter and slope and manning_n:
                hydraulic_radius = area / wetted_perimeter
                flow_rate = (1/manning_n) * area * (hydraulic_radius**(2/3)) * (slope**0.5)
                
                results['manning_formula'] = {
                    'flow_rate': flow_rate,
                    'hydraulic_radius': hydraulic_radius,
                    'area': area,
                    'wetted_perimeter': wetted_perimeter,
                    'slope': slope,
                    'manning_n': manning_n
                }
        
        # GEOTECNIA E FUNDAÇÕES
        elif calc_type == 'effective_stress':
            # 16. Pressão Efetiva (σ' = σ - u)
            total_stress = float(request.form.get('total_stress', 0))  # Pa
            pore_pressure = float(request.form.get('pore_pressure', 0))  # Pa
            
            effective_stress = total_stress - pore_pressure
            
            results['effective_stress'] = {
                'effective_stress': effective_stress,
                'total_stress': total_stress,
                'pore_pressure': pore_pressure
            }
        
        elif calc_type == 'terzaghi_bearing':
            # 17. Capacidade de Carga (Terzaghi)
            cohesion = float(request.form.get('cohesion', 0))  # Pa
            unit_weight = float(request.form.get('unit_weight', 18000))  # N/m³
            depth = float(request.form.get('depth', 1))  # m
            width = float(request.form.get('width', 1))  # m
            friction_angle = float(request.form.get('friction_angle', 30))  # graus
            
            if friction_angle:
                phi_rad = math.radians(friction_angle)
                
                # Fatores de capacidade de carga
                Nq = math.exp(math.pi * math.tan(phi_rad)) * (math.tan(math.pi/4 + phi_rad/2))**2
                Nc = (Nq - 1) / math.tan(phi_rad) if friction_angle > 0 else 5.14
                Ng = 2 * (Nq - 1) * math.tan(phi_rad)
                
                # Capacidade de carga última
                q_ult = cohesion * Nc + unit_weight * depth * Nq + 0.5 * unit_weight * width * Ng
                
                results['terzaghi_bearing'] = {
                    'ultimate_capacity': q_ult,
                    'Nc': Nc,
                    'Nq': Nq,
                    'Ng': Ng,
                    'cohesion': cohesion,
                    'unit_weight': unit_weight,
                    'depth': depth,
                    'width': width,
                    'friction_angle': friction_angle
                }
        
        elif calc_type == 'elastic_settlement':
            # 18. Assentamento Elástico (S = q⋅B(1-ν²)/E)
            bearing_pressure = float(request.form.get('bearing_pressure', 0))  # Pa
            width = float(request.form.get('width', 0))  # m
            poisson_ratio = float(request.form.get('poisson_ratio', 0.3))
            elastic_modulus = float(request.form.get('elastic_modulus', 0))  # Pa
            
            if bearing_pressure and width and elastic_modulus:
                settlement = (bearing_pressure * width * (1 - poisson_ratio**2)) / elastic_modulus
                
                results['elastic_settlement'] = {
                    'settlement': settlement,
                    'bearing_pressure': bearing_pressure,
                    'width': width,
                    'poisson_ratio': poisson_ratio,
                    'elastic_modulus': elastic_modulus
                }
        
        # CONSTRUÇÃO E MATERIAIS
        elif calc_type == 'specific_weight':
            # 19. Peso Específico (γ = P/V)
            weight = float(request.form.get('weight', 0))  # N
            volume = float(request.form.get('volume', 0))  # m³
            
            if weight and volume:
                specific_weight = weight / volume  # N/m³
                
                results['specific_weight'] = {
                    'specific_weight': specific_weight,
                    'weight': weight,
                    'volume': volume
                }
        
        elif calc_type == 'concrete_volume':
            # 20. Volume de Concreto (V = b⋅h⋅l)
            base = float(request.form.get('base', 0))  # m
            height = float(request.form.get('height', 0))  # m
            length = float(request.form.get('length', 0))  # m
            
            if base and height and length:
                volume = base * height * length  # m³
                
                results['concrete_volume'] = {
                    'volume': volume,
                    'base': base,
                    'height': height,
                    'length': length
                }
    
    return render_template('calculators/civil_engineering_formulas.html', results=results)