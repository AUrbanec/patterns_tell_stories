from sqlalchemy.orm import Session
from database import Episode, Entity, Detail, Relationship, Source
from typing import Dict, Any, List, Optional

class DataService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_episode(self, title: str, episode_url: str = None) -> Episode:
        """Create a new episode record."""
        episode = Episode(title=title, episode_url=episode_url)
        self.db.add(episode)
        self.db.commit()
        self.db.refresh(episode)
        return episode
    
    def update_episode_status(self, episode_id: int, status: str):
        """Update episode processing status."""
        episode = self.db.query(Episode).filter(Episode.id == episode_id).first()
        if episode:
            episode.status = status
            self.db.commit()
    
    def get_or_create_entity(self, name: str, entity_type: str, summary: str = None) -> Entity:
        """Get existing entity or create new one if it doesn't exist."""
        entity = self.db.query(Entity).filter(Entity.name == name).first()
        
        if not entity:
            entity = Entity(name=name, type=entity_type, summary=summary)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
        else:
            # Update summary if provided and current summary is empty
            if summary and not entity.summary:
                entity.summary = summary
                self.db.commit()
        
        return entity
    
    def create_source(self, episode_id: int, timestamp_start: int, timestamp_end: int, transcript_snippet: str = None) -> Source:
        """Create a new source record for a time segment."""
        source = Source(
            episode_id=episode_id,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
            transcript_snippet=transcript_snippet
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source
    
    def create_detail(self, entity_id: int, detail_text: str, source_id: int) -> Detail:
        """Create a new detail record for an entity."""
        detail = Detail(
            entity_id=entity_id,
            detail_text=detail_text,
            source_id=source_id
        )
        self.db.add(detail)
        self.db.commit()
        self.db.refresh(detail)
        return detail
    
    def create_relationship(self, source_entity_id: int, target_entity_id: int, description: str, source_id: int) -> Relationship:
        """Create a new relationship between two entities."""
        relationship = Relationship(
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            description=description,
            source_id=source_id
        )
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship
    
    def process_refined_analysis(self, refined_analysis: Dict[str, Any]):
        """Process the refined analysis result and store it in the database."""
        episode_id = refined_analysis["episode_id"]
        analysis = refined_analysis["analysis"]

        # Create a single source for the entire episode
        source = self.create_source(episode_id, timestamp_start=0, timestamp_end=-1)
        
        # Process entities
        entity_map = {}
        for entity_data in analysis.get("entities", []):
            entity = self.get_or_create_entity(
                name=entity_data["name"],
                entity_type=entity_data["type"],
                summary=entity_data.get("summary")
            )
            entity_map[entity_data["name"]] = entity
        
        # Process details
        for detail_data in analysis.get("details", []):
            entity_name = detail_data["entity"]
            if entity_name in entity_map:
                self.create_detail(
                    entity_id=entity_map[entity_name].id,
                    detail_text=detail_data["detail"],
                    source_id=source.id
                )
        
        # Process relationships
        for rel_data in analysis.get("relationships", []):
            source_name = rel_data["source"]
            target_name = rel_data["target"]
            
            if source_name in entity_map and target_name in entity_map:
                self.create_relationship(
                    source_entity_id=entity_map[source_name].id,
                    target_entity_id=entity_map[target_name].id,
                    description=rel_data["description"],
                    source_id=source.id
                )
    
    def get_episode_graph_data(self, episode_id: int) -> Dict[str, Any]:
        """Get all entities and relationships for an episode in graph format."""
        # Get all sources for this episode
        sources = self.db.query(Source).filter(Source.episode_id == episode_id).all()
        source_ids = [s.id for s in sources]
        
        if not source_ids:
            return {"nodes": [], "edges": []}
        
        # Get all entities that have details or relationships in this episode
        entities_with_details = self.db.query(Entity).join(Detail).filter(Detail.source_id.in_(source_ids)).all()
        entities_with_relationships = self.db.query(Entity).join(Relationship, 
            (Entity.id == Relationship.source_entity_id) | (Entity.id == Relationship.target_entity_id)
        ).filter(Relationship.source_id.in_(source_ids)).all()
        
        # Combine and deduplicate entities
        all_entities = {e.id: e for e in entities_with_details + entities_with_relationships}
        
        # Get all relationships for this episode
        relationships = self.db.query(Relationship).filter(Relationship.source_id.in_(source_ids)).all()
        
        # Format for frontend
        nodes = []
        for entity in all_entities.values():
            nodes.append({
                "id": str(entity.id),
                "label": entity.name,
                "type": entity.type,
                "summary": entity.summary or ""
            })
        
        edges = []
        for rel in relationships:
            edges.append({
                "id": str(rel.id),
                "source": str(rel.source_entity_id),
                "target": str(rel.target_entity_id),
                "label": rel.description
            })
        
        return {"nodes": nodes, "edges": edges}
    
    def get_entity_details(self, entity_id: int) -> Dict[str, Any]:
        """Get all details for a specific entity with source information."""
        entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            return None
        
        details = self.db.query(Detail).filter(Detail.entity_id == entity_id).all()
        
        detail_list = []
        for detail in details:
            detail_list.append({
                "detail": detail.detail_text,
                "timestamp_start": detail.source.timestamp_start,
                "timestamp_end": detail.source.timestamp_end,
                "episode_id": detail.source.episode_id
            })
        
        return {
            "entity": {
                "id": entity.id,
                "name": entity.name,
                "type": entity.type,
                "summary": entity.summary
            },
            "details": detail_list
        }