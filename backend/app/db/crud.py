# api/crud.py
from sqlalchemy.orm import Session
from app import models

def create_topic(db: Session, name: str, description: str):
    topic = models.Topic(name=name, description=description)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic

def create_quiz(db: Session, topic_id: int, question_data: dict):
    quiz = models.Quiz(topic_id=topic_id, question_data=question_data)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz

def create_roadmap(db: Session, topic_id: int, steps: str):
    roadmap = models.Roadmap(topic_id=topic_id, steps=steps)
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return roadmap

def get_topics(db: Session):
    return db.query(models.Topic).all()

def get_quizzes(db: Session, topic_id: int):
    return db.query(models.Quiz).filter(models.Quiz.topic_id == topic_id).all()

def get_roadmaps(db: Session, topic_id: int):
    return db.query(models.Roadmap).filter(models.Roadmap.topic_id == topic_id).all()
