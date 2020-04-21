from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/disc")
def disc():
    choices = ["never", "rarely", "sometimes", "often", "always"]

    return render_template("disc.html", type_questions=disc_type_questions, choices=choices)
    
@app.route("/disc/submit", methods = ["POST"])
def disc_submit():
    type_values = {}

    for types in disc_type_questions.keys():
        type_values[types] = 0
        for index in range(len(disc_type_questions[types])):
            type_values[types] += int(request.form.get(types + '-' + str(index)))

    maxType1 = list(disc_type_questions.keys())[0]
    for typeKey, value in type_values.items():
        if value > type_values[maxType1]:
            maxType1 = typeKey

    remaining = list(disc_type_questions.keys())
    remaining.remove(maxType1)
    maxType2 = remaining[0]
    for typeKey in remaining:
        if type_values[typeKey] > type_values[maxType2]:
            maxType2 = typeKey

    doubleMax = []
    if type_values[maxType1] == type_values[maxType2]:
        doubleMax = [maxType1, maxType2]

    return render_template("disc_complete.html", 
        type_values=type_values,
        doubleMax=doubleMax,
        maxType1=maxType1,
        maxType2=maxType2
    )

@app.route("/sga/submit", methods = ["POST"])
def sga_submit():
    type_values = {}

    for types in sga_type_details.keys():
        type_values[types] = 0
        for index in range(len(sga_type_details[types])):
            type_values[types] += int(request.form.get(types + '-' + str(index)))

    max_types = []
    remaining = list(sga_type_details.keys())
    counter = 9
    while len(max_types) < 5 and counter > 1:
        types = [key for key,val in sga_type_details.items() if type_values[key] == counter]
        max_types += types
        counter -= 1

    return render_template("sga_complete.html", 
        type_values=type_values,
        type_details=sga_type_details,
        max_types = max_types
    )

@app.route("/sga")
def sga():
    choices = ["Almost Never", "Sometimes", "Almost Always"]
    return render_template("sga.html", type_details=sga_type_details, choices=choices)
    
disc_type_questions = {
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

sga_type_details = {
    'Administration': {
        'description': 'The gift of administration is the divine strength or ability to organize multiple tasks and groups of people to accomplish these tasks.',
        'verses': 'Luke 14:28-30; Acts 6:1-7; 1 Corinthians 12:28',
        'questions': [
            'I like organizing services and events.',
            'I am passionate about managing details.',
            'Creating a task list is easy and enjoyable for me.'
        ]
    },
    'Apostleship': {
        'description': 'The gift of apostleship is the divine strength or ability to pioneer new churches and ministries through planting, overseeing, and training.',
        'verses': 'Acts 15:22-35; 1 Corinthians 12:28; 2 Corinthians 12:12; Galatians 2:7-10; Ephesians 4:11-14',
        'questions': [
            'I am interested in starting new churches.',
            'I like to help start new ministry projects.',
            'I am attracted to ministries that start new churches.'
        ]
    },
    'Craftsmanship': {
        'description': 'The gift of craftsmanship is the divine strength or ability to plan, build and work with your hands in construction environments to accomplish multiple ministry applications.',
        'verses': 'Exodus 30:22, 31:3-11; 2 Chronicles 34:9-13; Acts 18:2-3',
        'questions': [
            'I enjoy working with my hands.',
            'I consider myself a craftsman or craftswoman.',
            'Building something with my hands is very satisfying to me.'
        ]
    },
    'Discernment': {
        'description': 'The gift of discernment is the divine strength or ability to spiritually identify falsehood and to distinguish between right and wrong motives and situations.',
        'verses': 'Matthew 16:21-23; Acts 5:1-11, 16:16-18; 1 Corinthians 12:10; 1 John 4:1-6',
        'questions': [
            'I can tell when someone is insincere.',
            'I sense when situations are spiritually unhealthy.',
            'I can pinpoint issues or problems quickly.'
        ]
    },
    'Evangelism': {
        'description': 'The gift of evangelism is the divine strength or ability to help non-Christians take the necessary steps to becoming Christ followers.',
        'verses': 'Acts 8:5-6, 8:26-40, 14:21, 21:8; Ephesians 4:11-14',
        'questions': [
            'I pray daily for people who don’t know Jesus.',
            'I am greatly motivated by seeing people who don’t know God be saved.',
            'Sharing the Gospel with someone I do not know is exciting and natural for me.'
        ]
    },
    'Exhortation': {
        'description': 'The gift of exhortation is the divine strength or ability to encourage others through the written or spoken word and Biblical truth.',
        'verses': 'Acts 14:22; Romans 12:8; 1 Timothy 4:13; Hebrews 10:24-25',
        'questions': [
            'Encouraging others is a high priority in my life.',
            'I come across as loving and caring.',
            'I look for ways to encourage other people.'
        ]
    },
    'Faith': {
        'description': 'The gift of faith is the divine strength or ability to believe in God for unseen supernatural results in every arena of life.',
        'verses': 'Acts 11:22-24; Romans 4:18-21; 1 Corinthians 12:9; Hebrews 11',
        'questions': [
            'I trust God to provide for my daily needs.',
            'Asking God for a list of seemingly impossible things is exciting to me.',
            'I trust that God has my back in every situation.'
        ]
    },
    'Giving': {
        'description': 'The gift of giving is the divine strength or ability to produce wealth and to give by tithes and offerings for the purpose of advancing the Kingdom of God on earth.',
        'verses': 'Mark 12:41-44; Romans 12:8; 2 Corinthians 8:1-7, 9:2-7',
        'questions': [
            'I am passionate about financially investing in the Kingdom of God.',
            'I find ways to give offerings above my tithe.',
            'I want to make more money so that I can give more.'
        ]
    },
    'Healing': {
        'description': 'The gift of healing is the divine strength or ability to act as an intermediary in faith, prayer, and by the laying-on of hands for the healing of physical and mental illnesses.',
        'verses': 'Acts 3:1-10, 9:32-35, 28:7-10; 1 Corinthians 12:9, 28',
        'questions': [
            'I look for opportunities to pray for the sick.',
            'I believe miraculous healing is possible and still happens.',
            'God has used me to bring healing to those who are sick.'
        ]
    },
    'Helps': {
        'description': 'The gift of helps is the divine strength or ability to work in a supportive role for the accomplishment of tasks in Christian ministry.',
        'verses': 'Mark 15:40-41; Acts 9:36; Romans 16:1-2; 1 Corinthians 12:28',
        'questions': [
            'I enjoy doing little things that others typically do not enjoy.',
            'Helping others is one of my greatest motivations.',
            'Being a part of the process is fulfilling to me.'
        ]
    },
    'Hospitality': {
        'description': 'The gift of hospitality is the divine strength or ability to create warm, welcoming environments for others in places such as your home, office, or church.',
        'verses': 'Acts 16:14-15; Romans 12:13, 16:23; Hebrews 13:1-2; 1 Peter 4:9',
        'questions': [
            'I often have people over to my house.',
            'Creating a warm and welcoming environment is important to me.',
            'I tend to make total strangers feel at home.'
        ]
    },
    'Intercession': {
        'description': 'The gift of intercession is the divine strength or ability to stand in the gap in prayer for someone, something, or someplace believing for profound results.',
        'verses': 'Hebrews 7:25; Colossians 1:9-12, 4:12-13; James 5:14-16',
        'questions': [
            'I enjoy spending hours in prayer for other people.',
            'I am burdened to pray for situations affecting the world.',
            'People often ask me to pray for them.'
        ]
    },
    'Knowledge': {
        'description': 'The gift of knowledge is the divine strength or ability to understand and to bring clarity to situations and circumstances often accompanied by a word from God.',
        'verses': 'Acts 5:1-11; 1 Corinthians 12:8; Colossians 2:2-3',
        'questions': [
            'Education is very important to me.',
            'People come to me to learn more about God and the Bible.',
            'I enjoy knowing Biblical details and helping others understand them, too.'
        ]
    },
    'Leadership': {
        'description': 'The gift of leadership is the divine strength or ability to influence people at their level while directing and focusing them on the big picture, vision, or idea.',
        'verses': 'Romans 12:8; 1 Timothy 3:1-13, 5:17; Hebrews 13:17',
        'questions': [
            'I tend to motivate others to get involved.',
            'I prefer to take the lead whenever possible.',
            'I delegate responsibilities to accomplish tasks.'
        ]
    },
    'Mercy': {
        'description': 'The gift of mercy is the divine strength or ability to feel empathy and to care for those who are hurting in any way.',
        'verses': 'Matthew 9:35-36; Mark 9:41; Romans 12:8; 1 Thessalonians 5:14',
        'questions': [
            'I hurt when I see others hurting.',
            'I’m very sensitive to sad stories.',
            'I am motivated to help people in need.'
        ]
    },
    'Miracles': {
        'description': 'The gift of miracles is the divine strength or ability to alter the natural outcomes of life in a supernatural way through prayer, faith, and divine direction.',
        'verses': 'Acts 9:36-42, 19:11-12, 20:7-12; Romans 15:18-19; 1 Corinthians 12:10, 28',
        'questions': [
            'I believe God will use me to enact His miracles.',
            'Miracles often happen when I’m nearby.',
            'I have a constant hunger to see God’s miraculous power.'
        ]
    },
    'Missionary': {
        'description': 'The missionary gift is the divine strength or ability to reach others outside of your culture and nationality, while in most cases living in that culture or nation.',
        'verses': 'Acts 8:4, 13:2-3, 22:21; Romans 10:15',
        'questions': [
            'I enjoy sharing the Gospel with other people groups and nationalities.',
            'The idea of living in another country to benefit the Gospel is exciting to me.',
            'I focus a lot on reaching the world for Christ.'
        ]
    },
    'Music': {
        'description': 'The gift of music/worship is the divine strength or ability to sing, dance, or play an instrument primarily for the purpose of helping others worship God.',
        'verses': 'Deuteronomy 31:22; 1 Samuel 16:16; 1 Chronicles 16:41-42; 2 Chronicles 5:12-13, 34:12; Psalm 150',
        'questions': [
            'I’ve devoted considerable time to mastering my voice and/or musical instrument.',
            'I desire to serve the church through worship.',
            'I gain my deepest satisfaction through leading others in vocal or instrumental worship.'
        ]
    },
    'Pastor': {
        'description': 'The gift of pastor/shepherd is the divine strength or ability to care for the personal needs of others by nurturing and mending life issues.',
        'verses': 'John 10:1-18; Ephesians 4:11-14; 1 Timothy 3:1-7; 1 Peter 5:1-3',
        'questions': [
            'Caring for the hurting is one of my highest priorities.',
            'I enjoy connecting, caring for, and coaching others.',
            'I enjoy helping people who are going through a difficult time.'
        ]
    },
    'Prophecy': {
        'descriptions': 'The gift of prophecy is the divine strength or ability to boldly speak and bring clarity to scriptural and doctrinal truth, in some cases foretelling God’s plan.',
        'verses': 'Acts 2:37-40, 7:51-53, 26:24-29; 1 Corinthians 14:1-4; 1 Thessalonians 1:5',
        'questions': [
            'I get frustrated when people knowingly sin.',
            'Confronting someone about a sin in their life is important to me.',
            'I enjoy hearing passionate and clear preaching of God’s Word.'
        ]
    },
    'Service': {
        'descriptions': 'The gift of serving is the divine strength or ability to do small or great tasks in working for the overall good of the body of Christ.',
        'verses': 'Acts 6:1-7; Romans 12:7; Galatians 6:10; 1 Timothy 1:16-18; Titus 3:14',
        'questions': [
            'I enjoy serving behind the scenes.',
            'It bothers me when people sit around and do nothing.',
            'I like to do small things that others overlook.'
        ]
    },
    'Teaching': {
        'descriptions': 'The gift of teaching is the divine strength or ability to study and learn from the Scriptures primarily to bring understanding and growth to other Christians.',
        'verses': 'Acts 18:24-28, 20:20-21; 1 Corinthians 12:28; Ephesians 4:11-14',
        'questions': [
            'I like creating outlines of the Bible.',
            'I share Biblical truth with others to help them grow.',
            'I prefer to teach and study the Bible topically rather than verse by verse.'
        ]
    },
    'Tongues': {
        'descriptions': 'The gift of tongues is the divine strength or ability to pray in a heavenly language to encourage your spirit and to commune with God. The gift of tongues is often accompanied by interpretation and should be used appropriately.',
        'verses': 'Acts 2:1-13; 1 Corinthians 12:10, 14:1-14',
        'questions': [
            'God has used me to interpret what someone speaking in tongues is saying.',
            'I pray in tongues daily.',
            'Praying in tongues is encouraging and important to me.'
        ]
    },
    'Wisdom': {
        'descriptions': 'The gift of wisdom is the divine strength or ability to apply the truths of Scripture in a practical way, producing a fruitful outcome and the character of Jesus Christ.',
        'verses': 'Acts 6:3,10; 1 Corinthians 2:6-13, 12:8',
        'questions': [
            'I enjoy the book of Proverbs more than any other book in the Bible.',
            'When I study Scripture, I receive unique insights from God.',
            'When faced with difficulty, I tend to make wise decisions.'
        ]
    }
}

if __name__ == "__main__":
    app.run(debug=True)

