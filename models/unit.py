from __future__ import annotations

from typing import Optional, Annotated
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, StringConstraints

# =========================================================================
# Unit Model: 스타크래프트 유닛 관리 시스템의 core domain model!!
# - 프로토스, 테란, 저그 3개 종족의 다양한 유닛들을 manage!!
# - 각 유닛의 stats, cost, abilities를 완벽하게 tracking!!
# - Real-time strategy game의 핵심 요소!! super important~~~
# =========================================================================

# Race Enumeration - 스타크래프트의 3개 종족!! each has unique characteristics~~
class Race(str, Enum):
    PROTOSS = "protoss"    # 프로토스!! psi energy 사용!! high-tech civilization!!
    TERRAN = "terran"      # 테란!! human race!! versatile and adaptive!!
    ZERG = "zerg"          # 저그!! biological swarm!! rapid evolution!!

# Unit Type Classification - 유닛의 역할별 분류!! tactical importance~~~
class UnitType(str, Enum):
    WORKER = "worker"          # 일꾼!! resource gathering의 핵심!!
    BASIC_COMBAT = "basic"     # 기본 전투 유닛!! army의 backbone!!
    ADVANCED_COMBAT = "advanced"  # 고급 전투 유닛!! specialized warfare!!
    SUPPORT = "support"        # 지원 유닛!! utility and assistance!!
    HERO = "hero"             # 영웅 유닛!! powerful and unique!!

# Unit Name Type Definition - standardized unit naming!! consistency important~~
UnitNameType = Annotated[str, StringConstraints(min_length=1, max_length=50)]


class UnitBase(BaseModel):
    """
    ===================================================================
    UnitBase: 스타크래프트 유닛의 basic attributes를 정의하는 base model!! 
    - RTS game mechanics를 반영한 comprehensive unit system!!
    - Combat stats, resource costs, production requirements 모두 포함!!
    - Balance considerations를 위한 detailed attribute management!!
    ===================================================================
    """
    # Unit Name - required!! each unit has unique identity!!
    name: UnitNameType = Field(
        ...,  # required field!! 유닛 이름은 필수!!
        description="Unit name (e.g., Marine, Zealot, Zergling)",
        json_schema_extra={"example": "Marine"},
    )
    
    # Race Classification - determines unit characteristics and tech tree!!
    race: Race = Field(
        ...,  # required!! 종족은 반드시 지정되어야 함!!
        description="Unit race (Protoss/Terran/Zerg)",
        json_schema_extra={"example": "terran"},
    )
    
    # Unit Type - tactical role classification!! strategy planning에 crucial!!
    unit_type: UnitType = Field(
        ...,  # required!! 유닛 타입은 전략적으로 중요!!
        description="Unit type classification",
        json_schema_extra={"example": "basic"},
    )
    
    # Hit Points - survival capability!! 0이 되면 unit destruction!!
    hit_points: int = Field(
        ...,  # required!! HP 없으면 전투 불가능!!
        description="Maximum hit points",
        gt=0,  # must be positive!! negative HP는 말이 안됨!!
        json_schema_extra={"example": 40},
    )
    
    # Shields - 프로토스 전용!! additional protection layer~~
    shields: int = Field(
        0,  # default 0!! 테란/저그는 shield 없음!!
        description="Shield points (Protoss units only)",
        ge=0,  # non-negative!! shield는 0 이상!!
        json_schema_extra={"example": 20},
    )
    
    # Attack Damage - offensive capability!! combat effectiveness의 핵심!!
    attack_damage: int = Field(
        0,  # default 0!! worker units는 공격력 없을 수 있음~~
        description="Base attack damage",
        ge=0,  # non-negative!! negative damage는 healing이 아님!!
        json_schema_extra={"example": 6},
    )
    
    # Armor - damage reduction capability!! survivability 향상!!
    armor: int = Field(
        0,  # default 0!! 기본 armor 없음!!
        description="Armor value for damage reduction",
        ge=0,  # non-negative!! negative armor는 vulnerability!!
        json_schema_extra={"example": 1},
    )
    
    # Movement Speed - tactical mobility!! positioning과 escape에 중요!!
    movement_speed: Decimal = Field(
        ...,  # required!! 이동속도는 필수 stat!!
        description="Movement speed (game units per second)",
        gt=0,  # must be positive!! stationary units도 minimal speed!!
        decimal_places=2,  # precision for balance!! 2.25 같은 값들!!
        json_schema_extra={"example": 2.25},
    )
    
    # Mineral Cost - resource requirement!! economy management crucial!!
    mineral_cost: int = Field(
        ...,  # required!! 모든 유닛은 cost가 있음!!
        description="Mineral cost to produce this unit",
        ge=0,  # non-negative!! free units도 0 cost로 표현!!
        json_schema_extra={"example": 50},
    )
    
    # Gas Cost - secondary resource!! high-tech units require gas~~
    gas_cost: int = Field(
        0,  # default 0!! basic units는 gas 불필요!!
        description="Vespene gas cost to produce this unit",
        ge=0,  # non-negative!! gas cost는 0 이상!!
        json_schema_extra={"example": 0},
    )
    
    # Supply Cost - population limit management!! army size control!!
    supply_cost: int = Field(
        ...,  # required!! supply management는 strategic element!!
        description="Supply cost (population)",
        gt=0,  # must be positive!! 모든 유닛은 supply 차지!!
        json_schema_extra={"example": 1},
    )
    
    # Build Time - production duration!! timing strategy에 영향!!
    build_time: int = Field(
        ...,  # required!! production timing은 게임 밸런스의 핵심!!
        description="Build time in seconds",
        gt=0,  # must be positive!! instant production은 없음!!
        json_schema_extra={"example": 24},
    )
    
    # Description - lore and tactical info!! flavor text and usage guide~~
    description: Optional[str] = Field(
        None,  # optional!! 설명은 있으면 좋지만 필수는 아님~~
        description="Unit description and lore",
        max_length=500,  # reasonable limit!! 너무 길면 UI 문제!!
        json_schema_extra={"example": "Versatile Terran infantry unit armed with C-14 rifle"},
    )


class UnitCreate(UnitBase):
    """Unit creation payload!! new unit을 system에 register!!"""
    pass


class UnitUpdate(BaseModel):
    """Unit update payload!! balance patches and modifications~~"""
    name: Optional[UnitNameType] = Field(None, description="Unit name")
    race: Optional[Race] = Field(None, description="Unit race")
    unit_type: Optional[UnitType] = Field(None, description="Unit type")
    hit_points: Optional[int] = Field(None, description="Hit points", gt=0)
    shields: Optional[int] = Field(None, description="Shield points", ge=0)
    attack_damage: Optional[int] = Field(None, description="Attack damage", ge=0)
    armor: Optional[int] = Field(None, description="Armor value", ge=0)
    movement_speed: Optional[Decimal] = Field(None, description="Movement speed", gt=0, decimal_places=2)
    mineral_cost: Optional[int] = Field(None, description="Mineral cost", ge=0)
    gas_cost: Optional[int] = Field(None, description="Gas cost", ge=0)
    supply_cost: Optional[int] = Field(None, description="Supply cost", gt=0)
    build_time: Optional[int] = Field(None, description="Build time", gt=0)
    description: Optional[str] = Field(None, description="Unit description", max_length=500)


class UnitRead(UnitBase):
    """Server representation with metadata!! client에게 return되는 complete data!!"""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Unit ID",
        json_schema_extra={"example": "12345678-1234-4123-8123-123456789012"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC)",
        json_schema_extra={"example": "2025-09-14T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC)",
        json_schema_extra={"example": "2025-09-14T12:00:00Z"},
    )
