import openai
from youtube_transcript_api import YouTubeTranscriptApi
from llama_index.core import VectorStoreIndex, Document
import streamlit as st
from pytube import YouTube
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer
import os
import openai
client = OpenAI()
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_video_details(video_url):
    try:
        yt = YouTube(video_url)
        return {
            "title": yt.title,
            "thumbnail_url": yt.thumbnail_url,
        }
    except Exception as e:
        return {"error": str(e)}



# Function to extract video ID from YouTube URL
def extract_video_id(url):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

# Function to fetch YouTube transcript
def get_youtube_transcript(video_url):
    video_id = extract_video_id(video_url)
    if video_id:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_transcript = " ".join([t['text'] for t in transcript])
            return full_transcript
        except Exception as e:
            return f"Error: {str(e)}"
    return "Invalid URL"


def process_video(video_url):
    transcript = get_youtube_transcript(video_url)
    if 'Error' in transcript:
        return None, transcript
    chat_engine = initialize_chat_engine(transcript)
    return chat_engine, None

def get_video_details(video_url):
    try:
        yt = YouTube(video_url)
        return {
            "title": yt.title,
            "thumbnail_url": yt.thumbnail_url,
        }
    except Exception as e:
        return {"error": str(e)}

# Function to initialize the chat engine with Llama Index
def initialize_chat_engine(transcript):
    document = Document(text=transcript, extra_info={})
    index = VectorStoreIndex.from_documents([document])
    memory = ChatMemoryBuffer.from_defaults()

    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt="""
            Imagine you're a friendly teacher who's here to help. 
            When you answer questions, keep it casual and engaging—like you're talking to a 16-year-old student who’s curious to learn more.
            Make sure your explanations are clear and straight to the point, but feel free to keep things light and relatable.
            Avoid using big words or complicated terms unless absolutely necessary, and when you do, break them down into simple, easy-to-understand language.
            Encourage questions and curiosity, and always stay positive and supportive. 
            If things get a little off-topic or inappropriate, kindly guide the conversation back to the subject in a helpful way.
            Use examples and fun analogies to explain tricky concepts, and make sure your answers feel approachable and motivating.
            Remember, you're here to help the student feel confident and excited about learning!

            Rules:
            1. ALWAYS DISPLAY A MESSAGE WHEN UNETHICAL, SEXUALLY EXPLICIT, OR HATE SPEECH IS DETECTED. MESSAGE SHOULD BE IN THE FOLLOWING FORMAT:
            "Hey! I'm sorry, but I can't assist with that. My capabilities are limited to providing information based on the video's content. 
            Please keep the conversation respectful and appropriate. Thank you!"
            2. STRICTLY FOLLOW THE RULES MENTIONED ABOVE.
        """,
    )
    return chat_engine

# Function to handle queries using the chat engine
def run(chat_engine, query):
    response = chat_engine.chat(query)
    return response.response

