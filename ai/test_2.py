def get_component_benchmark(component_type, name, conn):
    """Получает benchmark_rate для конкретного компонента"""
    with conn.cursor() as cur:
        query = f"""
        SELECT benchmark_rate FROM pc_components.{component_type}
        WHERE name = %s
        """
        cur.execute(query, (name,))
        result = cur.fetchone()
        if result:
            return float(result[0])
        raise ValueError(f"Не удалось найти benchmark_rate для {component_type} {name}")

def find_alternative_components(component_type, original_name, max_price, conn):
    """Ищет альтернативные компоненты с похожим benchmark_rate и ценой <= max_price"""
    # Сначала получаем benchmark_rate оригинального компонента
    original_benchmark = get_component_benchmark(component_type, original_name, conn)
    
    with conn.cursor() as cur:
        query = f"""
        SELECT 
            name, 
            price, 
            benchmark_rate,
            ROUND((benchmark_rate / %s) * 100, 2) as performance_percent,
            ROUND((price / %s) * 100, 2) as price_percent
        FROM pc_components.{component_type}
        WHERE 
            benchmark_rate BETWEEN %s AND %s
            AND price <= %s
            AND name != %s
        ORDER BY 
            ABS(benchmark_rate - %s) ASC,  # Сначала компоненты с ближайшим benchmark_rate
            price ASC  # Затем самые дешевые
        LIMIT 5
        """
        # Ищем компоненты с benchmark_rate в пределах 15% от исходного
        min_rate = original_benchmark * 0.85
        max_rate = original_benchmark * 1.15
        
        cur.execute(query, (
            original_benchmark, original_benchmark,  # Для расчета процентов
            min_rate, max_rate, max_price, original_name, original_benchmark
        ))
        
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def adjust_components_to_budget_percentages(build, budget, conn):
    """Корректирует компоненты CPU и GPU согласно процентам бюджета"""
    CPU_PERCENT = 0.2  # 20% бюджета
    GPU_PERCENT = 0.4  # 40% бюджета
    
    result = {
        'adjusted': False,
        'components': {}
    }
    
    # Обрабатываем CPU
    cpu_name = build['cpu']
    cpu_price = get_component_price('cpu', cpu_name, conn)
    cpu_max_price = budget * CPU_PERCENT
    
    if cpu_price > cpu_max_price:
        print(f"CPU {cpu_name} ({cpu_price}₽) превышает {CPU_PERCENT*100}% бюджета ({cpu_max_price}₽), ищем альтернативы...")
        alternatives = find_alternative_components('cpu', cpu_name, cpu_max_price, conn)
        
        if alternatives:
            selected_cpu = alternatives[0]
            print(f"Выбран альтернативный CPU: {selected_cpu['name']} ({selected_cpu['price']}₽, {selected_cpu['benchmark_rate']} benchmark)")
            build['cpu'] = selected_cpu['name']
            result['components']['cpu'] = {
                'original': cpu_name,
                'selected': selected_cpu,
                'alternatives': alternatives
            }
            result['adjusted'] = True
        else:
            print(f"Не найдено подходящих альтернатив для CPU {cpu_name}")
            result['components']['cpu'] = {
                'original': cpu_name,
                'error': 'No alternatives found'
            }
    else:
        print(f"CPU {cpu_name} ({cpu_price}₽) соответствует бюджету ({cpu_max_price}₽)")
        result['components']['cpu'] = {
            'original': cpu_name,
            'price': cpu_price,
            'within_budget': True
        }
    
    # Обрабатываем GPU (аналогичная логика)
    gpu_name = build['gpu']
    gpu_price = get_component_price('gpu', gpu_name, conn)
    gpu_max_price = budget * GPU_PERCENT
    
    if gpu_price > gpu_max_price:
        print(f"GPU {gpu_name} ({gpu_price}₽) превышает {GPU_PERCENT*100}% бюджета ({gpu_max_price}₽), ищем альтернативы...")
        alternatives = find_alternative_components('gpu', gpu_name, gpu_max_price, conn)
        
        if alternatives:
            selected_gpu = alternatives[0]
            print(f"Выбран альтернативный GPU: {selected_gpu['name']} ({selected_gpu['price']}₽, {selected_gpu['benchmark_rate']} benchmark)")
            build['gpu'] = selected_gpu['name']
            result['components']['gpu'] = {
                'original': gpu_name,
                'selected': selected_gpu,
                'alternatives': alternatives
            }
            result['adjusted'] = True
        else:
            print(f"Не найдено подходящих альтернатив для GPU {gpu_name}")
            result['components']['gpu'] = {
                'original': gpu_name,
                'error': 'No alternatives found'
            }
    else:
        print(f"GPU {gpu_name} ({gpu_price}₽) соответствует бюджету ({gpu_max_price}₽)")
        result['components']['gpu'] = {
            'original': gpu_name,
            'price': gpu_price,
            'within_budget': True
        }
    
    return result