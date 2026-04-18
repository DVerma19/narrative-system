import inspect
import schemas as schemas
from typing import get_origin, get_args
from types import UnionType
# =============================================================================
# CONFIG
# =============================================================================

EXCLUDE_MODELS = {"BaseModel", "ORMModel"}

# Map common Python types → Mermaid-friendly
TYPE_MAP = {
    "str": "string",
    "int": "int",
    "bool": "bool",
    "float": "float",
    "UUID": "UUID",
    "datetime": "datetime",
}


# =============================================================================
# HELPERS
# =============================================================================

def is_pydantic_model(obj):
    return inspect.isclass(obj) and hasattr(obj, "model_fields")


def get_models(module):
    return {
        name: obj
        for name, obj in inspect.getmembers(module)
        if is_pydantic_model(obj) and name not in EXCLUDE_MODELS
    }


def clean_type(annotation):
    """Convert Python typing → Mermaid-friendly type"""
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Optional[T]
    if origin is UnionType or str(origin).endswith("Union"):
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            return clean_type(non_none[0])

    # List[T]
    if origin in (list, list):
        return f"{clean_type(args[0])}[]"

    # Dict
    if origin in (dict, dict):
        return "dict"

    # Base type
    t = str(annotation)

    # Clean Python noise
    t = t.replace("<class '", "").replace("'>", "")
    t = t.replace("<enum '", "").replace("'>", "")
    t = t.replace("typing.", "")
    t = t.replace("schemas.", "")

    # Normalize common types
    if "uuid.UUID" in t:
        return "UUID"
    if "datetime.datetime" in t:
        return "datetime"

    short = t.split(".")[-1]
    return TYPE_MAP.get(short, short)


def format_fields(model):
    lines = []
    for name, field in model.model_fields.items():
        t = clean_type(field.annotation)
        lines.append(f"  {t} {name}")
    return "\n".join(lines)


# =============================================================================
# RELATIONSHIP DETECTION
# =============================================================================

def infer_relationships(models):
    relations = []

    for name, model in models.items():
        for fname, field in model.model_fields.items():
            t = str(field.annotation)

            # Direct model reference
            for target in models:
                if target in t and target != name:
                    relations.append((name, target, fname))

            # *_id heuristic → EntityResponse
            if fname.endswith("_id"):
                if "Entity" in models:
                    relations.append((name, "EntityResponse", fname))

    return relations


# =============================================================================
# BUILD MERMAID
# =============================================================================

def build_mermaid(models):
    lines = ["classDiagram"]

    # Classes
    for name, model in models.items():
        lines.append(f"class {name} {{")
        lines.append(format_fields(model))
        lines.append("}")

    # Relationships
    for src, tgt, label in infer_relationships(models):
        lines.append(f"{src} --> {tgt} : {label}")

    return "\n".join(lines)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    models = get_models(schemas)
    mermaid = build_mermaid(models)

    with open("schemas_diagram.md", "w", encoding="utf-8") as f:
        f.write("```mermaid\n")
        f.write(mermaid)
        f.write("\n```")

    print("✅ Mermaid diagram saved to schemas_diagram.md")