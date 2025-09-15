from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse

# Import existing models (Person, Address, Health)
from models.health import Health, make_health
from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate

# Import new StarCraft models!! 스타크래프트 테마의 새로운 모델들!!
from models.unit import UnitCreate, UnitRead, UnitUpdate, Race, UnitType
from models.skill import SkillCreate, SkillRead, SkillUpdate, SkillCategory, TargetType

# =========================================================================
# FastAPI Application - 스타크래프트 유닛 & 스킬 관리 마이크로서비스!!
# - Person/Address는 기존 기능 유지!! (기본 제공 모델들)
# - Unit/Skill은 새로운 StarCraft 테마!! (과제 요구사항)
# - RESTful API design principles 완벽 적용!! 
# - 실시간 전략 게임의 데이터 관리 시스템!! super cool~~~
# =========================================================================

app = FastAPI(
    title="StarCraft Units & Skills Microservice",  # 스타크래프트 테마!! 
    description="A microservice for managing StarCraft units and skills, plus basic person/address management",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI!! 
    redoc_url="/redoc"  # ReDoc UI!!
)

# =========================================================================
# In-Memory "Databases" - 개발/테스트용 임시 저장소!!
# Production에서는 PostgreSQL, MongoDB 등 real database 사용!!
# 각 resource별로 separate dictionary!! clean separation~~
# =========================================================================

# Existing data stores!! 기존 Person/Address 관리!!
persons: Dict[UUID, PersonRead] = {}  # Person storage!! 
addresses: Dict[UUID, AddressRead] = {}  # Address storage!!

# New StarCraft data stores!! 새로운 게임 데이터 관리!!
units: Dict[UUID, UnitRead] = {}  # Unit storage!! 스타크래프트 유닛들!!
skills: Dict[UUID, SkillRead] = {}  # Skill storage!! 스타크래프트 스킬들!!

# =========================================================================
# Health Check Endpoints - 시스템 상태 확인!! monitoring essential~~
# Load balancer와 monitoring tools에서 사용!! uptime tracking!!
# =========================================================================

@app.get("/health", response_model=Health)
def get_health_no_path(echo: Optional[str] = Query(None, description="Optional echo string")):
    # Fixed Python 3.9 compatibility!! str | None → Optional[str]!!
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: Optional[str] = Query(None, description="Optional echo string"),
):
    # Fixed Python 3.9 compatibility!! str | None → Optional[str]!!
    return make_health(echo=echo, path_echo=path_echo)

# =========================================================================
# Person Endpoints - 기존 기능 유지!! 사람 정보 관리 CRUD!!
# 기본 제공된 모델이지만 여전히 중요한 기능!! user management~~
# =========================================================================

@app.post("/persons", response_model=PersonRead, status_code=201)
def create_person(person: PersonCreate):
    # UNI uniqueness validation!! Columbia University ID 중복 방지!!
    for existing_person in persons.values():
        if existing_person.uni == person.uni:
            raise HTTPException(status_code=400, detail="Person with this UNI already exists")
    
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by UNI"),
    email: Optional[str] = Query(None, description="Filter by email"),
):
    results = list(persons.values())
    if uni: results = [p for p in results if p.uni == uni]
    if email: results = [p for p in results if p.email == email]
    return results

@app.get("/persons/{person_id}", response_model=PersonRead)
def get_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons[person_id]

@app.patch("/persons/{person_id}", response_model=PersonRead)
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # UNI uniqueness validation on update!!
    if update.uni is not None:
        for pid, existing_person in persons.items():
            if pid != person_id and existing_person.uni == update.uni:
                raise HTTPException(status_code=400, detail="Person with this UNI already exists")
    
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    stored["updated_at"] = datetime.utcnow()
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]

@app.delete("/persons/{person_id}")
def delete_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    del persons[person_id]
    return {"message": "Person deleted successfully"}

# =========================================================================
# Address Endpoints - 기존 기능 유지!! 주소 정보 관리 CRUD!!
# Person과 연동되는 중요한 reference data!! location management~~
# =========================================================================

@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    # Address ID uniqueness validation!!
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    
    address_read = AddressRead(**address.model_dump())
    addresses[address_read.id] = address_read
    return address_read

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())
    if city: results = [a for a in results if a.city.lower() == city.lower()]
    if country: results = [a for a in results if a.country.lower() == country.lower()]
    return results

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    stored["updated_at"] = datetime.utcnow()
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

@app.delete("/addresses/{address_id}")
def delete_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    del addresses[address_id]
    return {"message": "Address deleted successfully"}

# =========================================================================
# Unit Endpoints - 스타크래프트 유닛 관리 CRUD!! 새로운 핵심 기능!!
# 프로토스, 테란, 저그 유닛들의 complete stats management!!
# Game balance와 strategic planning을 위한 essential data!!
# =========================================================================

@app.post("/units", response_model=UnitRead, status_code=201)
def create_unit(unit: UnitCreate):
    # Unit name uniqueness validation per race!! 종족별 유닛명 중복 방지!!
    for existing_unit in units.values():
        if existing_unit.name == unit.name and existing_unit.race == unit.race:
            raise HTTPException(status_code=400, detail=f"{unit.race.value} unit with name '{unit.name}' already exists")
    
    unit_read = UnitRead(**unit.model_dump())
    units[unit_read.id] = unit_read
    return unit_read

@app.get("/units", response_model=List[UnitRead])
def list_units(
    race: Optional[Race] = Query(None, description="Filter by race (protoss/terran/zerg)"),
    unit_type: Optional[UnitType] = Query(None, description="Filter by unit type"),
    name: Optional[str] = Query(None, description="Filter by unit name (partial match)"),
    min_cost: Optional[int] = Query(None, description="Minimum mineral cost filter"),
    max_cost: Optional[int] = Query(None, description="Maximum mineral cost filter"),
):
    # Advanced filtering!! strategic unit analysis를 위한 다양한 filter options!!
    results = list(units.values())
    
    if race: results = [u for u in results if u.race == race]
    if unit_type: results = [u for u in results if u.unit_type == unit_type]
    if name: results = [u for u in results if name.lower() in u.name.lower()]
    if min_cost is not None: results = [u for u in results if u.mineral_cost >= min_cost]
    if max_cost is not None: results = [u for u in results if u.mineral_cost <= max_cost]
    
    return results

@app.get("/units/{unit_id}", response_model=UnitRead)
def get_unit(unit_id: UUID):
    if unit_id not in units:
        raise HTTPException(status_code=404, detail="Unit not found")
    return units[unit_id]

@app.patch("/units/{unit_id}", response_model=UnitRead)
def update_unit(unit_id: UUID, update: UnitUpdate):
    # Balance patch endpoint!! 게임 밸런스 조정을 위한 unit stat 수정!!
    if unit_id not in units:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Name uniqueness validation on update!! 수정 시에도 중복 방지!!
    if update.name is not None and update.race is not None:
        for uid, existing_unit in units.items():
            if uid != unit_id and existing_unit.name == update.name and existing_unit.race == update.race:
                raise HTTPException(status_code=400, detail=f"{update.race.value} unit with name '{update.name}' already exists")
    
    stored = units[unit_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    stored["updated_at"] = datetime.utcnow()
    units[unit_id] = UnitRead(**stored)
    return units[unit_id]

@app.delete("/units/{unit_id}")
def delete_unit(unit_id: UUID):
    if unit_id not in units:
        raise HTTPException(status_code=404, detail="Unit not found")
    del units[unit_id]
    return {"message": "Unit deleted successfully"}

# =========================================================================
# Skill Endpoints - 스타크래프트 스킬/능력 관리 CRUD!! 전술적 핵심 요소!!
# 유닛들의 special abilities, spells, upgrades complete management!!
# Micro management와 strategic depth를 위한 essential system!!
# =========================================================================

@app.post("/skills", response_model=SkillRead, status_code=201)
def create_skill(skill: SkillCreate):
    # Skill name uniqueness validation!! 스킬명 중복 방지로 confusion 방지!!
    for existing_skill in skills.values():
        if existing_skill.name == skill.name:
            raise HTTPException(status_code=400, detail=f"Skill with name '{skill.name}' already exists")
    
    skill_read = SkillRead(**skill.model_dump())
    skills[skill_read.id] = skill_read
    return skill_read

@app.get("/skills", response_model=List[SkillRead])
def list_skills(
    category: Optional[SkillCategory] = Query(None, description="Filter by skill category"),
    target_type: Optional[TargetType] = Query(None, description="Filter by target type"),
    name: Optional[str] = Query(None, description="Filter by skill name (partial match)"),
    min_damage: Optional[int] = Query(None, description="Minimum base damage filter"),
    max_energy: Optional[int] = Query(None, description="Maximum energy cost filter"),
    upgrade_level: Optional[int] = Query(None, description="Filter by upgrade level"),
):
    # Strategic skill analysis!! tactical planning을 위한 comprehensive filtering!!
    results = list(skills.values())
    
    if category: results = [s for s in results if s.category == category]
    if target_type: results = [s for s in results if s.target_type == target_type]
    if name: results = [s for s in results if name.lower() in s.name.lower()]
    if min_damage is not None: results = [s for s in results if s.base_damage >= min_damage]
    if max_energy is not None: results = [s for s in results if s.energy_cost <= max_energy]
    if upgrade_level is not None: results = [s for s in results if s.upgrade_level == upgrade_level]
    
    return results

@app.get("/skills/{skill_id}", response_model=SkillRead)
def get_skill(skill_id: UUID):
    if skill_id not in skills:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skills[skill_id]

@app.patch("/skills/{skill_id}", response_model=SkillRead)
def update_skill(skill_id: UUID, update: SkillUpdate):
    # Skill balance adjustment!! 스킬 밸런스 패치를 위한 수정 기능!!
    if skill_id not in skills:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Name uniqueness validation on update!!
    if update.name is not None:
        for sid, existing_skill in skills.items():
            if sid != skill_id and existing_skill.name == update.name:
                raise HTTPException(status_code=400, detail=f"Skill with name '{update.name}' already exists")
    
    stored = skills[skill_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    stored["updated_at"] = datetime.utcnow()
    skills[skill_id] = SkillRead(**stored)
    return skills[skill_id]

@app.delete("/skills/{skill_id}")
def delete_skill(skill_id: UUID):
    if skill_id not in skills:
        raise HTTPException(status_code=404, detail="Skill not found")
    del skills[skill_id]
    return {"message": "Skill deleted successfully"}

# =========================================================================
# Application Startup Message - 서버 시작 확인!! development convenience~~
# =========================================================================

if __name__ == "__main__":
    import uvicorn
    print("🎮 Starting StarCraft Units & Skills Microservice!! 🎮")
    print("📊 Swagger UI: http://localhost:8000/docs")
    print("📖 ReDoc UI: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)