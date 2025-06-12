from typing import Dict, Any
from psycopg2.extras import DictCursor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.cpu import CpuModel

class DatabaseService:
    @staticmethod
    def get_cpu_specs(input_data: Dict[str, Any]) -> CpuModel:
        cpu_name = input_data.get('cpu')
        if not cpu_name:
            raise ValueError("CPU name not found in input data")
        
        query = """
            SELECT * FROM pc_components.cpu 
            WHERE name = %s
            LIMIT 1
        """
        
        with Database() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (cpu_name,))
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError(f"CPU '{cpu_name}' not found in database")
                
                return CpuModel.from_orm(result)
            
input_data = {
    "game": "cyberpunk_2077",
    "quality": "ultra",
    "cpu": "Процессор Intel Pentium Gold G5400 OEM",
    # ... другие поля
}

try:
    cpu_specs = DatabaseService.get_cpu_specs(input_data)
    print(cpu_specs.model_dump())
except ValueError as e:
    print(f"Error: {e}")