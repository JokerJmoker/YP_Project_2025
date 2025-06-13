import psycopg2

conn = psycopg2.connect("dbname=mydb user=jokerjmoker password=270961Ts host=127.0.0.1 port=5532")
cur = conn.cursor()

price_limit = 60000
memory_type = 'DDR4'
freq_min = 7020
freq_max = 8580
modules_count = 2
total_memory = 32
ecc_memory = False
registered_memory = False
target_frequency = 7800

print("=== Проверка: есть ли DIMM по цене и типу памяти ===")
cur.execute("""
    SELECT id, frequency, modules_count, total_memory, ecc_memory, registered_memory, price
    FROM pc_components.dimm
    WHERE price <= %s AND memory_type = %s
    LIMIT 5
""", (price_limit, memory_type))
rows = cur.fetchall()
print(f"Найдено {len(rows)} строк:")
for r in rows:
    print(r)

print("\n=== Проверка parsed_* значений ===")
cur.execute("""
    SELECT frequency, modules_count, total_memory,
           NULLIF(REGEXP_REPLACE(frequency, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_frequency,
           NULLIF(REGEXP_REPLACE(modules_count, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_modules_count,
           NULLIF(REGEXP_REPLACE(total_memory, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_total_memory
    FROM pc_components.dimm
    WHERE price <= %s AND memory_type = %s
    LIMIT 10
""", (price_limit, memory_type))
rows = cur.fetchall()
for r in rows:
    print(r)

print("\n=== Проверка с постепенным добавлением фильтров ===")

# Фильтр по частоте
cur.execute("""
    WITH parsed_dimm AS (
        SELECT *,
            NULLIF(REGEXP_REPLACE(frequency, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_frequency,
            NULLIF(REGEXP_REPLACE(modules_count, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_modules_count,
            NULLIF(REGEXP_REPLACE(total_memory, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_total_memory
        FROM pc_components.dimm
        WHERE price <= %s AND memory_type = %s
    )
    SELECT COUNT(*) FROM parsed_dimm
    WHERE parsed_frequency BETWEEN %s AND %s
""", (price_limit, memory_type, freq_min, freq_max))
count = cur.fetchone()[0]
print(f"Число строк, соответствующих по частоте: {count}")

# Добавляем modules_count
cur.execute("""
    WITH parsed_dimm AS (
        SELECT *,
            NULLIF(REGEXP_REPLACE(frequency, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_frequency,
            NULLIF(REGEXP_REPLACE(modules_count, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_modules_count,
            NULLIF(REGEXP_REPLACE(total_memory, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_total_memory
        FROM pc_components.dimm
        WHERE price <= %s AND memory_type = %s
    )
    SELECT COUNT(*) FROM parsed_dimm
    WHERE parsed_frequency BETWEEN %s AND %s
      AND parsed_modules_count = %s
""", (price_limit, memory_type, freq_min, freq_max, modules_count))
count = cur.fetchone()[0]
print(f"Число строк с modules_count={modules_count}: {count}")

# Добавляем total_memory
cur.execute("""
    WITH parsed_dimm AS (
        SELECT *,
            NULLIF(REGEXP_REPLACE(frequency, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_frequency,
            NULLIF(REGEXP_REPLACE(modules_count, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_modules_count,
            NULLIF(REGEXP_REPLACE(total_memory, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_total_memory
        FROM pc_components.dimm
        WHERE price <= %s AND memory_type = %s
    )
    SELECT COUNT(*) FROM parsed_dimm
    WHERE parsed_frequency BETWEEN %s AND %s
      AND parsed_modules_count = %s
      AND parsed_total_memory = %s
""", (price_limit, memory_type, freq_min, freq_max, modules_count, total_memory))
count = cur.fetchone()[0]
print(f"Число строк с total_memory={total_memory}: {count}")

# Добавляем ecc_memory и registered_memory
cur.execute("""
    WITH parsed_dimm AS (
        SELECT *,
            NULLIF(REGEXP_REPLACE(frequency, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_frequency,
            NULLIF(REGEXP_REPLACE(modules_count, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_modules_count,
            NULLIF(REGEXP_REPLACE(total_memory, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_total_memory
        FROM pc_components.dimm
        WHERE price <= %s AND memory_type = %s
    )
    SELECT COUNT(*) FROM parsed_dimm
    WHERE parsed_frequency BETWEEN %s AND %s
      AND parsed_modules_count = %s
      AND parsed_total_memory = %s
      AND ecc_memory = %s
      AND registered_memory = %s
""", (price_limit, memory_type, freq_min, freq_max, modules_count, total_memory, ecc_memory, registered_memory))
count = cur.fetchone()[0]
print(f"Число строк с фильтрами по ECC и Registered: {count}")

# Финальный запрос с выборкой
print("\n=== Финальный запрос с LIMIT 1 ===")
cur.execute("""
    WITH parsed_dimm AS (
        SELECT *,
            NULLIF(REGEXP_REPLACE(frequency, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_frequency,
            NULLIF(REGEXP_REPLACE(modules_count, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_modules_count,
            NULLIF(REGEXP_REPLACE(total_memory, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_total_memory
        FROM pc_components.dimm
    )
    SELECT * FROM parsed_dimm
    WHERE price <= %s
      AND memory_type = %s
      AND parsed_frequency BETWEEN %s AND %s
      AND parsed_modules_count = %s
      AND parsed_total_memory = %s
      AND ecc_memory = %s
      AND registered_memory = %s
    ORDER BY ABS(parsed_frequency - %s), price ASC
    LIMIT 1
""", (price_limit, memory_type, freq_min, freq_max, modules_count, total_memory, ecc_memory, registered_memory, target_frequency))
row = cur.fetchone()
if row:
    print("Найден DIMM:", row)
else:
    print("Ошибка: DIMM, подходящий под все критерии, не найден.")

cur.close()
conn.close()
