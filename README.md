# losazules — Ingesta de Telemetría de Flota (Los Azules, McEwen Copper)

## 1. FORMALIZE

**Propósito.** Script de ingesta que persiste eventos de ciclo de acarreo de camiones mineros en SQLite. Cada fila es una tupla `(equipo_id, modelo, timestamp, tiempo_ciclo_min, carga_ton)` — un punto de telemetría, no un estado de equipo.

**Modelo de datos.**

```
f: Evento → Fila
Evento = (equipo_id ∈ ID_flota, modelo ∈ Specs_OEM, t ∈ Timestamp, τ ∈ ℝ⁺, m ∈ ℝ⁺)
```

| Campo | Tipo | Dominio | Semántica |
|---|---|---|---|
| `equipo_id` | `TEXT` | `CAM-NNN` | Identificador físico del camión (constante en el tiempo) |
| `modelo` | `TEXT` | libre | Modelo OEM — debe validarse contra flota real, no es un enum forzado por schema |
| `timestamp` | `TEXT` |  no tipado | Instante de la medición |
| `tiempo_ciclo_min` | `REAL` | `[0, ∞)` | Duración del ciclo de acarreo en minutos |
| `carga_ton` | `REAL` | `[0, capacidad_OEM]` | Carga transportada, acotada arriba por el payload nominal del modelo |


## 2. VERIFY

**Comportamiento en dos regímenes**, según el estado del `.db` al momento de ejecutar:

- **DB nueva o inexistente:** `CREATE TABLE` con PK compuesta desde el origen. Correcto por construcción.
- **DB legacy (creada antes de este fix, sin PK):** SQLite no soporta `ALTER TABLE ... ADD PRIMARY KEY` sobre una tabla existente. El script detecta este caso (`'PRIMARY KEY' not in <schema existente>`) y ejecuta una migración explícita: `RENAME` → `CREATE` con constraint → `INSERT OR IGNORE ... SELECT DISTINCT` desde la tabla vieja → `DROP` de la tabla legacy.

**Test de idempotencia (control empírico, no supuesto).** Se ejecutó el script 3 veces consecutivas contra una copia del `losazules.db` original (4 filas, sin PK):

```
Run 1 → 4 filas
Run 2 → 4 filas
Run 3 → 4 filas
```

Sin la migración, el mismo test da `4 → 8 → 12` filas — el bug original: `CREATE TABLE IF NOT EXISTS` es no-op sobre schema preexistente, y sin PK el `INSERT OR IGNORE` no tiene contra qué comparar, así que no ignora nada. El script corre sin excepción e imprime `OK` en ambos casos — el fallo es silencioso, no se detecta por logs ni por código de salida.

**Error de dominio corregido — `CAM-001`.** El dato original listaba `Mercedes-Benz Arocs` con `carga_ton = 175.0`. El Arocs es un chasis de obra/vial (8x4, GVW máximo ≈32 t); no es un haul truck minero y no puede fisicamente transportar 175 t. Se reemplazó por `CAT 797F`, consistente con el rango de payload del resto de la flota (168–182 t: CAT 793F, Komatsu 930E, Liebherr T284). **Limitación:** este fix corrige el *schema* y la lógica de *inserts nuevos* — no reescribe contenido histórico. Un `losazules.db` real que ya tenga la fila legacy con "Mercedes-Benz Arocs" persistida requiere un `UPDATE` explícito y deliberado; la migración de schema no lo hace implícitamente, porque una migración que además reescribe valores sin pedirse es un side-effect no auditable.



*Actualizacion*
Con este simple programa podemos despues pasarlo a MD para hacer fine tunning , lo estare actualizando asi hacerlo automaticamente.