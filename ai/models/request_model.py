from typing import Optional, Dict, Literal
from pydantic import BaseModel


class Technologies(BaseModel):
    rt: bool
    dlss: Optional[Literal["off", "performance", "balanced", "quality"]] = "off"


class RequestModel(BaseModel):
    game: str
    graphics: Literal["Low", "Medium", "High", "Ultra"]
    fps: int
    resolution: str  # Можно разбить на ширину и высоту при желании
    technologies: Technologies
    budget: int  # В рублях
    preselected_parts: Dict[str, Optional[int]]  # Название компонента -> ID в БД
    priorities: Dict[str, Literal["low", "medium", "high"]]
