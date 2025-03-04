from beanie import Document
from typing import List

class Topic(Document):
    userId: str
    name: str

    class Settings:
        name = "topics"

class Quiz(Document):
    topic_id: str
    question_data: str

    class Settings:
        name = "quizzes"

class Roadmap(Document):
    topic_id: str
    steps: str

    class Settings:
        name = "roadmaps"

class GeneratedTopic(Document):
    topic_id: str
    difficulty: List[str]
    medium: List[str]
    easy: List[str]
    
    class Settings:
        name = "generated_topics"

class Score(Document):
    userId: str
    points:int

    class Settings:
        name = "Scores"
