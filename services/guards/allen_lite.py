from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import re

@dataclass
class Interval: start:int; end:int

def relation(a:Interval,b:Interval)->str:
 if a.end<b.start: return 'before'
 if a.start==b.start and a.end==b.end: return 'equal'
 if a.start<b.start<a.end<b.end: return 'overlaps'
 if b.start<=a.start and a.end<=b.end: return 'during'
 if a.end==b.start: return 'meets'
 if a.start>b.end: return 'after'
 return 'unknown'

def path_consistent(a:Interval,b:Interval,c:Interval)->bool:
 rab=relation(a,b); rbc=relation(b,c); rac=relation(a,c)
 if rab in ('before','meets') and rbc in ('before','meets'): return rac in ('before','meets')
 if rab=='during' and rbc=='during': return rac=='during'
 return True

def validate_entity_consistency(entity: Dict[str, Any]) -> List[str]:
    """Validate entity consistency using Allen Lite principles"""
    issues = []
    
    # Basic field validation
    if not entity.get('id'):
        issues.append("Entity ID is required")
    
    if not entity.get('name'):
        issues.append("Entity name is required")
    
    if not entity.get('type'):
        issues.append("Entity type is required")
    
    # Type-specific validation
    entity_type = entity.get('type')
    traits = entity.get('traits', {})
    
    if entity_type == 'Character':
        # Characters should have basic traits
        if not traits.get('age') and not traits.get('description'):
            issues.append("Character entities should have age or description")
    
    elif entity_type == 'Place':
        # Places should have location information
        if not traits.get('location') and not traits.get('coordinates'):
            issues.append("Place entities should have location or coordinates")
    
    elif entity_type == 'Event':
        # Events should have temporal information
        if not traits.get('date') and not traits.get('timeframe'):
            issues.append("Event entities should have date or timeframe")
    
    # World ID validation
    world_id = entity.get('world_id')
    if world_id and not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', world_id):
        issues.append("Invalid world_id format")
    
    # Name validation
    name = entity.get('name', '')
    if len(name) > 200:
        issues.append("Entity name too long (max 200 characters)")
    
    if len(name) < 1:
        issues.append("Entity name cannot be empty")
    
    return issues
