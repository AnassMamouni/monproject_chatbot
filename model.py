from sentence_transformers import SentenceTransformer, util
import json
import pandas as pd
import os

# Charger la FAQ
with open("faq.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

# Préparer les données
questions_fr = list(faq_data["questions"]["fr"].keys())
answers_fr = list(faq_data["questions"]["fr"].values())
questions_ar = list(faq_data["questions"]["ar"].keys())
answers_ar = list(faq_data["questions"]["ar"].values())

questions = questions_fr + questions_ar
answers = answers_fr + answers_ar

# Charger le modèle
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
question_embeddings = model.encode(questions, convert_to_tensor=True)

# Gestion des logs
LOG_FILE = 'unanswered_questions.csv'

def log_unanswered(question, score):
    """Enregistre les questions non reconnues"""
    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=['Question', 'Score']).to_csv(LOG_FILE, index=False)
    
    pd.DataFrame([[question, score]], columns=['Question', 'Score']).to_csv(
        LOG_FILE, mode='a', header=False, index=False)

def get_best_answer(query, threshold=0.65):
    """Trouve la meilleure réponse avec score de confiance"""
    query_embedding = model.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, question_embeddings)[0]
    
    max_score = cos_scores.max().item()
    best_idx = cos_scores.argmax().item()
    
    if max_score < threshold:
        log_unanswered(query, max_score)
        return "Je n'ai pas compris votre question. Pour plus d'aide, contactez le service administratif.", None
    
    return answers[best_idx], questions[best_idx]