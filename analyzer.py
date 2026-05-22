from groq import Groq
from dotenv import load_dotenv
import pandas as pd
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def calculate_funnel(df):
    steps = df['step'].unique().tolist()
    result = []
    
    for step in steps:
        total = df[df['step'] == step]['user_id'].nunique()
        done = df[(df['step'] == step) & (df['completed'] == True)]['user_id'].nunique()
        
        # calculate drop
        if total > 0:
            drop = round((1 - done/total) * 100, 1)
        else:
            drop = 0
            
        result.append({
            "step": step,
            "users": total,
            "completed": done,
            "drop_rate": drop
        })
    
    return result


def calculate_cohort(df):
    # convert to datetime first
    df['date'] = pd.to_datetime(df['timestamp'])
    df['week'] = df['date'].dt.isocalendar().week
    
    cohort = df.groupby('week')['user_id'].nunique().reset_index()
    cohort.columns = ['Week', 'Users']
    
    return cohort


def get_ai_insights(funnel_data):
    # build prompt
    prompt = f"""
You are a product analyst. Look at this funnel data and give me insights.
Return ONLY valid JSON. No explanation, no markdown, just the JSON object.

Format:
{{
  "biggest_problem": "describe the worst drop off point",
  "fixes": [
    {{
      "step": "which step",
      "issue": "what the problem is",
      "fix": "what to do about it",
      "impact": "High or Medium or Low",
      "effort": "High or Medium or Low"
    }},
    {{
      "step": "which step",
      "issue": "what the problem is", 
      "fix": "what to do about it",
      "impact": "High or Medium or Low",
      "effort": "High or Medium or Low"
    }},
    {{
      "step": "which step",
      "issue": "what the problem is",
      "fix": "what to do about it",
      "impact": "High or Medium or Low",
      "effort": "High or Medium or Low"
    }}
  ],
  "quick_win": "one thing they can fix this week",
  "retention_insight": "what helps users stick around"
}}

Here is the data:
{str(funnel_data)}
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    # parse the response
    raw = res.choices[0].message.content
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    
    return json.loads(cleaned)