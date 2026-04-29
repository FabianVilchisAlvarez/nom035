from pydantic import BaseModel, Field
from uuid import UUID

class GenerarEvaluacionSchema(BaseModel):
    total_empleados: int = Field(gt=0)