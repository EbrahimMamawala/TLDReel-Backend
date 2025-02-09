from app.models import Topic, Quiz, Roadmap

async def create_topic(name: str, description: str):
    topic = Topic(name=name, description=description)
    await topic.insert()
    return topic

async def create_quiz(topic_id: str, question_data: str):
    quiz = Quiz(topic_id=topic_id, question_data=question_data)
    await quiz.insert()
    return quiz

async def create_roadmap(topic_id: str, steps: str):
    roadmap = Roadmap(topic_id=topic_id, steps=steps)
    await roadmap.insert()
    return roadmap

async def get_topics():
    return await Topic.find().to_list()

async def get_quizzes(topic_id: str):
    return await Quiz.find(Quiz.topic_id == topic_id).to_list()

async def get_roadmaps(topic_id: str):
    return await Roadmap.find(Roadmap.topic_id == topic_id).to_list()