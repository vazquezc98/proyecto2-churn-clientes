"""
Análisis Exploratorio de Datos (EDA) - Proyecto de Customer Churn

Lee clientes_churn.csv y produce:
  - Estadísticas descriptivas.
  - Tasas de churn por variable categórica y numérica (binned).
  - Detección de valores nulos y duplicados.
  - Visualizaciones guardadas en carpeta 'outputs/'.
  - Resumen exportado a clientes_churn_resumen.xlsx.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de visualización
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

INPUT_CSV = "clientes_churn.csv"
OUTPUT_DIR = "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def cargar_datos(ruta):
    df = pd.read_csv(ruta, encoding="utf-8")
    return df


def resumen_general(df):
    print("=" * 60)
    print("RESUMEN GENERAL DEL DATASET")
    print("=" * 60)
    print(f"Dimensiones (filas, columnas): {df.shape}")
    print(f"\nColumnas: {list(df.columns)}")
    print("\nTipos de datos:")
    print(df.dtypes)
    print("\nValores nulos por columna:")
    print(df.isnull().sum())
    print(f"\nFilas duplicadas: {df.duplicated().sum()}")
    print(f"\nClientes únicos (id_cliente): {df['id_cliente'].nunique()}")
    print("\nEstadísticas descriptivas (numéricas):")
    print(df.describe(include="number"))

    print("\n" + "=" * 60)
    print("VARIABLE OBJETIVO: cancelado_si_no")
    print("=" * 60)
    print(df["cancelado_si_no"].value_counts())
    print("\nProporción de churn:")
    print(df["cancelado_si_no"].value_counts(normalize=True).mul(100).round(2))

    return df


def analisis_categorico(df):
    print("\n" + "=" * 60)
    print("ANÁLISIS POR VARIABLES CATEGÓRICAS")
    print("=" * 60)

    for col in ["plan", "soporte_tecnico_usado"]:
        print(f"\n--- {col} ---")
        conteo = df[col].value_counts()
        print("Conteo absoluto:")
        print(conteo)
        print("\nTasa de churn por categoría:")
        tasa = (
            df.groupby(col)["cancelado_si_no"]
            .apply(lambda s: (s == "Sí").mean() * 100)
            .round(2)
        )
        print(tasa)

        # Gráfico de barras: tasa de churn por categoría
        plt.figure()
        tasa.sort_values().plot(kind="barh", color="steelblue", edgecolor="black")
        plt.title(f"Tasa de Churn (%) por {col}")
        plt.xlabel("Tasa de churn (%)")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"churn_por_{col}.png"), dpi=150)
        plt.close()

    return df


def analisis_numerico(df):
    print("\n" + "=" * 60)
    print("ANÁLISIS POR VARIABLES NUMÉRICAS")
    print("=" * 60)

    for col in ["antigüedad_meses", "costo_mensual"]:
        print(f"\n--- {col} ---")
        print(df[col].describe())

        # Boxplot por churn
        plt.figure()
        sns.boxplot(x="cancelado_si_no", y=col, data=df, hue="cancelado_si_no",
                    palette="Set2", legend=False)
        plt.title(f"{col} según cancelado_si_no")
        plt.xlabel("¿Canceló?")
        plt.ylabel(col)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"boxplot_{col}_por_churn.png"), dpi=150)
        plt.close()

        # Histograma segmentado por churn
        plt.figure()
        for valor, color in [("No", "green"), ("Sí", "red")]:
            sub = df[df["cancelado_si_no"] == valor][col]
            plt.hist(sub, bins=25, alpha=0.6, label=valor, color=color, edgecolor="black")
        plt.title(f"Distribución de {col} por estado de churn")
        plt.xlabel(col)
        plt.ylabel("Frecuencia")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"hist_{col}_por_churn.png"), dpi=150)
        plt.close()

    # Antigüedad binned por churn
    df["antigüedad_rango"] = pd.cut(
        df["antigüedad_meses"],
        bins=[-1, 6, 12, 24, 48, 120],
        labels=["0-6", "7-12", "13-24", "25-48", "49+"],
    )
    print("\nTasa de churn por rango de antigüedad (meses):")
    tasa_ant = (
        df.groupby("antigüedad_rango", observed=True)["cancelado_si_no"]
        .apply(lambda s: (s == "Sí").mean() * 100)
        .round(2)
    )
    print(tasa_ant)

    plt.figure()
    tasa_ant.plot(kind="bar", color="darkorange", edgecolor="black")
    plt.title("Tasa de Churn (%) por Rango de Antigüedad")
    plt.xlabel("Antigüedad (meses)")
    plt.ylabel("Tasa de churn (%)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "churn_por_antigüedad.png"), dpi=150)
    plt.close()

    # Costo binned por churn
    df["costo_rango"] = pd.cut(
        df["costo_mensual"],
        bins=[0, 30, 50, 70, 100],
        labels=["0-30", "31-50", "51-70", "71+"],
    )
    print("\nTasa de churn por rango de costo mensual:")
    tasa_costo = (
        df.groupby("costo_rango", observed=True)["cancelado_si_no"]
        .apply(lambda s: (s == "Sí").mean() * 100)
        .round(2)
    )
    print(tasa_costo)

    plt.figure()
    tasa_costo.plot(kind="bar", color="purple", edgecolor="black")
    plt.title("Tasa de Churn (%) por Rango de Costo Mensual")
    plt.xlabel("Costo mensual")
    plt.ylabel("Tasa de churn (%)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "churn_por_costo.png"), dpi=150)
    plt.close()

    return df


def matriz_correlacion(df):
    print("\n" + "=" * 60)
    print("MATRIZ DE CORRELACIÓN (variables numéricas + objetivo binario)")
    print("=" * 60)

    df_num = df.copy()
    df_num["cancelado_bin"] = (df_num["cancelado_si_no"] == "Sí").astype(int)
    df_num["soporte_bin"] = (df_num["soporte_tecnico_usado"] == "Sí").astype(int)

    cols_corr = ["antigüedad_meses", "costo_mensual", "soporte_bin", "cancelado_bin"]
    corr = df_num[cols_corr].corr().round(3)
    print(corr)

    plt.figure()
    sns.heatmap(corr, annot=True, cmap="RdBu_r", center=0, fmt=".3f",
                square=True, cbar_kws={"shrink": 0.8})
    plt.title("Matriz de Correlación - Variables Numéricas y Churn")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "matriz_correlacion.png"), dpi=150)
    plt.close()

    return df_num


def exportar_resumen(df, df_num):
    # Estadísticas descriptivas
    df.describe(include="all").to_csv(
        os.path.join(OUTPUT_DIR, "resumen_descriptivos.csv"), encoding="utf-8"
    )
    # Churn global
    df["cancelado_si_no"].value_counts().to_csv(
        os.path.join(OUTPUT_DIR, "resumen_churn_global.csv"), encoding="utf-8"
    )
    # Tasa de churn por variable categórica
    for col in ["plan", "soporte_tecnico_usado", "antigüedad_rango", "costo_rango"]:
        (
            df.groupby(col, observed=True)["cancelado_si_no"]
            .apply(lambda s: (s == "Sí").mean() * 100)
            .round(2)
            .to_csv(
                os.path.join(OUTPUT_DIR, f"resumen_churn_por_{col}.csv"),
                encoding="utf-8",
            )
        )
    # Matriz de correlación
    df_num[["antigüedad_meses", "costo_mensual", "soporte_bin", "cancelado_bin"]].corr().round(3).to_csv(
        os.path.join(OUTPUT_DIR, "resumen_matriz_correlacion.csv"), encoding="utf-8"
    )
    print(f"\nResumen exportado a archivos CSV en: {OUTPUT_DIR}/")


def main():
    df = cargar_datos(INPUT_CSV)
    df = resumen_general(df)
    df = analisis_categorico(df)
    df = analisis_numerico(df)
    df_num = matriz_correlacion(df)
    exportar_resumen(df, df_num)

    print("\n" + "=" * 60)
    print("ANÁLISIS COMPLETADO")
    print("=" * 60)
    print(f"Gráficos guardados en: {OUTPUT_DIR}/")
    for archivo in sorted(os.listdir(OUTPUT_DIR)):
        print(" -", archivo)


if __name__ == "__main__":
    main()
