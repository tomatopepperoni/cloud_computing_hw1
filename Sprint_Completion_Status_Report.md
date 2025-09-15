# Sprint Completion Status Report

**Student Name:** [Your Name]
**Sprint Number:** Sprint 0
**Duration:** September 10, 2025 – September 14, 2025
**Report Date:** September 14, 2025

## 1. Sprint Goal 🎯

**Defined Goal:**

1. Clone Professor Ferguson's Simple Microservices Repository.
2. Create a project that is my version using two different resources.
   a. Copy the structure of Professor Ferguson's repository
   b. Define two models.
   c. Implement "API first" definition by implementing placeholder routes for each resource:
   i. GET /<resource>
   ii. POST /<resource>
   iii. GET /<resource>/{id}
   iv. PUT /<resource>/{id}
   v. DELETE /<resource>/{id}
   d. Annotate models and paths to autogenerate OpenAPI document.
   e. Tested OpenAPI document dispatching to methods.

**Outcome:** Achieved
**Notes:** Successfully implemented StarCraft Unit and Skill models with full CRUD operations and comprehensive annotations. Created a gaming-themed microservice for managing RTS game data.

## 2. Completed Work ✅

### Resource 1 - Unit Model (StarCraft Units)

```python
class UnitBase(BaseModel):
    name: UnitNameType = Field(..., description="Unit name (e.g., Marine, Zealot, Zergling)")
    race: Race = Field(..., description="Unit race (Protoss/Terran/Zerg)")
    unit_type: UnitType = Field(..., description="Unit type classification")
    hit_points: int = Field(..., description="Maximum hit points", gt=0)
    shields: int = Field(0, description="Shield points (Protoss units only)", ge=0)
    attack_damage: int = Field(0, description="Base attack damage", ge=0)
    armor: int = Field(0, description="Armor value for damage reduction", ge=0)
    movement_speed: Decimal = Field(..., description="Movement speed", gt=0, decimal_places=2)
    mineral_cost: int = Field(..., description="Mineral cost to produce", ge=0)
    gas_cost: int = Field(0, description="Vespene gas cost", ge=0)
    supply_cost: int = Field(..., description="Supply cost (population)", gt=0)
    build_time: int = Field(..., description="Build time in seconds", gt=0)
    description: Optional[str] = Field(None, description="Unit description", max_length=500)
```

### Resource 2 - Skill Model (StarCraft Abilities)

```python
class SkillBase(BaseModel):
    name: SkillNameType = Field(..., description="Skill name (e.g., Psionic Storm, Stim Pack)")
    category: SkillCategory = Field(..., description="Skill category for tactical classification")
    target_type: TargetType = Field(..., description="Target type for skill usage")
    energy_cost: int = Field(..., description="Energy/Mana cost to cast", ge=0)
    cooldown: Decimal = Field(..., description="Cooldown time in seconds", ge=0, decimal_places=1)
    cast_range: int = Field(..., description="Maximum casting range", ge=0)
    area_of_effect: int = Field(0, description="AoE radius (0 for single target)", ge=0)
    base_damage: int = Field(0, description="Base damage (0 for non-damage skills)", ge=0)
    duration: Decimal = Field(0.0, description="Effect duration (0 for instant)", ge=0, decimal_places=1)
    upgrade_level: int = Field(1, description="Skill upgrade level", ge=1, le=5)
    prerequisites: Optional[str] = Field(None, description="Required buildings/upgrades", max_length=200)
    description: Optional[str] = Field(None, description="Detailed skill description", max_length=1000)
```

### main.py Routes

```python
# Unit Endpoints - StarCraft Unit Management
@app.post("/units", response_model=UnitRead, status_code=201)
def create_unit(unit: UnitCreate):
    # Unit name uniqueness validation per race
    for existing_unit in units.values():
        if existing_unit.name == unit.name and existing_unit.race == unit.race:
            raise HTTPException(status_code=400, detail=f"{unit.race.value} unit with name '{unit.name}' already exists")

    unit_read = UnitRead(**unit.model_dump())
    units[unit_read.id] = unit_read
    return unit_read

@app.get("/units", response_model=List[UnitRead])
def list_units(race: Optional[Race] = Query(None), unit_type: Optional[UnitType] = Query(None)):
    results = list(units.values())
    if race: results = [u for u in results if u.race == race]
    if unit_type: results = [u for u in results if u.unit_type == unit_type]
    return results

@app.get("/units/{unit_id}", response_model=UnitRead)
def get_unit(unit_id: UUID):
    if unit_id not in units:
        raise HTTPException(status_code=404, detail="Unit not found")
    return units[unit_id]

@app.patch("/units/{unit_id}", response_model=UnitRead)
def update_unit(unit_id: UUID, update: UnitUpdate):
    if unit_id not in units:
        raise HTTPException(status_code=404, detail="Unit not found")
    stored = units[unit_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    units[unit_id] = UnitRead(**stored)
    return units[unit_id]

@app.delete("/units/{unit_id}")
def delete_unit(unit_id: UUID):
    if unit_id not in units:
        raise HTTPException(status_code=404, detail="Unit not found")
    del units[unit_id]
    return {"message": "Unit deleted successfully"}

# Skill Endpoints - StarCraft Skill/Ability Management
@app.post("/skills", response_model=SkillRead, status_code=201)
def create_skill(skill: SkillCreate):
    # Skill name uniqueness validation
    for existing_skill in skills.values():
        if existing_skill.name == skill.name:
            raise HTTPException(status_code=400, detail=f"Skill with name '{skill.name}' already exists")

    skill_read = SkillRead(**skill.model_dump())
    skills[skill_read.id] = skill_read
    return skill_read

@app.get("/skills", response_model=List[SkillRead])
def list_skills(category: Optional[SkillCategory] = Query(None), target_type: Optional[TargetType] = Query(None)):
    results = list(skills.values())
    if category: results = [s for s in results if s.category == category]
    if target_type: results = [s for s in results if s.target_type == target_type]
    return results

@app.get("/skills/{skill_id}", response_model=SkillRead)
def get_skill(skill_id: UUID):
    if skill_id not in skills:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skills[skill_id]

@app.patch("/skills/{skill_id}", response_model=SkillRead)
def update_skill(skill_id: UUID, update: SkillUpdate):
    if skill_id not in skills:
        raise HTTPException(status_code=404, detail="Skill not found")
    stored = skills[skill_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    skills[skill_id] = SkillRead(**stored)
    return skills[skill_id]

@app.delete("/skills/{skill_id}")
def delete_skill(skill_id: UUID):
    if skill_id not in skills:
        raise HTTPException(status_code=404, detail="Skill not found")
    del skills[skill_id]
    return {"message": "Skill deleted successfully"}
```

### OpenAPI Document (Partial)

- Available at http://localhost:8000/docs
- All endpoints properly documented with Pydantic models
- Interactive API documentation with request/response schemas
- Automatic validation and error handling
- StarCraft-themed models with comprehensive field descriptions
- Enum support for Race, UnitType, SkillCategory, TargetType

### Link to Recording of Demo

[Insert your demo video link here - showing StarCraft units and skills CRUD operations]

### Link to GitHub Repository

https://github.com/tomatopepperoni/cloud_computing_hw1

## 3. Incomplete Work ❌

**Items planned but not completed:** None - All sprint goals successfully achieved!!

**Carryover to Next Sprint:** No

## 4. Key Metrics 📊

Note: Ignore this section

**Planned vs. Completed Points:** [e.g., 40 planned / 35 completed]
**Burndown Chart:** [Attach image if available]
**Defects Identified:** [Number + Severity]

## 5. Risks & Blockers ⚠

Note: Ignore this section

- [Risk/Issue] – [Impact] – [Mitigation/Resolution]
- [Dependency on X team] – [Impact on timeline]

## 6. Team Feedback 💬

Note: Ignore this section

**What Went Well:**

- [Positive note 1]
- [Positive note 2]

**What Could Be Improved:**

- [Improvement area 1]
- [Improvement area 2]

## 7. Next Steps 🔜

Note: Ignore this section

**Upcoming Sprint Goal (Draft):** [Proposed goal]
**Focus Areas:** [e.g., technical debt, new feature, stabilization]
**Planned Dependencies:** [Cross-team items, external blockers]
