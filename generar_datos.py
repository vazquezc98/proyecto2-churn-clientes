"""
Genera el dataset sintético clientes_churn.csv con 500 filas.

Columnas:
- id_cliente: identificador único del cliente (C001..C500).
- antigüedad_meses: tiempo de permanencia en meses (entero, 0-120).
- plan: tipo de plan (Básico, Estándar, Premium).
- soporte_tecnico_usado: uso de soporte técnico (Sí/No).
- costo_mensual: cargo mensual (float).
- cancelado_si_no: variable objetivo, canceló el servicio (Sí/No).

Se introduce una correlación realista con la fuga (churn):
  - Menor antigüedad -> mayor probabilidad de cancelar.
  - Plan Básico y costo alto relativo -> mayor probabilidad de cancelar.
  - Uso frecuente de soporte técnico -> mayor probabilidad de cancelar.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

N = 500

# Identificadores de cliente
id_cliente = [f"C{i:03d}" for i in range(1, N + 1)]

# Antigüedad en meses (distribución sesgada hacia clientes nuevos)
antigüedad_meses = np.random.exponential(scale=24, size=N).astype(int)
antigüedad_meses = np.clip(antigüedad_meses, 0, 120)

# Plan (distribución desbalanceada: más clientes en Básico y Estándar)
plan = np.random.choice(
    ["Básico", "Estándar", "Premium"], size=N, p=[0.45, 0.40, 0.15]
)

# Soporte técnico usado (Sí/No)
soporte_tecnico_usado = np.random.choice(["Sí", "No"], size=N, p=[0.35, 0.65])

# Costo mensual según plan (con ruido)
costo_base = {"Básico": 25.0, "Estándar": 45.0, "Premium": 75.0}
costo_mensual = np.array([costo_base[p] for p in plan]) + np.random.normal(
    loc=0.0, scale=5.0, size=N
)
costo_mensual = np.round(np.clip(costo_mensual, 10, None), 2)

# Variable objetivo: cancelado_si_no (Sí/No)
# Modelo logístico simple para inducir correlación realista con churn
logit = (
    -2.5
    - 0.03 * antigüedad_meses          # menos antigüedad, más churn
    + 0.6 * (plan == "Básico").astype(int)   # plan básico, más churn
    + 0.2 * (plan == "Estándar").astype(int)
    + 0.5 * (soporte_tecnico_usado == "Sí").astype(int)  # soporte, más churn
    + 0.02 * (costo_mensual - 45)      # costo por encima del promedio, más churn
)
prob_cancelar = 1 / (1 + np.exp(-logit))
cancelado_si_no = np.random.binomial(1, prob_cancelar).astype(int)
cancelado_si_no = np.where(cancelado_si_no == 1, "Sí", "No")

df = pd.DataFrame(
    {
        "id_cliente": id_cliente,
        "antigüedad_meses": antigüedad_meses,
        "plan": plan,
        "soporte_tecnico_usado": soporte_tecnico_usado,
        "costo_mensual": costo_mensual,
        "cancelado_si_no": cancelado_si_no,
    }
)

# Mezclar filas para evitar orden por antigüedad
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Re-asignar ids ordenados después del shuffle para mantener unicidad
df["id_cliente"] = [f"C{i:03d}" for i in range(1, N + 1)]

df.to_csv("clientes_churn.csv", index=False, encoding="utf-8")

print(f"Se generaron {len(df)} filas en clientes_churn.csv")
print("\nDistribución de cancelado_si_no:")
print(df["cancelado_si_no"].value_counts(normalize=True).mul(100).round(2))
print("\nPrimeras 5 filas:")
print(df.head())
