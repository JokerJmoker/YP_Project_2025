from pydantic import BaseModel, validator
from typing import Optional, Any 
import re

class CaseFanModel(BaseModel):
    id: int
    name: str
    price: int  # в рублях
    
    # Основные параметры вентилятора
    fan_size: Optional[int] = None              # мм
    fan_thickness: Optional[int] = None         # мм
    max_rotation_speed: Optional[int] = None    # об/мин (max_rpm)
    min_rotation_speed: Optional[int] = None    # об/мин (min_rpm)
    max_airflow: Optional[float] = None         # CFM
    max_static_pressure: Optional[float] = None # mmH2O
    max_noise_level: Optional[float] = None     # дБА
    min_noise_level: Optional[float] = None     # дБА
    power_connector_type: Optional[str] = None  # Тип разъема питания
    
    @classmethod
    def parse_numeric_string(cls, value: Any) -> Optional[float]:
        """Извлекает числовое значение из строки с единицами измерения"""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        
        try:
            # Ищем первое число в строке (с плавающей точкой)
            match = re.search(r"[-+]?\d*\.\d+|\d+", str(value))
            return float(match.group()) if match else None
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def parse_integer_string(cls, value: Any) -> Optional[int]:
        """Извлекает целое число из строки с единицами измерения"""
        num = cls.parse_numeric_string(value)
        return int(num) if num is not None else None
    
    @classmethod
    def from_orm(cls, fan_orm):
        return cls(
            id=fan_orm['id'],
            name=fan_orm['name'],
            price=int(fan_orm['price']),
            fan_size=cls.parse_integer_string(fan_orm.get('fan_size')),
            fan_thickness=cls.parse_integer_string(fan_orm.get('fan_thickness')),
            max_rotation_speed=cls.parse_integer_string(fan_orm.get('max_rotation_speed')),
            min_rotation_speed=cls.parse_integer_string(fan_orm.get('min_rotation_speed')),
            max_airflow=cls.parse_numeric_string(fan_orm.get('max_airflow')),
            max_static_pressure=cls.parse_numeric_string(fan_orm.get('max_static_pressure')),
            max_noise_level=cls.parse_numeric_string(fan_orm.get('max_noise_level')),
            min_noise_level=cls.parse_numeric_string(fan_orm.get('min_noise_level')),
            power_connector_type=fan_orm.get('power_connector_type')
        )

    # Валидаторы для каждого числового поля
    @validator('fan_size', 'fan_thickness', 'max_rotation_speed', 'min_rotation_speed', pre=True)
    def validate_integer_fields(cls, v):
        return cls.parse_integer_string(v)
    
    @validator('max_airflow', 'max_static_pressure', 'max_noise_level', 'min_noise_level', pre=True)
    def validate_float_fields(cls, v):
        return cls.parse_numeric_string(v)