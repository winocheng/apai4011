import pandas as pd
import os
import itertools
from skillNer.general_params import SKILL_DB
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def course_list():
    """
    Output:
        list of course codes
    """
    if(os.path.exists("UST_Course_skilled.pkl")):
        courses = pd.read_pickle("UST_Course_skilled.pkl")
        return list(courses.index.values)
    else:
        raise Exception("Course file doesn't exist")
        

def skill_list(courses):
    """
    Input:
        courses: list of string of course code
    Output:
        list of skill names,
        list of skill ids
    """
    if(os.path.exists("UST_Course_skilled.pkl")):
        course_skills = pd.read_pickle("UST_Course_skilled.pkl")
        ids = [item['id'] for item in list(itertools.chain.from_iterable(list(course_skills.loc[courses]["skills"])))]
        ids = list(set(ids))
        
        return [SKILL_DB[i]["skill_name"] for i in ids], ids
    else:
        raise Exception("Course file doesn't exist")
        
def get_job_list(skillids, category, vectorizer=pickle.load(open("vectorizer.pkl", "rb"))):
    """
    input:
        skillids: list of skill IDs,
        category: string of the job category,
        vectorizer: fitted vectorizer
    output:
        list of string of top 10 similarity jobs titles within category
    """
    labels = df_job_label = pd.read_csv("job_label.csv",index_col=0)
    ids = df_job_label[df_job_label["Label"] == category].index.values
    
    jobskills = pd.read_pickle('job_skilled.pkl')
    filtered = jobskills.loc[np.intersect1d(ids,jobskills.index.values)]
    filtered["skills"] = filtered["skills"].apply(lambda skills: ' '.join([item['id'] for item in skills]))
    filtered["tf_idf"] = filtered["skills"].apply(lambda skills: vectorizer.transform([skills]))
    in_vector = vectorizer.transform([' '.join(skillids)])
    filtered["score"] = filtered["tf_idf"].apply(lambda tfidf: float(cosine_similarity(in_vector, tfidf)))
    return filtered.sort_values(by="score", ascending=False).iloc[:10]["Title"]
    

    
def get_job_skills(idx):
    """
    input:
        idx: job id
    output:
        list of skills extracted from that job
    """
    if(os.path.exists('job_skilled.pkl')):
        jobskills = pd.read_pickle('job_skilled.pkl')
        job = jobskills.loc[idx]
        ids = [item['id'] for item in job["skills"]]
        return [SKILL_DB[i]["skill_name"] for i in ids], job["Title"]
    else:
        raise Exception("Job skills file dosen't exist")
        
        


def predict_job(skill_list,vectorizer=pickle.load(open("vectorizer.pkl", "rb")),df_job=pickle.load(open("df_job.pkl", "rb"))):
    """
    Input:
        skill_list: list of skill IDs,
        vectorizer: fitted vectorizer,
        df_job: job dataframe with labels and tf-idf vectors
    Output:
        vec_output_list: sorted list of tuple with (cos_sim and label)
    """
    vec_input = vectorizer.transform([' '.join(skill_list)])
    labels = df_job['Label'].unique()
    vec_output_list = []
    for label in labels:
        vec_output = df_job[df_job['Label'] == label]['tf_idf'].sum()
        vec_output_list.append((float(cosine_similarity(vec_input,vec_output)),label))
    vec_output_list.sort(reverse=True)
    return vec_output_list
    