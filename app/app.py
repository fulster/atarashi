import openai
import configparser
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Charger la configuration
config = configparser.ConfigParser()
config.read('app.secret.conf')
openai.api_key = config['openai']['api_key']

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Table de relation many-to-many entre Idea et Keyword
idea_keywords = db.Table('idea_keywords',
    db.Column('idea_id', db.Integer, db.ForeignKey('idea.id'), primary_key=True),
    db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id'), primary_key=True)
)

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    keywords = db.relationship('Keyword', secondary=idea_keywords, lazy='subquery',
                               backref=db.backref('ideas', lazy=True))

class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False)

@app.route('/')
def home():
    ideas = Idea.query.all()
    return render_template('home.html', ideas=ideas)

@app.route('/keywords', methods=['POST'])
def keywords():
    text = request.json['text']
    # response = openai.Completion.create(
    #     engine="text-davinci-002",
    #     prompt=f"Generate keywords for the following idea: {text}",
    #     max_tokens=60
    # )
    response = openai.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f"Tu es spécialiste en aménagement d'intérieur. Génère une liste séparée de 3 nom de commerce générique séparés par des virgules chez qui on peut trouver cet item (exemple pour du pain : boulangerie, rayon boulangerie de supermarché) : {text}",
        }
    ],
    model="gpt-3.5-turbo",
    )

    # keywords = response['choices'][0]['text'].strip().split(',')
    keyword_texts = response.choices[0].message.content.strip().split(',')
    new_idea = Idea(content=text)
    for keyword_text in keyword_texts:
        keyword = Keyword.query.filter_by(keyword=keyword_text.strip()).first()
        if not keyword:
            keyword = Keyword(keyword=keyword_text.strip())
        new_idea.keywords.append(keyword)
    db.session.add(new_idea)
    db.session.commit()
    return jsonify(keywords=[k.keyword for k in new_idea.keywords])

@app.route('/reset-db', methods=['POST'])
def reset_db():
    with app.app_context():
        # db.drop_all()  # Attention: Cela supprimera toutes les données !
        db.create_all()
    return redirect(url_for('home'))  # Rediriger vers la page d'accueil après la réinitialisation

@app.route('/delete-idea/<int:idea_id>', methods=['DELETE'])
def delete_idea(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    db.session.delete(idea)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Idea deleted'})

if __name__ == '__main__':
    app.run(debug=True)
