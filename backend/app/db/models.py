# api/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from api.database import Base

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(JSON, nullable=False)

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"))
    question_data = Column(JSON, nullable=False)  # Stores answer choices as JSON

    topic = relationship("Topic", back_populates="quizzes")

Topic.quizzes = relationship("Quiz", back_populates="topic", cascade="all, delete-orphan")

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    steps = Column(Text)  # JSON format or delimited steps

    topic = relationship("Topic")
