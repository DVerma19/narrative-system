# app/schemas.py

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# =============================================================================
# BASE CONFIG
# =============================================================================

class ORMModel(BaseModel):
    class Config:
        from_attributes = True


# =============================================================================
# ENUMS
# =============================================================================

class EntityType(str, Enum):
    CHARACTER = "character"
    LOCATION = "location"
    OBJECT = "object"
    PSYCHOLOGICAL_STATE = "psychological_state"
    EVENT = "event"
    RELATIONSHIP = "relationship"
    FUNCTION = "function"


class RelationshipType(str, Enum):
    PARTICIPANT = "participant"
    STATE_OF = "state_of"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    LOCATION = "location"
    INVOLVES = "involves"
    USES = "uses"


class SceneStatus(str, Enum):
    DRAFT = "draft"
    REVISED = "revised"
    FINAL = "final"


class PromiseStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    ABANDONED = "abandoned"


class ArcType(str, Enum):
    CHARACTER = "character"
    PLOT = "plot"


class ArcStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class VocabTermType(str, Enum):
    CLASS = "class"
    PROPERTY = "property"


# =============================================================================
# ENTITY
# =============================================================================

class EntityBase(BaseModel):
    type: EntityType
    name: str = Field(..., max_length=255)
    state: Dict[str, Any] = Field(default_factory=dict)


class EntityCreate(EntityBase):
    pass


class EntityUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    state: Optional[Dict[str, Any]] = None


class EntityResponse(EntityBase, ORMModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


# =============================================================================
# RELATIONSHIP
# =============================================================================

class RelationshipBase(BaseModel):
    source_id: UUID
    target_id: UUID
    type: RelationshipType
    strength: int = Field(..., ge=1, le=10)
    state: Dict[str, Any] = Field(default_factory=dict)


class RelationshipCreate(RelationshipBase):
    pass


class RelationshipUpdate(BaseModel):
    strength: Optional[int] = Field(None, ge=1, le=10)
    state: Optional[Dict[str, Any]] = None


class RelationshipResponse(RelationshipBase, ORMModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


# =============================================================================
# SCENE
# =============================================================================

class SceneBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    chapter_number: Optional[int]
    order_in_chapter: int = 1
    status: SceneStatus = SceneStatus.DRAFT
    prose: str = ""
    word_count: int = 0
    pov_character_id: Optional[UUID]


class SceneCreate(SceneBase):
    pass


class SceneUpdate(BaseModel):
    title: Optional[str] = None
    chapter_number: Optional[int] = None
    order_in_chapter: Optional[int] = None
    status: Optional[SceneStatus] = None
    prose: Optional[str] = None
    word_count: Optional[int] = None
    pov_character_id: Optional[UUID] = None


class SceneResponse(SceneBase, ORMModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


# =============================================================================
# EVENT
# =============================================================================

class EventBase(BaseModel):
    scene_id: Optional[UUID]
    type: str  # keep flexible if AI-generated
    initiator_id: Optional[UUID]
    description: Optional[str]
    state_changes: List[Dict[str, Any]] = Field(default_factory=list)
    witnesses: List[UUID] = Field(default_factory=list)


class EventCreate(EventBase):
    pass


class EventResponse(EventBase, ORMModel):
    id: UUID
    created_at: datetime


# =============================================================================
# PROMISE
# =============================================================================

class PromiseBase(BaseModel):
    description: str
    setup_event_id: Optional[UUID]
    status: PromiseStatus = PromiseStatus.OPEN
    resolution_event_id: Optional[UUID]
    target_scene: Optional[str] = Field(None, max_length=255)


class PromiseCreate(PromiseBase):
    pass


class PromiseUpdate(BaseModel):
    status: Optional[PromiseStatus]
    resolution_event_id: Optional[UUID]
    target_scene: Optional[str]


class PromiseResponse(PromiseBase, ORMModel):
    id: UUID
    created_at: datetime


# =============================================================================
# VOCABULARY
# =============================================================================

class VocabularyBase(BaseModel):
    term_type: VocabTermType
    uri: str = Field(..., max_length=500)
    local_name: str = Field(..., max_length=100)
    label: str = Field(..., max_length=200)
    description: Optional[str]
    domain: Optional[str]
    range: Optional[str]
    category: Optional[str]


class VocabularyCreate(VocabularyBase):
    pass


class VocabularyResponse(VocabularyBase, ORMModel):
    id: UUID
    created_at: datetime


# =============================================================================
# ARC
# =============================================================================

class ArcBase(BaseModel):
    name: str = Field(..., max_length=255)
    type: ArcType
    description: Optional[str]
    status: ArcStatus = ArcStatus.ACTIVE


class ArcCreate(ArcBase):
    pass


class ArcUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    status: Optional[ArcStatus]


class ArcResponse(ArcBase, ORMModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


class CharacterArcBase(BaseModel):
    character_id: UUID
    arc_id: UUID
    role: Optional[str]
    progress: int = Field(0, ge=0, le=100)


class CharacterArcCreate(CharacterArcBase):
    pass


class CharacterArcResponse(CharacterArcBase, ORMModel):
    pass


# =============================================================================
# MEMORY
# =============================================================================

class MemoryBase(BaseModel):
    character_id: UUID
    event_id: Optional[UUID]
    clarity: int = Field(100, ge=0, le=100)
    emotional_weight: int = Field(5, ge=1, le=10)
    last_recalled_at: Optional[datetime]
    notes: Optional[str]


class MemoryCreate(MemoryBase):
    pass


class MemoryUpdate(BaseModel):
    clarity: Optional[int] = Field(None, ge=0, le=100)
    emotional_weight: Optional[int] = Field(None, ge=1, le=10)
    last_recalled_at: Optional[datetime]
    notes: Optional[str]


class MemoryResponse(MemoryBase, ORMModel):
    id: UUID
    created_at: datetime


# =============================================================================
# THEMES
# =============================================================================

class ThemeBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str]


class ThemeCreate(ThemeBase):
    pass


class ThemeResponse(ThemeBase, ORMModel):
    id: UUID


class SceneThemeBase(BaseModel):
    scene_id: UUID
    theme_id: UUID
    relevance: int = Field(5, ge=1, le=10)


class SceneThemeCreate(SceneThemeBase):
    pass


class SceneThemeResponse(SceneThemeBase, ORMModel):
    pass


# =============================================================================
# TIMELINES
# =============================================================================

class TimelineBase(BaseModel):
    name: str = Field(..., max_length=100)
    is_prime: bool = False
    divergence_event_id: Optional[UUID]
    status: str = "active"


class TimelineCreate(TimelineBase):
    pass


class TimelineResponse(TimelineBase, ORMModel):
    id: UUID
    created_at: datetime


class CharacterTimelineBase(BaseModel):
    character_id: UUID
    timeline_id: UUID


class CharacterTimelineCreate(CharacterTimelineBase):
    pass


class CharacterTimelineResponse(CharacterTimelineBase, ORMModel):
    joined_at: datetime


# =============================================================================
# USER / PROJECT
# =============================================================================

class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: Optional[str]


class UserCreate(UserBase):
    pass


class UserResponse(UserBase, ORMModel):
    id: UUID
    created_at: datetime


class ProjectBase(BaseModel):
    user_id: UUID
    name: str = Field(..., max_length=255)
    description: Optional[str]


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


class ProjectResponse(ProjectBase, ORMModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


# =============================================================================
# GENERATION
# =============================================================================

class GenerateRequest(BaseModel):
    instruction: str
    scene_id: Optional[UUID]
    initiator_id: Optional[UUID]
    auto_log: bool = False
    append_prose: bool = False
    location_context: Optional[str]


class GenerateResponse(BaseModel):
    prose: str
    suggested_state_changes: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# SNAPSHOT
# =============================================================================

class SnapshotResponse(BaseModel):
    entities: List[EntityResponse]
    relationships: List[RelationshipResponse]
    open_promises: List[PromiseResponse]
    recent_scenes: List[SceneResponse]
    active_location: Optional[str]