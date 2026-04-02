import datetime

from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

vectorizer = pickle.load(open('models/vectorizer.pkl', 'rb'))
data = pd.read_pickle('models/dev.pkl')
tfidf_matrix = pickle.load(open('models/tfidf_matrix.pkl', 'rb'))

vectorizer_design = pickle.load(open('models/vectorizer_design.pkl', 'rb'))
data_design = pd.read_pickle('models/design.pkl')
tfidf_matrix_design = pickle.load(open('models/tfidf_matrix_design.pkl', 'rb'))

vectorizer_ai = pickle.load(open('models/vectorizer_ai.pkl', 'rb'))
data_ai = pd.read_pickle('models/ai_job.pkl')
tfidf_matrix_ai = pickle.load(open('models/tfidf_matrix_ai.pkl', 'rb'))


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="systemerror@778118",
    database="jobroles"
)

cursor = db.cursor()

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/ai', methods=['GET', 'POST'])
def ai():

    results = None
    unique_projects = []
    unique_math = []

    if request.method == "POST":

        user_skills = request.form['skills']
        education = request.form['education']

        # clean input
        user_skills = user_skills.lower()
        skills_list = [s.strip() for s in user_skills.split(",")]
        skills_list = list(set(skills_list))
        user_skills = ", ".join(skills_list)

        # vectorization
        user_vector = vectorizer_ai.transform([user_skills])
        similarity_scores = cosine_similarity(user_vector, tfidf_matrix_ai).flatten()

        # add scores
        data_temp = data_ai.copy()
        data_temp["score"] = similarity_scores

        # sort + remove duplicate jobs
        data_sorted = data_temp.sort_values(by="score", ascending=False)
        data_unique = data_sorted.drop_duplicates(subset="job_recommendation")

        top_jobs = data_unique.head(2)

        results = []

        for _, row in top_jobs.iterrows():

            match = round(row["score"] * 100, 2)

            results.append({
                "role": row["job_recommendation"],
                "project": row["projects"],
                "math": row["math_knowledge"],
                "demand": row["industry_demand"],
                "match": match
            })

        # 🔥 REMOVE DUPLICATE PROJECTS & MATH
        project_set = set()
        math_set = set()

        for r in results:

            # split projects
            projects = r["project"].split(";")
            for p in projects:
                project_set.add(p.strip())

            # split math topics
            maths = r["math"].split(",")
            for m in maths:
                math_set.add(m.strip())

        unique_projects = list(project_set)
        unique_math = list(math_set)

        # save to DB
        if len(results) >= 2:

            job1 = results[0]["role"]
            job2 = results[1]["role"]

            project1 = results[0]["project"]
            project2 = results[1]["project"]

            math_knowledge = results[0]["math"]
            demand = results[0]["demand"]

            cursor.execute("""
            INSERT INTO user_history
            (education, job1, job2, project1, project2, math_knowledge, demand)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (education, job1, job2, project1, project2, math_knowledge, demand))

            db.commit()

    return render_template(
        "ai.html",
        results=results,
        projects=unique_projects,
        maths=unique_math
    )

@app.route('/web', methods=["GET","POST"])
def web():

    results = None

    if request.method == "POST":

        user_skills = request.form['skills']
        education = request.form['education']

        user_skills = user_skills.lower()

        skills_list = [s.strip() for s in user_skills.split(",")]
        skills_list = list(set(skills_list))
        user_skills = ", ".join(skills_list)

        user_vector = vectorizer.transform([user_skills])
        similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()

        data_temp = data.copy()
        data_temp["score"] = similarity_scores

        data_sorted = data_temp.sort_values(by="score", ascending=False)
        data_unique = data_sorted.drop_duplicates(subset="job_recommendation")
        top_jobs = data_unique.head(2)

        results = []

        for _, row in top_jobs.iterrows():

            match = round(row["score"] * 100, 2)

            results.append({
                "role": row["job_recommendation"],
                "project": row["projects"],
                "math": row["math_knowledge"],
                "demand": row["industry_demand"],
                "match": match
            })

        job1 = results[0]["role"]
        job2 = results[1]["role"]

        project1 = results[0]["project"]
        project2 = results[1]["project"]

        math_knowledge = results[0]["math"]
        demand = results[0]["demand"]

        cursor.execute("""
        INSERT INTO user_history
        (education, job1, job2, project1, project2, math_knowledge, demand)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (education, job1, job2, project1, project2, math_knowledge, demand))

        db.commit()

    return render_template("web.html", results=results)

@app.route('/design', methods=["GET","POST"])
def design():

    results = None

    if request.method == "POST":

        user_skills = request.form['skills']
        education = request.form['education']

        user_skills = user_skills.lower()

        skills_list = [s.strip() for s in user_skills.split(",")]
        skills_list = list(set(skills_list))
        user_skills = ", ".join(skills_list)

        user_vector = vectorizer_design.transform([user_skills])
        similarity_scores = cosine_similarity(user_vector, tfidf_matrix_design).flatten()

        data_temp = data_design.copy()
        data_temp["score"] = similarity_scores

        data_sorted = data_temp.sort_values(by="score", ascending=False)
        data_unique = data_sorted.drop_duplicates(subset="job_recommendation")
        top_jobs = data_unique.head(2)

        results = []

        for _, row in top_jobs.iterrows():

            match = round(row["score"] * 100, 2)

            results.append({
                "role": row["job_recommendation"],
                "project": row["projects"],
                "math": row["math_knowledge"],
                "demand": row["industry_demand"],
                "match": match
            })

        job1 = results[0]["role"]
        job2 = results[1]["role"]

        project1 = results[0]["project"]
        project2 = results[1]["project"]

        math_knowledge = results[0]["math"]
        demand = results[0]["demand"]

        cursor.execute("""
        INSERT INTO user_history
        (education, job1, job2, project1, project2, math_knowledge, demand)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (education, job1, job2, project1, project2, math_knowledge, demand))

        db.commit()

    return render_template("design.html", results=results)

@app.route('/history')
def history():

    cursor.execute("SELECT * FROM user_history ORDER BY user_date ASC")

    history_data = cursor.fetchall()

    return render_template("history.html", history=history_data)

@app.route('/delete_history', methods=["POST"])
def delete_history():

    cursor.execute("truncate table user_history")
    db.commit()

    return redirect(url_for('history'))

if __name__ == '__main__':
    app.run(debug=True)