from db.models import Topic, Quiz, Roadmap, GeneratedTopic, Score
from typing import List

async def create_topic(name: str, userId: str):
    topic = Topic(userId=userId, name=name)
    await topic.insert()
    return topic.id

async def create_quiz(topic_id: str, question_data: str):
    quiz = Quiz(topic_id=topic_id, question_data=question_data)
    await quiz.insert()
    return quiz

async def create_roadmap(topic_id: str, steps: str):
    roadmap = Roadmap(topic_id=topic_id, steps=steps)
    await roadmap.insert()
    return roadmap

async def create_generated_topics(topic_id: str, difficulty: List[str], medium: List[str], easy: List[str]):
    generated_topics = GeneratedTopic(topic_id=topic_id, difficulty=difficulty, medium=medium, easy=easy)
    await generated_topics.insert()
    return generated_topics

async def store_points(userId: str, points: int):
    existing_score = await Score.find_one({"userId": userId})

    if existing_score:
        existing_score.points += points
        await existing_score.save()
    else:
        new_score = Score(userId=userId, points=points)
        await new_score.insert()
        return new_score
    
    return existing_score

async def get_points(userId: str):
    return await Score.find_one({"userId":userId});

async def get_topic(topic_id: str):
    return await Topic.find(Topic.topic_id == topic_id).to_list()

async def get_topics(userId: str):
    return await Topic.find({"userId": userId}).to_list()

async def get_quizzes(topic_id: str):
    return await Quiz.find(Quiz.topic_id == topic_id).to_list()

async def get_roadmaps(topic_id: str):
    return await Roadmap.find(Roadmap.topic_id == topic_id).to_list()

async def get_generatedTopics(topic_id: str):
    return await GeneratedTopic.find(GeneratedTopic.topic_id == topic_id).to_list()
