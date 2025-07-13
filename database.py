from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Episode(Base):
    __tablename__ = "episodes"
    
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    episode_url = Column(Text)
    processed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='pending')  # pending, processing, complete
    
    # Relationships
    sources = relationship("Source", back_populates="episode")

class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    type = Column(Text, nullable=False)  # Person, Organization, Event, Source Material, Concept
    summary = Column(Text)
    
    # Relationships
    details = relationship("Detail", back_populates="entity")
    source_relationships = relationship("Relationship", foreign_keys="Relationship.source_entity_id", back_populates="source_entity")
    target_relationships = relationship("Relationship", foreign_keys="Relationship.target_entity_id", back_populates="target_entity")

class Detail(Base):
    __tablename__ = "details"
    
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    detail_text = Column(Text, nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    
    # Relationships
    entity = relationship("Entity", back_populates="details")
    source = relationship("Source", back_populates="details")

class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True)
    source_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    target_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    description = Column(Text, nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    
    # Relationships
    source_entity = relationship("Entity", foreign_keys=[source_entity_id], back_populates="source_relationships")
    target_entity = relationship("Entity", foreign_keys=[target_entity_id], back_populates="target_relationships")
    source = relationship("Source", back_populates="relationships")

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)
    timestamp_start = Column(Integer, nullable=False)  # Start time in seconds
    timestamp_end = Column(Integer, nullable=False)    # End time in seconds
    transcript_snippet = Column(Text)
    
    # Relationships
    episode = relationship("Episode", back_populates="sources")
    details = relationship("Detail", back_populates="source")
    relationships = relationship("Relationship", back_populates="source")

# Database setup
DATABASE_URL = "sqlite:///./podcast_mapper.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()