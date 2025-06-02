from flask import Flask,render_template,request
import json
from transformers import pipeline


summarizer =pipeline('summarization',model="google/flan-t5-base")

def generate_summary(text,level):
    if level=="child":
        prompt=f"Summarize this for a 10 year old:{text}"
    elif level=="teen":
        prompt=f"Summarize this for a High School Student:{text}"
    else:
        prompt=f"Summarize this technically for a college Student:{text}"

        result=summarizer(prompt,max_length=100,min_length=30,do_sample=False)
        return result[0]["generated_text"]