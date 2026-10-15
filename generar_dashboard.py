"""
Genera dashboard_churn.html: dashboard web interactivo (un solo archivo) con
Plotly y DataTables sobre clientes_churn.csv.

Incluye:
  - Tarjetas de KPI (total clientes, cancelados, activos, tasa de churn,
    antigüedad promedio, costo promedio mensual).
  - Filtros interactivos (plan, soporte técnico, rango de antigüedad, rango de costo).
  - Gráficos Plotly reactivos a los filtros.
  - Tabla DataTables con los datos filtrados (paginación, ordenamiento, búsqueda).
"""

import pandas as pd
import json

CSV_INPUT = "clientes_churn.csv"
HTML_OUTPUT = "dashboard_churn.html"

# ---------------------------------------------------------------------------
# 1. Cargar datos y calcular KPIs globales
# ---------------------------------------------------------------------------
df = pd.read_csv(CSV_INPUT, encoding="utf-8")

total_clientes = len(df)
cancelados = int((df["cancelado_si_no"] == "Sí").sum())
activos = total_clientes - cancelados
tasa_churn = (cancelados / total_clientes * 100) if total_clientes else 0
antig_promedio = df["antigüedad_meses"].mean()
costo_promedio = df["costo_mensual"].mean()

# Datos embebidos como JSON en el HTML (UTF-8, sin escapar acentos/ñ)
datos_json = json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2)

# ---------------------------------------------------------------------------
# 2. Plantilla HTML (placeholders se sustituyen con .replace())
# ---------------------------------------------------------------------------
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard Customer Churn</title>

<!-- Plotly.js -->
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<!-- jQuery + DataTables -->
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
<script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>

<style>
  :root{
    --primary:#1f77b4;
    --danger:#ef553b;
    --success:#00cc96;
    --bg:#f7f9fc;
    --card:#ffffff;
    --text:#2b2b2b;
  }
  body{font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: var(--bg); color: var(--text); margin:0; padding:24px;}
  .header{background: linear-gradient(90deg, #1f4e79, #2980b9); color:#fff; padding:24px 32px; border-radius:12px; margin-bottom:24px; box-shadow:0 4px 12px rgba(0,0,0,.08);}
  .header h1{margin:0 0 8px 0; font-size:26px;}
  .header p{margin:0; opacity:.9; font-size:14px;}

  /* KPI cards */
  .kpi-grid{display:grid; grid-template-columns: repeat(auto-fit,minmax(170px,1fr)); gap:16px; margin-bottom:28px;}
  .kpi-card{background: var(--card); border:1px solid #e3e8ee; border-radius:12px; padding:20px 16px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,.04);}
  .kpi-card .valor{font-size:28px; font-weight:700; margin:6px 0 2px 0;}
  .kpi-card .etiqueta{font-size:13px; color:#5b6b7c; text-transform:uppercase; letter-spacing:.04em;}
  .kpi-card .sub{font-size:12px; color:#8a97a5; margin-top:4px;}
  .kpi-danger .valor{color: var(--danger);}
  .kpi-success .valor{color: var(--success);}
  .kpi-primary .valor{color: var(--primary);}

  /* Filtros */
  .filtros{background: var(--card); border:1px solid #e3e8ee; border-radius:12px; padding:20px; margin-bottom:24px; box-shadow:0 2px 8px rgba(0,0,0,.04); display:flex; flex-wrap:wrap; gap:16px; align-items:flex-end;}
  .filtro{display:flex; flex-direction:column; gap:6px; min-width:160px;}
  .filtro label{font-size:12px; font-weight:600; color:#4a5a6a; text-transform:uppercase; letter-spacing:.02em;}
  .filtro select{padding:8px 10px; border:1px solid #c9d2dc; border-radius:8px; background:#fff; font-size:13px; cursor:pointer;}
  .filtro select:focus{border-color: var(--primary); outline:none;}

  /* Gráficos */
  .graficos{display:grid; grid-template-columns: repeat(auto-fit,minmax(420px,1fr)); gap:24px; margin-bottom:28px;}
  .grafico-card{background: var(--card); border:1px solid #e3e8ee; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,.04);}
  .grafico-card h3{margin:0 0 12px 0; font-size:16px; color:#3a4a5a;}

  /* Tabla */
  .tabla-card{background: var(--card); border:1px solid #e3e8ee; border-radius:12px; padding:0; box-shadow:0 2px 8px rgba(0,0,0,.04); overflow:hidden;}
  .tabla-card .tabla-header{padding:16px 20px; border-bottom:1px solid #e3e8ee; display:flex; justify-content:space-between; align-items:center;}
  .tabla-header h3{margin:0; font-size:16px; color:#3a4a5a;}
  .tabla-header .badge{background:#eef4fb; color: var(--primary); border:1px solid #cde3f6; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:600;}
  table.dataTable.no-footer{border-collapse:collapse !important;}
  table.dataTable thead th{background:#f1f5f9; color:#3a4a5a; font-weight:600; font-size:13px; padding:12px 10px; border-bottom:1px solid #e3e8ee;}
  table.dataTable tbody td{padding:10px; font-size:13px; border-bottom:1px solid #f0f2f5;}
  table.dataTable tbody tr:hover{background:#f7fafc;}
  .dataTables_wrapper .dataTables_paginate .paginate_button.current{background: var(--primary) !important; border:1px solid var(--primary) !important; color:#fff !important;}
  .dataTables_length, .dataTables_filter{margin:8px 0;}
  .dataTables_length select, .dataTables_filter input{padding:6px 8px; border:1px solid #c9d2dc; border-radius:6px; font-size:13px;}

  .muted{color:#6b7a8a; font-size:12px; margin-top:8px;}
</style>
</head>
<body>

<div class="header">
  <h1>📊 Dashboard de Fuga de Clientes (Customer Churn)</h1>
  <p>Análisis exploratorio y monitoreo de cancelaciones &mdash; {TOTAL_CLIENTES} clientes registrados</p>
</div>

<!-- KPIs -->
<div class="kpi-grid">
  <div class="kpi-card kpi-primary">
    <div class="etiqueta">Total de clientes</div>
    <div class="valor">{TOTAL_CLIENTES}</div>
  </div>
  <div class="kpi-card kpi-danger">
    <div class="etiqueta">Cancelados (Churn)</div>
    <div class="valor">{CANCELADOS}</div>
    <div class="sub">Tasa de churn: <b>{TASA_CHURN}%</b></div>
  </div>
  <div class="kpi-card kpi-success">
    <div class="etiqueta">Activos</div>
    <div class="valor">{ACTIVOS}</div>
  </div>
  <div class="kpi-card">
    <div class="etiqueta">Antigüedad promedio</div>
    <div class="valor">{ANTIG_PROMEDIO} meses</div>
  </div>
  <div class="kpi-card">
    <div class="etiqueta">Costo mensual promedio</div>
    <div class="valor">{COSTO_PROMEDIO}</div>
  </div>
</div>

<!-- Filtros -->
<div class="filtros">
  <div class="filtro">
    <label>Plan</label>
    <select id="filtro-plan">
      <option value="Todos">Todos</option>
      <option value="Básico">Básico</option>
      <option value="Estándar">Estándar</option>
      <option value="Premium">Premium</option>
    </select>
  </div>
  <div class="filtro">
    <label>Soporte técnico usado</label>
    <select id="filtro-soporte">
      <option value="Todos">Todos</option>
      <option value="Sí">Sí</option>
      <option value="No">No</option>
    </select>
  </div>
  <div class="filtro">
    <label>Rango de antigüedad (meses)</label>
    <select id="filtro-antiguedad">
      <option value="Todas">Todas</option>
      <option value="0-6">0 - 6</option>
      <option value="7-12">7 - 12</option>
      <option value="13-24">13 - 24</option>
      <option value="25-48">25 - 48</option>
      <option value="49-120">49 +</option>
    </select>
  </div>
  <div class="filtro">
    <label>Rango de costo mensual</label>
    <select id="filtro-costo">
      <option value="Todas">Todas</option>
      <option value="0-30">0 - 30</option>
      <option value="31-50">31 - 50</option>
      <option value="51-70">51 - 70</option>
      <option value="71-200">71 +</option>
    </select>
  </div>
  <p class="muted" style="margin:0 0 0 16px;">Los filtros se aplican a KPIs, gráficos y tabla al instante.</p>
</div>

<!-- Gráficos -->
<div class="graficos">
  <div class="grafico-card"><h3>Tasa de Churn por Plan (%)</h3><div id="g-plan"></div></div>
  <div class="grafico-card"><h3>Tasa de Churn por Soporte Técnico (%)</h3><div id="g-soporte"></div></div>
  <div class="grafico-card"><h3>Tasa de Churn por Antigüedad (%)</h3><div id="g-antiguedad"></div></div>
  <div class="grafico-card"><h3>Tasa de Churn por Costo Mensual (%)</h3><div id="g-costo"></div></div>
  <div class="grafico-card" style="grid-column: span 2;"><h3>Antigüedad vs Costo Mensual (color = ¿Canceló?)</h3><div id="g-scatter"></div></div>
  <div class="grafico-card"><h3>Distribución de Costo Mensual por Churn</h3><div id="g-hist"></div></div>
</div>

<!-- Tabla -->
<div class="tabla-card">
  <div class="tabla-header">
    <h3>Detalle de Clientes</h3>
    <div class="badge" id="badge-filas">0 filas</div>
  </div>
  <table id="tabla-clientes" class="display" style="width:100%;">
    <thead>
      <tr>
        <th>id_cliente</th>
        <th>Antigüedad (meses)</th>
        <th>Plan</th>
        <th>Soporte técnico</th>
        <th>Costo mensual</th>
        <th>¿Canceló?</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>
</div>

<p class="muted">Generado automáticamente con Python, Plotly y DataTables. Archivo: {HTML_OUTPUT}</p>

<script>
  const datos = {DATOS_JSON};

  const rangosAntiguedad = {
    "0-6": [0, 6],
    "7-12": [7, 12],
    "13-24": [13, 24],
    "25-48": [25, 48],
    "49-120": [49, 120]
  };
  const rangosCosto = {
    "0-30": [0, 30],
    "31-50": [31, 50],
    "51-70": [51, 70],
    "71-200": [71, 200]
  };

  let tabla = null;

  function obtenerFiltros(){
    return {
      plan: document.getElementById("filtro-plan").value,
      soporte: document.getElementById("filtro-soporte").value,
      antiguedad: document.getElementById("filtro-antiguedad").value,
      costo: document.getElementById("filtro-costo").value
    };
  }

  function filtrarDatos(){
    const f = obtenerFiltros();
    return datos.filter(d => {
      if (f.plan !== "Todos" && d.plan !== f.plan) return false;
      if (f.soporte !== "Todos" && d.soporte_tecnico_usado !== f.soporte) return false;
      if (f.antiguedad !== "Todas"){
        const [a,b] = rangosAntiguedad[f.antiguedad];
        if (d.antigüedad_meses < a || d.antigüedad_meses > b) return false;
      }
      if (f.costo !== "Todas"){
        const [a,b] = rangosCosto[f.costo];
        if (d.costo_mensual < a || d.costo_mensual > b) return false;
      }
      return true;
    });
  }

  function tasaChurn(subset){
    if (!subset.length) return 0;
    const c = subset.filter(d => d.cancelado_si_no === "Sí").length;
    return (c / subset.length * 100);
  }

  function actualizarKPIs(subset){
    const total = subset.length;
    const canc = subset.filter(d => d.cancelado_si_no === "Sí").length;
    const act = total - canc;
    const tasa = tasaChurn(subset);
    const promAnt = total ? (subset.reduce((s,d)=>s+d.antigüedad_meses,0)/total).toFixed(1) : 0;
    const promCos = total ? (subset.reduce((s,d)=>s+d.costo_mensual,0)/total).toFixed(2) : 0;

    document.getElementById("badge-filas").textContent = total + " filas";
    document.querySelector(".kpi-card:nth-child(2) .valor").textContent = canc;
    document.querySelector(".kpi-card:nth-child(2) .sub").innerHTML = "Tasa de churn: <b>" + tasa.toFixed(1) + "%</b>";
    document.querySelector(".kpi-card:nth-child(3) .valor").textContent = act;
    document.querySelector(".kpi-card:nth-child(4) .valor").textContent = promAnt + " meses";
    document.querySelector(".kpi-card:nth-child(5) .valor").textContent = promCos;
  }

  function agruparTasa(subset, clave, orden){
    const grupos = [...new Set(subset.map(d => d[clave]))].sort((a,b)=>{
      if (orden) return orden.indexOf(a) - orden.indexOf(b);
      return a - b;
    });
    const tasas = grupos.map(g => {
      const sub = subset.filter(d => d[clave] === g);
      const c = sub.filter(d => d.cancelado_si_no === "Sí").length;
      return (c / sub.length * 100).toFixed(1);
    });
    return {x: grupos, y: tasas};
  }

  const layoutBase = {
    margin: {t: 40, b: 40, l: 60, r: 20},
    font: {family: "Segoe UI, sans-serif", size: 12, color: "#3a4a5a"},
    plot_bgcolor: "#ffffff",
    paper_bgcolor: "#ffffff",
    xaxis: {tickangle: 0},
    yaxis: {rangemode: "tozero", ticksuffix: "%"}
  };

  function dibujarGraficos(subset){
    // 1. Churn por plan
    const p1 = agruparTasa(subset, "plan", ["Básico", "Estándar", "Premium"]);
    Plotly.newPlot("g-plan", [{
      x: p1.x, y: p1.y, type: "bar",
      marker: {color: ["#ef553b", "#ef553b", "#ef553b"]},
      text: p1.y.map(v => v + "%"), textposition: "auto"
    }], {...layoutBase, title: {text: "Tasa de Churn por Plan (%)", x: 0.5}, yaxis: {ticksuffix: "%", range: [0, Math.max(...p1.y, 10) * 1.25]}});

    // 2. Churn por soporte
    const p2 = agruparTasa(subset, "soporte_tecnico_usado", ["No", "Sí"]);
    Plotly.newPlot("g-soporte", [{
      x: p2.x, y: p2.y, type: "bar",
      marker: {color: ["#00cc96", "#ef553b"]},
      text: p2.y.map(v => v + "%"), textposition: "auto"
    }], {...layoutBase, title: {text: "Tasa de Churn por Soporte Técnico (%)", x: 0.5}, yaxis: {ticksuffix: "%", range: [0, Math.max(...p2.y, 10) * 1.25]}});

    // 3. Churn por antigüedad
    const p3 = agruparTasa(subset, "antigüedad_rango_calc", ["0-6", "7-12", "13-24", "25-48", "49+"]);
    Plotly.newPlot("g-antiguedad", [{
      x: p3.x, y: p3.y, type: "bar",
      marker: {color: "#ef553b"},
      text: p3.y.map(v => v + "%"), textposition: "auto"
    }], {...layoutBase, title: {text: "Tasa de Churn por Rango de Antigüedad (meses)", x: 0.5}, yaxis: {ticksuffix: "%", range: [0, Math.max(...p3.y, 10) * 1.25]}});

    // 4. Churn por costo
    const p4 = agruparTasa(subset, "costo_rango_calc", ["0-30", "31-50", "51-70", "71+"]);
    Plotly.newPlot("g-costo", [{
      x: p4.x, y: p4.y, type: "bar",
      marker: {color: "#636efa"},
      text: p4.y.map(v => v + "%"), textposition: "auto"
    }], {...layoutBase, title: {text: "Tasa de Churn por Rango de Costo Mensual", x: 0.5}, yaxis: {ticksuffix: "%", range: [0, Math.max(...p4.y, 10) * 1.25]}});

    // 5. Scatter antigüedad vs costo
    const no = subset.filter(d => d.cancelado_si_no === "No");
    const si = subset.filter(d => d.cancelado_si_no === "Sí");
    Plotly.newPlot("g-scatter", [
      {x: no.map(d=>d.antigüedad_meses), y: no.map(d=>d.costo_mensual), mode: "markers", type: "scatter", name: "No canceló", marker: {color: "#00cc96", size: 8, opacity: 0.7}},
      {x: si.map(d=>d.antigüedad_meses), y: si.map(d=>d.costo_mensual), mode: "markers", type: "scatter", name: "Canceló", marker: {color: "#ef553b", size: 8, opacity: 0.85, symbol: "x"}}
    ], {...layoutBase, title: {text: "Antigüedad vs Costo Mensual", x: 0.5}, xaxis: {title: "Antigüedad (meses)"}, yaxis: {title: "Costo mensual"}});

    // 6. Histograma costo por churn
    const histNo = no.map(d => d.costo_mensual);
    const histSi = si.map(d => d.costo_mensual);
    Plotly.newPlot("g-hist", [
      {x: histNo, type: "histogram", name: "No canceló", marker: {color: "#00cc96"}, opacity: 0.7, nbinsx: 20},
      {x: histSi, type: "histogram", name: "Canceló", marker: {color: "#ef553b"}, opacity: 0.85, nbinsx: 20}
    ], {...layoutBase, title: {text: "Distribución de Costo Mensual por Estado de Churn", x: 0.5}, barmode: "overlay", xaxis: {title: "Costo mensual"}, yaxis: {title: "Frecuencia"}});
  }

  function actualizarTabla(subset){
    if (!tabla){
      tabla = $("#tabla-clientes").DataTable({
        data: subset,
        columns: [
          {data: "id_cliente"},
          {data: "antigüedad_meses"},
          {data: "plan"},
          {data: "soporte_tecnico_usado"},
          {data: "costo_mensual", render: $.fn.dataTable.render.number('.', ',', 2, '')},
          {data: "cancelado_si_no", render: function(d, type, row){
            return d === "Sí" ? '<span style="color:#ef553b; font-weight:600;">Sí</span>' : '<span style="color:#00cc96; font-weight:600;">No</span>';
          }}
        ],
        pageLength: 10,
        responsive: true,
        language: {
          url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
        }
      });
    } else {
      tabla.clear().rows.add(subset).draw();
    }
  }

  // Rangos de antigüedad/costo para agrupación (calculados en JS para filtrado)
  function clasificarAntiguedad(v){
    if (v <= 6) return "0-6";
    if (v <= 12) return "7-12";
    if (v <= 24) return "13-24";
    if (v <= 48) return "25-48";
    return "49+";
  }
  function clasificarCosto(v){
    if (v <= 30) return "0-30";
    if (v <= 50) return "31-50";
    if (v <= 70) return "51-70";
    return "71+";
  }

  function actualizarDashboard(){
    const subset = filtrarDatos();
    // Añadir columnas de rango para agrupación
    const subsetConRangos = subset.map(d => ({
      ...d,
      antigüedad_rango_calc: clasificarAntiguedad(d.antigüedad_meses),
      costo_rango_calc: clasificarCosto(d.costo_mensual)
    }));
    actualizarKPIs(subset);
    dibujarGraficos(subsetConRangos);
    actualizarTabla(subset);
  }

  // Eventos de filtros
  document.getElementById("filtro-plan").addEventListener("change", actualizarDashboard);
  document.getElementById("filtro-soporte").addEventListener("change", actualizarDashboard);
  document.getElementById("filtro-antiguedad").addEventListener("change", actualizarDashboard);
  document.getElementById("filtro-costo").addEventListener("change", actualizarDashboard);

  // Inicializar
  window.addEventListener("DOMContentLoaded", actualizarDashboard);
</script>

</body>
</html>
"""

# ---------------------------------------------------------------------------
# 3. Sustituir placeholders y escribir archivo
# ---------------------------------------------------------------------------
html_final = HTML_TEMPLATE.replace("{DATOS_JSON}", datos_json)
html_final = html_final.replace("{TOTAL_CLIENTES}", str(total_clientes))
html_final = html_final.replace("{CANCELADOS}", str(cancelados))
html_final = html_final.replace("{ACTIVOS}", str(activos))
html_final = html_final.replace("{TASA_CHURN}", f"{tasa_churn:.1f}")
html_final = html_final.replace("{ANTIG_PROMEDIO}", f"{antig_promedio:.1f}")
html_final = html_final.replace("{COSTO_PROMEDIO}", f"{costo_promedio:.2f}")
html_final = html_final.replace("{HTML_OUTPUT}", HTML_OUTPUT)

with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
    f.write(html_final)

print(f"Dashboard generado: {HTML_OUTPUT}")
print(f"Clientes: {total_clientes} | Cancelados: {cancelados} ({tasa_churn:.1f}%) | Activos: {activos}")
