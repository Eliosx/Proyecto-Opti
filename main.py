import pandas as pd
from gurobipy import Model, GRB
from itertools import product # <- No está en el enunciado pero viene instalada con python. Solo permite hacer más operaciones con los iterables.

modelo = Model("entrega 3 proyecto")

# # Conjuntos
# 

cantidad_terrenos = 2            # Definir
K = [k for k in range(cantidad_terrenos)]
J = [j for j in range(7)]  # <------------------------ Los indices empiezan en 0. Ojo con la interpretación
JPaneles = [0, 1]
JMolinos = [2, 3]
JProductores = JPaneles + JMolinos
JBaterias = [4,5,6]

T = [t for t in range(50)]   
Z = [z for z in range(7)] # Simulación de una semana
# # Variables

U = modelo.addVars(K, J, T, lb=0, vtype=GRB.INTEGER, name="U")
X = modelo.addVars(K, T, lb=0, vtype=GRB.BINARY, name="X")
SProduciendo = modelo.addVars(K, J, T, lb=0, vtype=GRB.INTEGER, name="SProduciendo")
SContruccion = modelo.addVars(K, J, T, lb=0, vtype=GRB.INTEGER, name="SContruccion")
Beta = modelo.addVars(T, Z, lb=0, vtype=GRB.CONTINUOUS, name="Beta")
# # Parametros
# Debemos rellenar estos datos

class SolarPequeña:
    def __init__(self):
        self.precioInstalacion = 718_867.92 # Valor real
        self.emisionCO2 = 40 #gCO2/kWh
        self.espacioUtilizado = 1000
        self.distanciaMinimaAHogar = 0 # No se necesita distancia mínima
        self.produccionEnergiaPorTerreno = [1_327_000, 1_327_000]  # Un valor por cada terreno
        self.MinimoDeAlmacenamientoDeBaterias = 0.6 # Valor real
        self.vidaUtil = 30 # Valor real

class SolarGrande:
    def __init__(self):
        self.precioInstalacion = 906_603.77 # Valor real
        self.emisionCO2 = 40 #gCO2/kWh
        self.espacioUtilizado = 21670
        self.distanciaMinimaAHogar = 0 # No se necesita distancia mínima
        self.produccionEnergiaPorTerreno = [39_814_000, 39_814_000]
        self.MinimoDeAlmacenamientoDeBaterias = 0.5 # Valor real
        self.vidaUtil = 30 # Valor real

class EolicaPequeña:
    def __init__(self):
        self.precioInstalacion = 1_152_830.19 # Valor real
        self.emisionCO2 = 5.3 #gCO2/kWh
        self.espacioUtilizado = 162_000 # Valor real
        self.distanciaMinimaAHogar = 500 # Valor real
        self.produccionEnergiaPorTerreno = [3_500_000, 2_750_000]
        self.MinimoDeAlmacenamientoDeBaterias = 0.5 # Valor real
        self.vidaUtil = 30 # Valor real

class EolicaGrande:
    def __init__(self):
        self.precioInstalacion = 1_409_433.96 # Valor real
        self.emisionCO2 = 5.3 #gCO2/kWh
        self.espacioUtilizado = 202_500 # Valor real
        self.distanciaMinimaAHogar = 500 # Valor real
        self.produccionEnergiaPorTerreno = [17_000_000, 13_500_000]
        self.MinimoDeAlmacenamientoDeBaterias = 0.4 # Valor real
        self.vidaUtil = 25 # Valor real

class BateriaLitio:
    def __init__(self):
        self.precioInstalacion = 1_467_924.53 # Valor real
        self.emisionCO2 = 168_000 #gCO2/kWh
        self.espacioUtilizado = 0.3
        self.capacidadMaximaAlmacenada = 230 # Valor real
        self.vidaUtil = 20  # Valor real

class BateriaPlomoAcido:
    def __init__(self):
        self.precioInstalacion = 1_603_773.58 # Valor real
        self.emisionCO2 = 175_000 #gCO2/kWh
        self.espacioUtilizado = 5.74
        self.capacidadMaximaAlmacenada = 1.2 # Valor real
        self.vidaUtil = 15 # Valor real

class BateriaFlujo:
    def __init__(self):
        self.precioInstalacion = 1_037_735.85 # Valor real
        self.emisionCO2 = 183_000 #gCO2/kWh
        self.espacioUtilizado = 13.74
        self.capacidadMaximaAlmacenada = 800 # Valor real
        self.vidaUtil = 20 # Valor real


Infraestructuras : list[SolarPequeña] = [SolarPequeña(), SolarGrande(), EolicaPequeña(), EolicaGrande(), BateriaLitio(), BateriaPlomoAcido(), BateriaFlujo()] 

class Terreno:
    def __init__(self, precioArriendo, tamaño, distanciaAHogar):
        self.precioArriendo : int = precioArriendo
        self.tamaño : int = tamaño
        self.distanciaAHogar : int = distanciaAHogar



Terrenos = [Terreno(precioArriendo=2_981_132.07, tamaño=10_000_000, distanciaAHogar=500), # Poniente
            Terreno(precioArriendo=2_062_264.15, tamaño=10_000_000, distanciaAHogar=500)] # Oriente


class Simulacion:
    def __init__(self):
        # 7 días de simulación
        self.demandaSimulada = [481_442.96, 449_786.83, 421_593.05, 421_593.05, 481_442.96, 421_593.05, 421_593.05] # Nublado, Parcialmente nublado, Soleado, Parcialemente Nublado, Nublado, Soleado, Soleado
        # Matriz 7x7 (infraestructuras x días)
        self.disminucionProduccion = [
            [0.3325, 0.762, 1.0, 0.762, 0.3325, 1.0, 1.0],  # 0: Solar pequeña
            [0.3325, 0.762, 1.0, 0.762, 0.3325, 1.0, 1.0], # 1: Solar grande
            [0.3, 0.6, 1.0, 0.6, 0.3, 1.0, 1.0],    # 2: Eólica pequeña
            [0.55, 0.8, 1.0, 0.8, 0.55, 1.0, 1.0], # 3: Eólica grande
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],      # 4: Batería litio
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],      # 5: Batería plomo ácido
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]       # 6: Batería flujo
        ]

simulacion = Simulacion()


demandaElectricaAñoInicial = 158_314_691 # Parametro real
aumentoDemandaAnual = 1.0339 # Parametro real

# Costos y emisiones
p = [i.precioInstalacion for i in Infraestructuras]
c = [i.emisionCO2 for i in Infraestructuras]
p_arriendo = [t.precioArriendo for t in Terrenos]
q_presupuesto = 3_266_037_735.29

# Caracteristicas fisicas y operativas

e = [i.espacioUtilizado for i in Infraestructuras]
t_area = [t.tamaño for t in Terrenos]
t_dist_hogares = [t.distanciaAHogar for t in Terrenos]
h_vida = [i.vidaUtil for i in Infraestructuras]

w = {(j,k): Infraestructuras[j].produccionEnergiaPorTerreno[k] for (j, k) in product(JProductores,K)}

t_distancia_correcta= {(k,i): int(Terrenos[k].distanciaAHogar - Infraestructuras[i].distanciaMinimaAHogar >= 0)  for (k,i) in product(K, JProductores)}
gamma = {(j,z): simulacion.disminucionProduccion[j][z] for (j,z) in product(J, Z)}


# Demanda y almacenamiento

d = [demandaElectricaAñoInicial * (aumentoDemandaAnual ** t) for t in T]
a = simulacion.demandaSimulada
v_guardada = [Infraestructuras[i].MinimoDeAlmacenamientoDeBaterias for i in JProductores]
b = { i: Infraestructuras[i].capacidadMaximaAlmacenada for i in JBaterias}

M = 1e16
# # Función objetivo

modelo.setObjective(
    sum(U[k,j,t] * c[j]
        for (k,j,t) in product(K,J,T)),
    GRB.MINIMIZE
)
# # Restricciones
# 
# 1) # MODIFICADA (CAMBIAR EN EL INFORME)

for k, j, t in product(K, J, T):
    if t == 0:
        modelo.addConstr(SProduciendo[k,j,t] == 0, name=f"prod_inicial_{k}_{j}_{t}")
    else:
        # Solo considerar construcciones que están dentro de su vida útil
        modelo.addConstr(
            SProduciendo[k,j,t] == sum(
                U[k,j,tt] for tt in range(max(0, t - h_vida[j] + 1), t + 1)
                if (t - tt) < h_vida[j] and (t - tt) >= 0
            ),
            name=f"prod_operativa_{k}_{j}_{t}"
        )
# 2)

modelo.addConstrs(
    (
        SContruccion[k,j,t] == U[k,j,t]
        for (k,j,t) in product(K,J,T)
    ),
    name="2)"
    )
# 3) 

modelo.addConstrs(
    (
        sum((SProduciendo[k, j, t] + SContruccion[k, j, t]) * e[j] for j in J)
        <= t_area[k]
        for k, t in product(K, T)
    ),
    name="3"
)
# 4) # Agregue un for k in K porque estamos sumando sobre todos los terrenos y en 
# la restriccion original no se hacia eso porque la demanda era de la localidad 
# no del terreno.
# if t>=1 agregado

modelo.addConstrs(
    (
    sum(SProduciendo[k,j,t] * w[j,k] for k in K for j in JProductores) >= d[t]
        for t in T if t >= 1
    ),
    name="4)"
)

# 5) 

modelo.addConstrs(
    (
        sum(SProduciendo[k,j,t] + SContruccion[k,j,t] for j in J)
        <= M * X[k,t]
        for (k,t) in product(K,T)
    ),
    name="5)"
)
# 6. # if t>=1 agregado

modelo.addConstrs(
    (
        sum(b[j] * SProduciendo[k,j,t] for j in JBaterias) >=
        sum(SProduciendo[k,j,t] * w[j,k] * v_guardada[j] for j in JProductores)/365
        for (k,t) in product(K, T) if t >= 1
    ),
    name="6)"
)



# 7)

modelo.addConstrs(
    (
        SProduciendo[k,j,t] + SContruccion[k,j,t] 
        <= M * t_distancia_correcta[k,j]
        for (k,j,t) in product(K, JMolinos, T)
    ),
    name="7)"
)
# 8) 

modelo.addConstr(
    sum(U[k,j,t] * p[j] for (k,j,t) in product(K,J,T)) +
    sum(X[k,t] * p_arriendo[k] for (k,t) in product(K,T))
    <= q_presupuesto,
    name="8)"
)
# 9)

modelo.addConstrs(
    (
        Beta[t,z] 
        <= sum(SProduciendo[k,j,t] * b[j] for (k,j) in product(K,JBaterias))
        for (t,z) in product(T, Z)
    ),
    name="9a)"
)

modelo.addConstrs(
    (
        Beta[t,z] >= 0
        for (t,z) in product(T, Z)
    ),
    name="9b)"
)
# 10) 
# if t>=1 agregado

modelo.addConstrs(
    (
        sum(Beta[t,z] for z in Z) >= 0.05 * sum(SProduciendo[k,j,t] * b[j] for k in K for j in JBaterias) * len(Z)
        for t in T if t >= 1
    ),
    name="almacenamiento_promedio_minimo_suave"
)

# 3. Restricción de máximo más realista
modelo.addConstrs(
    (
        Beta[t,z+1] <= 0.98 * (  # 98% de eficiencia (más realista)
            Beta[t,z] +
            sum(SProduciendo[k,j,t] * w[j,k] * gamma[j,z] for (k,j) in product(K, JProductores)) / 365
            - a[z]
        )
        for (t,z) in product(T, [0,1,2,3,4,5]) if t >= 1
    ),
    name="10_con_perdidas_suave"
)

# 11) 

modelo.addConstrs(
    (
        Beta[t,1] == 0 for t in T
    ),
    name="11)"
)
# 12
# if t>=1 agregado

modelo.addConstrs(
    (
        sum(SProduciendo[k,j,t] * w[j,k] for (k,j) in product(K, JPaneles)) -
        sum(SProduciendo[k,j,t] * w[j,k] for (k,j) in product(K, JProductores)) * 0.3 >= 0
        for t in T if t >= 1
    ),
    name="12a)"
)

modelo.addConstrs(
    (
        sum(SProduciendo[k,j,t] * w[j,k] for (k,j) in product(K, JMolinos)) -
        sum(SProduciendo[k,j,t] * w[j,k] for (k,j) in product(K, JProductores)) * 0.3 >= 0
        for t in T if t >= 1
    ),
    name="12b)"
)
# 13) # if t>=1 agregado 

modelo.addConstrs(
    (
        a[z] <= 
        Beta[t,z] +
        sum(SProduciendo[k,j,t] * w[j,k] * gamma[j,z] for (k,j) in product(K,JProductores)) / 365
        for (z,t) in product(Z,T)  if t>=1
    ),
    name="13)"
)

modelo.optimize()

if modelo.status == GRB.OPTIMAL:
    # Crear y abrir archivo para escribir todos los resultados
    with open('resultados_completos.txt', 'w', encoding='utf-8') as f:
        # Escribir diagnóstico detallado
        f.write("🔍 DIAGNÓSTICO DETALLADO - AÑO 25 (CUANDO SE VACÍAN LAS BATERÍAS)\n")
        f.write("-" * 60 + "\n")
        
        t_problema = 25
        
        # 1. Capacidad disponible
        capacidad_total = sum(SProduciendo[k,j,t_problema].x * b[j] 
                             for k in K for j in JBaterias)
        f.write(f"Capacidad total baterías: {capacidad_total:,.0f} kWh\n")
        
        # 2. Requerimiento mínimo por restricción 6
        requerimiento_minimo = sum(SProduciendo[k,j,t_problema].x * w[j,k] * v_guardada[j] 
                                  for k in K for j in JProductores) / 365
        f.write(f"Requerimiento mínimo (restricción 6): {requerimiento_minimo:,.0f} kWh\n")
        
        # 3. Producción vs Demanda
        produccion_diaria = sum(SProduciendo[k,j,t_problema].x * w[j,k] 
                               for k in K for j in JProductores) / 365
        demanda_diaria = d[t_problema] / 365
        f.write(f"Producción diaria: {produccion_diaria:,.0f} kWh\n")
        f.write(f"Demanda diaria: {demanda_diaria:,.0f} kWh\n")
        f.write(f"Exceso: {produccion_diaria - demanda_diaria:,.0f} kWh\n")
        
        # 4. Estado de las baterías
        for z in Z:
            beta_val = Beta[t_problema, z].x
            f.write(f"Día {z}: Energía almacenada = {beta_val:,.0f} kWh\n")

        f.write(f"Valor óptimo (emisiones totales de CO2): {modelo.objVal:.2f} unidades\n")
        
        # =============================================================================
        # SECCIÓN DE VISUALIZACIÓN DE RESULTADOS
        # =============================================================================
        
        f.write("\n" + "="*80 + "\n")
        f.write("ANÁLISIS COMPLETO DE RESULTADOS\n")
        f.write("="*80 + "\n")
        
        # 1. RESUMEN EJECUTIVO
        f.write("\nRESUMEN EJECUTIVO\n")
        f.write("-" * 50 + "\n")
        
        # Calcular métricas clave
        total_inversion = sum(U[k,j,t].x * p[j] for k in K for j in J for t in T)
        total_emisiones = modelo.objVal/1000  # Convertir gCO2 a kgCO2
        total_arriendo = sum(X[k,t].x * p_arriendo[k] for k in K for t in T)
        
        f.write(f"• Inversión total: ${total_inversion:,.0f} pesos\n")
        f.write(f"• Costo arriendo total: ${total_arriendo:,.0f} pesos\n")
        f.write(f"• Emisiones totales de CO2: {total_emisiones:,.0f} kgCO2/kWh\n")
        f.write(f"• Presupuesto utilizado: {(total_inversion + total_arriendo)/q_presupuesto*100:.1f}%\n")

        
        # 2. INFRAESTRUCTURA CONSTRUIDA POR AÑO
        f.write("\nINFRAESTRUCTURA CONSTRUIDA POR AÑO\n")
        f.write("-" * 50 + "\n")
        
        # Crear DataFrame para infraestructura construida
        construccion_data = []
        for t in T:
            fila = {'Año': t}
            for j in J:
                total_j = sum(U[k,j,t].x for k in K)
                nombre = ["Solar Peq", "Solar Gr", "Eólica Peq", "Eólica Gr", 
                            "Bat Litio", "Bat Plomo", "Bat Flujo"][j]
                fila[nombre] = total_j
            construccion_data.append(fila)
        
        df_construccion = pd.DataFrame(construccion_data)
        f.write(df_construccion.to_string(index=False) + "\n")
        
        # 3. INFRAESTRUCTURA EN OPERACIÓN POR AÑO
        f.write("\n⚡ INFRAESTRUCTURA EN OPERACIÓN POR AÑO\n")
        f.write("-" * 50 + "\n")
        
        operacion_data = []
        for t in T:
            fila = {'Año': t}
            for j in J:
                total_j = sum(SProduciendo[k,j,t].x for k in K)
                nombre = ["Solar Peq", "Solar Gr", "Eólica Peq", "Eólica Gr", 
                            "Bat Litio", "Bat Plomo", "Bat Flujo"][j]
                fila[nombre] = total_j
            operacion_data.append(fila)
        
        df_operacion = pd.DataFrame(operacion_data)
        f.write(df_operacion.to_string(index=False) + "\n")
        
        # 4. PRODUCCIÓN DE ENERGÍA VS DEMANDA
        f.write("\n PRODUCCIÓN DE ENERGÍA VS DEMANDA\n")
        f.write("-" * 50 + "\n")
        
        energia_data = []
        for t in T:
                produccion_total = sum(SProduciendo[k,j,t].x * w.get((j,k), 0) 
                                     for k in K for j in JProductores)
                fila = {
                    'Año': t,
                    'Producción (kWh)': f"{produccion_total:,.0f}",
                    'Demanda (kWh)': f"{d[t]:,.0f}",
                    'Cumplimiento': f"{(produccion_total/d[t]*100) if d[t] > 0 else 0:.1f}%"
                }
                energia_data.append(fila)
        
        df_energia = pd.DataFrame(energia_data)
        f.write(df_energia.to_string(index=False) + "\n")
        
        # 5. USO DE TERRENOS
        f.write("\nUSO DE TERRENOS\n")
        f.write("-" * 50 + "\n")
        
        terreno_data = []
        for t in T:
                uso_0 = sum(SProduciendo[0,j,t].x + SContruccion[0,j,t].x for j in J)
                uso_1 = sum(SProduciendo[1,j,t].x + SContruccion[1,j,t].x for j in J)
                fila = {
                    'Año': t,
                    'Terreno 0 - Uso': f"{uso_0:,.0f} u.",
                    'Terreno 0 - Arrendado': 'Sí' if X[0,t].x > 0.5 else 'No',
                    'Terreno 1 - Uso': f"{uso_1:,.0f} u.", 
                    'Terreno 1 - Arrendado': 'Sí' if X[1,t].x > 0.5 else 'No'
                }
                terreno_data.append(fila)
        
        df_terrenos = pd.DataFrame(terreno_data)
        f.write(df_terrenos.to_string(index=False) + "\n")
        
        # 6. ALMACENAMIENTO EN BATERÍAS
        f.write("\nALMACENAMIENTO EN BATERÍAS (Día 1 de cada año)\n")
        f.write("-" * 50 + "\n")
        
        bateria_data = []
        for t in T:
                capacidad_total = sum(SProduciendo[k,j,t].x * b[j] 
                                    for k in K for j in JBaterias)
                energia_almacenada = Beta[t,0].x
                fila = {
                    'Año': t,
                    'Capacidad Total': f"{capacidad_total:,.0f} kWh",
                    'Energía Almacenada': f"{energia_almacenada:,.0f} kWh",
                    'Porcentaje Uso': f"{(energia_almacenada/capacidad_total*100) if capacidad_total > 0 else 0:.1f}%"
                }
                bateria_data.append(fila)
        
        df_baterias = pd.DataFrame(bateria_data)
        f.write(df_baterias.to_string(index=False) + "\n")
        
        # 7. ANÁLISIS DE DIVERSIFICACIÓN ENERGÉTICA
        f.write("\nDIVERSIFICACIÓN ENERGÉTICA (Año 10)\n")
        f.write("-" * 50 + "\n")
        
        t_analisis = 10
        prod_solar = sum(SProduciendo[k,j,t_analisis].x * w.get((j,k), 0) 
                        for k in K for j in JPaneles)
        prod_eolica = sum(SProduciendo[k,j,t_analisis].x * w.get((j,k), 0) 
                         for k in K for j in JMolinos)
        prod_total = prod_solar + prod_eolica
        
        f.write(f"• Producción Solar: {prod_solar:,.0f} kWh ({prod_solar/prod_total*100:.1f}%)\n")
        f.write(f"• Producción Eólica: {prod_eolica:,.0f} kWh ({prod_eolica/prod_total*100:.1f}%)\n")
        f.write(f"• Cumple diversificación (≥30% cada una): {'Si!' if prod_solar/prod_total >= 0.3 and prod_eolica/prod_total >= 0.3 else 'No'}\n")
        
        # 8. INVERSIÓN POR TIPO DE TECNOLOGÍA
        f.write("\nINVERSIÓN POR TIPO DE TECNOLOGÍA\n")
        f.write("-" * 50 + "\n")
        
        inversion_por_tipo = {}
        for j in J:
            total_j = sum(U[k,j,t].x * p[j] for k in K for t in T)
            nombre = ["Solar Peq", "Solar Gr", "Eólica Peq", "Eólica Gr", 
                     "Bat Litio", "Bat Flujo", "Bat Plomo"][j]
            inversion_por_tipo[nombre] = total_j
        
        for tech, inv in inversion_por_tipo.items():
            f.write(f"• {tech}: ${inv:,.0f} ({inv/total_inversion*100:.1f}%)\n")
        
        # 9. VERIFICACIÓN DE RESTRICCIONES CRÍTICAS
        f.write("\nVERIFICACIÓN DE FACTIBILIDAD\n")
        f.write("-" * 50 + "\n")
        
        # Verificar presupuesto
        costo_total = total_inversion + total_arriendo
        f.write(f"• Presupuesto: ${costo_total:,.0f} / ${q_presupuesto:,.0f}\n")
        
        # Verificar demanda en años clave
        for t_verificar in [3, 10, 15]:
            produccion = sum(SProduciendo[k,j,t_verificar].x * w.get((j,k), 0) 
                           for k in K for j in JProductores)
            f.write(f"• Año {t_verificar}: Producción {produccion:,.0f} ≥ Demanda {d[t_verificar]:,.0f}\n")
        
        # Verificar espacio en terrenos
        for k in K:
            for t_verificar in [0, 10, 15]:
                espacio_usado = sum((SProduciendo[k,j,t_verificar].x + SContruccion[k,j,t_verificar].x) * e[j] 
                                  for j in J)
                f.write(f"• Terreno {k}, Año {t_verificar}: {espacio_usado:,.0f}/{t_area[k]:,.0f} u²\n")
        
        # 10. RECOMENDACIONES
        f.write("\nRECOMENDACIONES ESTRATÉGICAS\n")
        f.write("-" * 50 + "\n")
        
        # Análisis de tecnologías preferidas
        construccion_total = {j: sum(U[k,j,t].x for k in K for t in T) for j in J}
        tech_preferida = max(construccion_total, key=construccion_total.get)
        nombres_tech = ["Solar Pequeña", "Solar Grande", "Eólica Pequeña", "Eólica Grande", 
                       "Batería Litio", "Batería Flujo", "Batería Plomo"]
        
        f.write(f"• Tecnología más construída: {nombres_tech[tech_preferida]}\n")
        f.write(f"• Total unidades: {construccion_total[tech_preferida]}\n")
        
        # Análisis de temporalidad
        años_primera_construccion = {}
        for j in J:
            for t in T:
                if any(U[k,j,t].x > 0 for k in K):
                    años_primera_construccion[j] = t
                    break
        
        f.write("• Años de primera construcción:\n")
        for j, año in años_primera_construccion.items():
            f.write(f"  - {nombres_tech[j]}: Año {año}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("ANÁLISIS COMPLETADO EXITOSAMENTE\n")
        f.write("="*80 + "\n")

    # También imprimir en consola que se guardó el archivo
    print("✅ Todos los resultados se han guardado en 'resultados_completos.txt'")
    
else:
    print("No se encontró solución óptima.")