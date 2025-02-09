from beanie import Document
from typing import List

class Topic(Document):
    name: str
    description: str

    class Settings:
        collection = "topics"

class Quiz(Document):
    topic_id: str
    question_data: str

    class Settings:
        collection = "quizzes"

class Roadmap(Document):
    topic_id: str
    steps: str

    class Settings:
        collection = "roadmaps"