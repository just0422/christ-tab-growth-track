from flask import Flask, render_template

app = Flask(__name__)

@app.route("/disc")
def disc():
    type_questions = {
        'dominance': [
            'I am assertive, demanding, and decisive.',
            'I enjoy doing multiple tasks at once.',
            'I thrive in a challenge-based environment.',
            'I think about tasks more than others or myself.',
            'I am motivated by accomplishment and authority.'
        ],
        'influence': [
            'I enjoy influencing and inspiring other people.',
            'I am optimistic about others.',
            'I tend to be the life of the party.',
            'I think about motivating people.',
            'I am motivated by recognition and approval.'
        ],
        'steadiness': [
            'I thrive in consistent environments.',
            'I prefer specifics over generalizations.',
            'I enjoy small groups of people.',
            'I prefer being a member of a team.',
            'I am motivated by stability and support.'
        ],
        'conscientiousness': [
            'I typically do not take big risks.',
            'I love tasks, order, and details.',
            'I am right most of the time.',
            'I comply with clearly defined rules.',
            'I am motivated by quality and correctness.'
        ]
    }

    return render_template("disc.html", type_questions=type_questions)
    
@app.route("/sga")
def sga():
    return render_template("sga.html")
    
if __name__ == "__main__":
    app.run(debug=True)
