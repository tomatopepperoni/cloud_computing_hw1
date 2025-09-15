from __future__ import annotations

from typing import Optional, Annotated
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, StringConstraints

# =========================================================================
# Skill Model: 스타크래프트 스킬/능력 관리 시스템의 core domain model!!
# - 유닛들의 special abilities, spells, upgrades를 관리!!
# - Mana/Energy cost, cooldown, damage/effect 등을 tracking!!
# - Strategic gameplay의 핵심 요소!! micro management essential~~~
# =========================================================================

# Skill Category - 스킬의 용도별 분류!! tactical decision making에 중요~~
class SkillCategory(str, Enum):
    OFFENSIVE = "offensive"      # 공격 스킬!! damage dealing abilities!!
    DEFENSIVE = "defensive"      # 방어 스킬!! protection and healing!!
    UTILITY = "utility"          # 유틸리티!! movement, detection, economy!!
    BUFF = "buff"               # 버프!! stat enhancement abilities!!
    DEBUFF = "debuff"           # 디버프!! enemy weakening effects!!
    SUMMON = "summon"           # 소환!! creating additional units!!

# Target Type - 스킬의 대상 분류!! targeting system crucial!!
class TargetType(str, Enum):
    SELF = "self"               # 자기 자신!! self-enhancement!!
    SINGLE_ENEMY = "single_enemy"      # 단일 적!! focused attack!!
    SINGLE_ALLY = "single_ally"        # 단일 아군!! targeted support!!
    AREA_ENEMY = "area_enemy"          # 적 범위!! AoE damage!!
    AREA_ALLY = "area_ally"            # 아군 범위!! group support!!
    GROUND_TARGET = "ground_target"    # 지면 대상!! positional abilities!!

# Skill Name Type Definition - standardized skill naming!! consistency~~
SkillNameType = Annotated[str, StringConstraints(min_length=1, max_length=100)]


class SkillBase(BaseModel):
    """
    ===================================================================
    SkillBase: 스타크래프트 스킬의 basic attributes를 정의하는 base model!! 
    - RTS game의 tactical depth를 제공하는 ability system!!
    - Cost-benefit analysis를 위한 detailed stat tracking!!
    - Strategic decision making을 위한 comprehensive skill data!!
    ===================================================================
    """
    # Skill Name - required!! each skill has unique identity and recognition!!
    name: SkillNameType = Field(
        ...,  # required field!! 스킬 이름은 필수!!
        description="Skill name (e.g., Psionic Storm, Stim Pack, Plague)",
        json_schema_extra={"example": "Psionic Storm"},
    )
    
    # Skill Category - tactical classification!! strategy planning에 essential!!
    category: SkillCategory = Field(
        ...,  # required!! 스킬 카테고리는 전략적 분류에 필수!!
        description="Skill category for tactical classification",
        json_schema_extra={"example": "offensive"},
    )
    
    # Target Type - determines how skill can be used!! targeting mechanics!!
    target_type: TargetType = Field(
        ...,  # required!! 타겟팅 방식은 사용법 결정에 crucial!!
        description="Target type for skill usage",
        json_schema_extra={"example": "area_enemy"},
    )
    
    # Mana/Energy Cost - resource consumption!! ability usage limitation~~
    energy_cost: int = Field(
        ...,  # required!! 에너지 비용은 스킬 밸런스의 핵심!!
        description="Energy/Mana cost to cast this skill",
        ge=0,  # non-negative!! 0 cost skills도 있음 (passive abilities)!!
        json_schema_extra={"example": 75},
    )
    
    # Cooldown - usage frequency limitation!! prevents skill spam~~
    cooldown: Decimal = Field(
        ...,  # required!! 쿨다운은 스킬 밸런스에 essential!!
        description="Cooldown time in seconds",
        ge=0,  # non-negative!! 0 cooldown = instant reuse possible!!
        decimal_places=1,  # precision for timing!! 1.5초 같은 값들!!
        json_schema_extra={"example": 4.0},
    )
    
    # Cast Range - distance limitation!! positioning strategy에 영향!!
    cast_range: int = Field(
        ...,  # required!! 사거리는 tactical positioning에 crucial!!
        description="Maximum casting range",
        ge=0,  # non-negative!! 0 range = melee/self-cast only!!
        json_schema_extra={"example": 9},
    )
    
    # Area of Effect - impact radius!! determines skill effectiveness scope~~
    area_of_effect: int = Field(
        0,  # default 0!! single target skills는 AoE 없음!!
        description="Area of effect radius (0 for single target)",
        ge=0,  # non-negative!! AoE는 0 이상!!
        json_schema_extra={"example": 3},
    )
    
    # Base Damage - offensive capability!! combat effectiveness measurement~~
    base_damage: int = Field(
        0,  # default 0!! utility skills는 damage 없을 수 있음!!
        description="Base damage dealt by skill (0 for non-damage skills)",
        ge=0,  # non-negative!! negative damage = healing effect!!
        json_schema_extra={"example": 112},
    )
    
    # Duration - effect persistence!! temporal impact management~~
    duration: Decimal = Field(
        0.0,  # default 0!! instant effects는 duration 없음!!
        description="Effect duration in seconds (0 for instant effects)",
        ge=0,  # non-negative!! negative duration은 말이 안됨!!
        decimal_places=1,  # precision for timing!! 2.5초 같은 값들!!
        json_schema_extra={"example": 4.0},
    )
    
    # Upgrade Level - skill enhancement stage!! tech progression tracking~~
    upgrade_level: int = Field(
        1,  # default level 1!! basic skill level!!
        description="Skill upgrade level (1-3 typically)",
        ge=1,  # minimum level 1!! 0 level은 skill 없음을 의미!!
        le=5,  # reasonable maximum!! 너무 높은 level은 complexity 증가!!
        json_schema_extra={"example": 1},
    )
    
    # Prerequisites - tech requirements!! research tree management~~
    prerequisites: Optional[str] = Field(
        None,  # optional!! basic skills는 prerequisite 없을 수 있음~~
        description="Required buildings/upgrades (comma-separated)",
        max_length=200,  # reasonable limit!! 너무 긴 prerequisite list 방지!!
        json_schema_extra={"example": "Templar Archives, High Templar"},
    )
    
    # Description - detailed explanation!! usage guide and lore~~
    description: Optional[str] = Field(
        None,  # optional!! 설명은 있으면 좋지만 필수는 아님~~
        description="Detailed skill description and effects",
        max_length=1000,  # comprehensive description 허용!! strategy guide 포함!!
        json_schema_extra={"example": "Creates a devastating psionic storm that deals massive damage to all units in the target area over time"},
    )


class SkillCreate(SkillBase):
    """Skill creation payload!! new ability를 system에 register!!"""
    pass


class SkillUpdate(BaseModel):
    """Skill update payload!! balance patches and ability modifications~~"""
    name: Optional[SkillNameType] = Field(None, description="Skill name")
    category: Optional[SkillCategory] = Field(None, description="Skill category")
    target_type: Optional[TargetType] = Field(None, description="Target type")
    energy_cost: Optional[int] = Field(None, description="Energy cost", ge=0)
    cooldown: Optional[Decimal] = Field(None, description="Cooldown time", ge=0, decimal_places=1)
    cast_range: Optional[int] = Field(None, description="Cast range", ge=0)
    area_of_effect: Optional[int] = Field(None, description="AoE radius", ge=0)
    base_damage: Optional[int] = Field(None, description="Base damage", ge=0)
    duration: Optional[Decimal] = Field(None, description="Effect duration", ge=0, decimal_places=1)
    upgrade_level: Optional[int] = Field(None, description="Upgrade level", ge=1, le=5)
    prerequisites: Optional[str] = Field(None, description="Prerequisites", max_length=200)
    description: Optional[str] = Field(None, description="Skill description", max_length=1000)


class SkillRead(SkillBase):
    """Server representation with metadata!! client에게 return되는 complete data!!"""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Skill ID",
        json_schema_extra={"example": "87654321-4321-4321-8765-876543210987"},
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
