import openai
import re
import httpx
import os
from dotenv import load_dotenv
import chromadb

_ = load_dotenv()
from google import genai

chroma_client = chromadb.Client()
collection = chroma_client.create_collection("knowledge")

collection.add(
    documents=[
        "python is a programming language known for simplicity.",
        "chromadb is a vector database for storing and searching documents.",
        "RAG stands for Retrieval-Augmented Generation. It fetches relevant documents before answering.",
        "An AI agent can think, act and use tools to complete tasks.",
        "Lanchain is a framework for building AI agents that can use tools and access external data.",
    ],
    ids=["doc1", "doc2", "doc3", "doc4", "doc5"]
)

action_re = re.compile('^Action: (\\w+): (.*)$')  

prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.
t
Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

average_dog_weight:
e.g. average_dog_weight: Collie
returns average weight of a dog when given the breed

search_knowledge_base:
e.g. search_knowledge_base: What is RAG?
Searches the knowledge base and returns relevant information

Example session:

Question: How much does a Bulldog weigh?
Thought: I should look the dogs weight using average_dog_weight
Action: average_dog_weight: Bulldog
PAUSE

You will be called again with this:

Observation: A Bulldog weights 51 lbs

You then output:

Answer: A bulldog weights 51 lbs
""".strip()


client = genai.Client()

class Agent:
    

    def __init__(self, system=""):
        self.system = system
        self.messages = []

    def __call__(self, message):
        self.messages.append({
            "role": "user",
            "parts": [{"text": message}]
        })
        result = self.execute()
        self.messages.append({
            "role": "model",
            "parts": [{"text": result}]
        })
        return result

    def execute(self):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self.messages,
            config={
                "system_instruction": self.system,
                "temperature": 0
            }
        )
        return response.text
    
def calculate(what):
    return eval(what)

def average_dog_weight(name):
    if name in "Scottish Terrier": 
        return("Scottish Terriers average 20 lbs")
    elif name in "Border Collie":
        return("a Border Collies average weight is 37 lbs")
    elif name in "Toy Poodle":
        return("a toy poodles average weight is 7 lbs")
    else:
        return("An average dog weights 50 lbs")

def search_knowledge_base(query):
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    return " | ".join(results['documents'][0])

known_actions = {
    "calculate": calculate,
    "average_dog_weight": average_dog_weight,
    "search_knowledge_base": search_knowledge_base
}

def query(question, max_turns=5):
    i = 0
    bot = Agent(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [
            action_re.match(a) 
            for a in result.split('\n') 
            if action_re.match(a)
        ]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
    else:
        return


question = """What is RAG and how does it work?"""
query(question)



        
