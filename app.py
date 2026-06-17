from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'narrative-forge-secret-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///narratives.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Models ───────────────────────────────────────────────────────────────────

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    narrative = db.relationship('Narrative', backref='project', uselist=False, cascade='all, delete-orphan')
    characters = db.relationship('Character', backref='project', cascade='all, delete-orphan')

class Narrative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    title = db.Column(db.String(300))
    synopsis = db.Column(db.Text)
    full_narrative = db.Column(db.Text)
    world_building = db.Column(db.Text)
    main_conflict = db.Column(db.Text)
    themes = db.Column(db.Text)
    plot_acts = db.Column(db.Text)  # JSON string
    # Specs
    genre = db.Column(db.String(100))
    sub_genre = db.Column(db.String(100))
    setting = db.Column(db.String(200))
    time_period = db.Column(db.String(100))
    tone = db.Column(db.String(100))
    plot_type = db.Column(db.String(100))
    target_audience = db.Column(db.String(100))
    themes_input = db.Column(db.String(300))
    narrative_length = db.Column(db.String(50))
    protagonist_archetype = db.Column(db.String(100))
    antagonist_type = db.Column(db.String(100))
    world_type = db.Column(db.String(100))
    magic_system = db.Column(db.String(200))
    tech_level = db.Column(db.String(100))
    extra_notes = db.Column(db.Text)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(200))
    role = db.Column(db.String(100))
    archetype = db.Column(db.String(100))
    age = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    appearance = db.Column(db.Text)
    personality = db.Column(db.Text)
    backstory = db.Column(db.Text)
    motivations = db.Column(db.Text)
    abilities = db.Column(db.Text)
    flaws = db.Column(db.Text)
    relationships = db.Column(db.Text)
    arc = db.Column(db.Text)
    quotes = db.Column(db.Text)
    avatar_color = db.Column(db.String(20), default='#6c63ff')
    avatar_initials = db.Column(db.String(5))

# ─── AI Service ───────────────────────────────────────────────────────────────

def get_gemini_client():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def generate_narrative_ai(specs):
    client = get_gemini_client()
    prompt = f"""You are a master video game narrative designer. Generate a rich, detailed video game narrative based on these specifications:

Genre: {specs.get('genre', 'Fantasy')}
Sub-genre: {specs.get('sub_genre', '')}
Setting: {specs.get('setting', '')}
Time Period: {specs.get('time_period', '')}
Tone: {specs.get('tone', '')}
Plot Type: {specs.get('plot_type', '')}
Target Audience: {specs.get('target_audience', '')}
Themes: {specs.get('themes_input', '')}
Narrative Length: {specs.get('narrative_length', 'medium')}
Protagonist Archetype: {specs.get('protagonist_archetype', '')}
Antagonist Type: {specs.get('antagonist_type', '')}
World Type: {specs.get('world_type', '')}
Magic/Power System: {specs.get('magic_system', '')}
Technology Level: {specs.get('tech_level', '')}
Additional Notes: {specs.get('extra_notes', '')}

Respond ONLY with a valid JSON object (no markdown, no code fences) with these exact keys:
{{
  "title": "Epic game title",
  "synopsis": "2-3 sentence hook synopsis",
  "world_building": "Detailed world description (200-300 words)",
  "main_conflict": "The central conflict explained (150-200 words)",
  "themes": "Core themes explored (100 words)",
  "plot_acts": [
    {{"act": "Act 1 - The Call", "description": "What happens in act 1 (100 words)"}},
    {{"act": "Act 2 - The Descent", "description": "What happens in act 2 (150 words)"}},
    {{"act": "Act 3 - The Confrontation", "description": "What happens in act 3 (150 words)"}},
    {{"act": "Act 4 - The Resolution", "description": "How it all ends (100 words)"}}
  ],
  "full_narrative": "Full immersive narrative description (400-500 words)"
}}"""

    if client:
        try:
            response = client.generate_content(prompt)
            text = response.text.strip()
            if text.startswith('```'):
                text = text[text.find('{'):text.rfind('}')+1]
            return json.loads(text)
        except Exception as e:
            print(f'AI Error: {e}')
    
    # Fallback template
    return generate_fallback_narrative(specs)

def generate_characters_ai(narrative, count=4):
    client = get_gemini_client()
    prompt = f"""You are a master video game character designer. Based on this narrative, generate {count} compelling, deeply detailed characters:

NARRATIVE TITLE: {narrative.title}
SYNOPSIS: {narrative.synopsis}
WORLD: {narrative.world_building}
CONFLICT: {narrative.main_conflict}
GENRE: {narrative.genre}
TONE: {narrative.tone}

Generate exactly {count} characters including a protagonist and antagonist. 
Respond ONLY with a valid JSON array (no markdown, no code fences):
[
  {{
    "name": "Character name",
    "role": "Protagonist/Antagonist/Ally/Mentor/Rival/Wild Card",
    "archetype": "The Hero/The Shadow/The Mentor/etc",
    "age": "Age or age range",
    "gender": "Gender identity",
    "appearance": "Vivid physical description (80 words)",
    "personality": "Personality traits and demeanor (80 words)",
    "backstory": "Rich backstory (120 words)",
    "motivations": "What drives them (60 words)",
    "abilities": "Skills, powers, or special abilities (60 words)",
    "flaws": "Weaknesses and internal conflicts (60 words)",
    "relationships": "How they relate to other characters (60 words)",
    "arc": "Character development arc (60 words)",
    "quotes": "2-3 memorable in-character quotes",
    "avatar_color": "#hexcolor matching their vibe"
  }}
]"""

    if client:
        try:
            response = client.generate_content(prompt)
            text = response.text.strip()
            if text.startswith('```'):
                text = text[text.find('['):text.rfind(']')+1]
            return json.loads(text)
        except Exception as e:
            print(f'AI Error: {e}')

    return generate_fallback_characters(narrative, count)

def generate_fallback_narrative(specs):
    genre = specs.get('genre', 'Fantasy')
    setting = specs.get('setting', 'a mystical realm')
    tone = specs.get('tone', 'epic')
    return {
        "title": f"Chronicles of {setting.split()[0] if setting else 'the Forgotten'}",
        "synopsis": f"In a {tone} world of {setting}, a lone hero must rise against impossible odds to forge a new destiny for all who dwell within.",
        "world_building": f"The world is a vast expanse of {setting}, shaped by ancient forces and forgotten wars. Civilizations rose and crumbled beneath the weight of their own ambitions. Now, the land teeters on the edge of a new age — one that could herald salvation or annihilation. Hidden beneath the surface lie secrets that the powerful have buried for centuries, secrets that only the desperate and the brave dare to uncover.",
        "main_conflict": f"The central conflict arises from a power imbalance that threatens to destroy the delicate fabric of society. An ancient evil, long dormant, has stirred once again — and only one person carries the bloodline needed to stop it. But doing so means sacrificing everything they hold dear.",
        "themes": "Identity and destiny. Sacrifice and redemption. The corruption of power. Found family versus blood ties. The cost of freedom.",
        "plot_acts": [
            {"act": "Act 1 - The Awakening", "description": "The protagonist discovers their hidden heritage and is thrust into a conflict they never sought. The ordinary world is shattered."},
            {"act": "Act 2 - The Journey", "description": "Gathering unlikely allies, the hero traverses dangerous lands, uncovering the true scope of the threat. Betrayals and revelations reshape their worldview."},
            {"act": "Act 3 - The Crucible", "description": "The hero faces their darkest hour. Allies are lost. The enemy seems unstoppable. Everything must be reconsidered."},
            {"act": "Act 4 - The Reckoning", "description": "Armed with hard-won wisdom and unbreakable resolve, the hero confronts the final enemy. Victory comes at a price — but a new dawn rises."}
        ],
        "full_narrative": f"In the age of fractured skies and dying gods, the world of {setting} bears the scars of a war that ended a thousand years ago — or so they believe. Beneath the cobblestone streets of the last great city, beneath the roots of the world-tree that holds the sky aloft, something ancient breathes again.\n\nYou are nobody. A survivor in a world that chews up the hopeful and spits out the broken. But a chance encounter with a dying messenger — and the sealed letter they pressed into your hands with their last breath — changes everything. The letter bears a sigil you've seen only in dreams. A sigil that marks you as heir to a legacy that was supposed to be dead.\n\nNow they're hunting you. The Syndicate of Silence, the masked enforcers of the regime, want that letter destroyed and you with it. But others want you alive — for reasons they refuse to share. An exiled scholar. A disgraced knight. A thief who knows too much. These broken people become your shield and your blade.\n\nThe journey ahead will take you from the gutters of the city to the shattered peaks of the Worldspine Mountains, into the deep places where light has never reached, and finally to the Tower of Last Words — where the final truth waits, and where the hardest choice of your life must be made.\n\nBecause saving the world isn't the question. The question is: what kind of world do you want to save?"
    }

def generate_fallback_characters(narrative, count):
    colors = ['#6c63ff', '#e94560', '#00d4aa', '#f7a325', '#7c3aed', '#ec4899']
    chars = [
        {
            "name": "Kael Dawnstrider",
            "role": "Protagonist",
            "archetype": "The Reluctant Hero",
            "age": "24",
            "gender": "Male",
            "appearance": "Lean and weathered beyond his years, with storm-grey eyes that have seen too much. A jagged scar runs from his left brow to his jaw. His dark hair is kept short. He moves like someone who has learned to be invisible.",
            "personality": "Quietly intense, sardonic humor as armor. Deeply loyal once trust is earned. Carries guilt like a second skin. Instinctively puts others before himself, then resents himself for it.",
            "backstory": "Raised in the border slums after his village was burned by regime soldiers, Kael survived by stealing and trading secrets. He never knew his lineage — only that his mother hid something from everyone, including him. A sealed letter from a dying stranger has upended every truth he thought he knew.",
            "motivations": "Find out who he really is. Protect the people he travels with. Burn down the system that destroyed his childhood.",
            "abilities": "Expert in street combat and knife-work. Unusually attuned to ambient magic though untrained. Exceptional reader of people.",
            "flaws": "Crippling fear of becoming like those who hurt him. Pushes people away before they can leave. Freezes under high pressure.",
            "relationships": "Cautious of everyone at first. Fiercely protective of Mira. Complicated respect-rivalry with the knight Ashara.",
            "arc": "From identity-less survivor to self-actualized leader who chooses who he is, not what he was born to be.",
            "quotes": '"I\'ve been nobody my whole life. Turns out, nobody is the most dangerous thing you can be." | "Don\'t thank me. I didn\'t do it for you." | "The world doesn\'t need a hero. It needs someone too stubborn to quit."',
            "avatar_color": "#6c63ff"
        },
        {
            "name": "Seraphine Voss",
            "role": "Antagonist",
            "archetype": "The Fallen Idealist",
            "age": "41",
            "gender": "Female",
            "appearance": "Imposing and immaculate, with silver-white hair swept back and eyes like polished obsidian. Her armour is black and ceremonial. She smiles rarely — and when she does, it never reaches her eyes.",
            "personality": "Razor-sharp intellect wrapped in glacial composure. True believer who has committed monstrous acts for a vision of peace. Respects strength and despises weakness. Haunted by the cost of her choices.",
            "backstory": "Once a revolutionary fighting the same system she now commands. She made a deal — took control to steer it from within. Forty years of compromise has made her the thing she once fought. She knows this. She has chosen not to care.",
            "motivations": "Maintain order at any cost. Prove that the ends justify the means. Prevent the chaos she believes the protagonist will unleash.",
            "abilities": "Master strategist. Gifted in arcane suppression magic. Commands absolute loyalty from the Silence Syndicate.",
            "flaws": "Cannot admit she was wrong without destroying her identity. Underestimates personal connection as a force. Deeply lonely.",
            "relationships": "Views the protagonist as a dangerous child. Has a genuine, fractured bond with her second-in-command who questions her.",
            "arc": "Forced to confront whether the world she built is worth the price — with no certainty she can change.",
            "quotes": '"Order is not given. It is taken." | "You think you\'re the hero of this story. Every monster does." | "I built walls to keep the chaos out. I never noticed I\'d locked myself inside."',
            "avatar_color": "#e94560"
        },
        {
            "name": "Mira Ashcroft",
            "role": "Ally",
            "archetype": "The Wise Fool",
            "age": "19",
            "gender": "Female",
            "appearance": "Small and quick, with a perpetual ink stain on her fingers and a battered satchel always overflowing with books. Bright amber eyes that miss nothing. Dresses in layers like she expects the weather to betray her.",
            "personality": "Effervescent optimism that has somehow survived real hardship. Talks fast when nervous (always). Deeply empathetic. Hides genuine courage behind self-deprecating humor.",
            "backstory": "A scholar's apprentice who was cataloguing forbidden texts when she stumbled into something she shouldn't have. Instead of running, she took notes. She knows more about the ancient bloodlines than anyone alive — and has been running from the people who want that knowledge ever since.",
            "motivations": "Knowledge for its own sake. Protecting her friends. Proving that a small person can change a big story.",
            "abilities": "Encyclopedic knowledge of history and lore. Can decipher ancient scripts. Surprisingly effective with improvised tools.",
            "flaws": "Overthinks into paralysis under real pressure. Terrible at lying. Dangerously trusting.",
            "relationships": "Genuine warmth toward Kael that he doesn't know how to handle. Awe and terror of Ashara in equal measure.",
            "arc": "From passive observer of history to active maker of it.",
            "quotes": '"I\'ve read about days like this. They never end well for the supporting cast." | "Knowledge is armor. Unfortunately it\'s made of paper." | "Someone has to write this down. Might as well be me."',
            "avatar_color": "#00d4aa"
        },
        {
            "name": "Ashara vel Caine",
            "role": "Rival",
            "archetype": "The Fallen Knight",
            "age": "33",
            "gender": "Non-binary",
            "appearance": "Built like a statue and moves like one too — controlled, deliberate, intimidating. Cropped auburn hair and a face full of old and new scars. Eyes the colour of gunmetal. Carries two shortswords crossed at the back.",
            "personality": "Brutally direct. Has no patience for self-pity including their own. A dry, black sense of humour. Honour is everything — and they are very specific about what honour means.",
            "backstory": "A disgraced Knight of the Eternal Flame, stripped of rank after refusing an order to massacre a village. They've been working as a mercenary since, taking only jobs that don't make them sick to complete. The protagonist's quest is the first thing in years that has made them feel something.",
            "motivations": "Redemption on their own terms. Prove that honour is a choice, not a rank. End the system that put them in the position to refuse that order.",
            "abilities": "Exceptional dual-blade combatant. Tactical genius in close-quarters. Can read a battlefield in seconds.",
            "flaws": "Inflexible moral code that can become a liability. Refuses to ask for help. Self-destructive.",
            "relationships": "Reluctant respect for Kael's instincts. Protective of Mira, which surprises everyone, including them.",
            "arc": "From someone defined by what they refused to do, to someone defined by what they choose to do.",
            "quotes": '"I don\'t work for causes. I work for people." | "Honour isn\'t about following orders. It\'s about knowing which ones to break." | "Don\'t mistake my patience for forgiveness."',
            "avatar_color": "#f7a325"
        }
    ]
    return chars[:count]

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    return render_template('index.html', projects=projects)

@app.route('/create', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        title = request.form.get('title', 'Untitled Project')
        genre = request.form.get('genre', 'Fantasy')
        project = Project(title=title, genre=genre)
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('create_narrative', project_id=project.id))
    return render_template('create_project.html')

@app.route('/project/<int:project_id>/narrative/create', methods=['GET', 'POST'])
def create_narrative(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        specs = {
            'genre': request.form.get('genre'),
            'sub_genre': request.form.get('sub_genre'),
            'setting': request.form.get('setting'),
            'time_period': request.form.get('time_period'),
            'tone': request.form.get('tone'),
            'plot_type': request.form.get('plot_type'),
            'target_audience': request.form.get('target_audience'),
            'themes_input': request.form.get('themes_input'),
            'narrative_length': request.form.get('narrative_length'),
            'protagonist_archetype': request.form.get('protagonist_archetype'),
            'antagonist_type': request.form.get('antagonist_type'),
            'world_type': request.form.get('world_type'),
            'magic_system': request.form.get('magic_system'),
            'tech_level': request.form.get('tech_level'),
            'extra_notes': request.form.get('extra_notes'),
        }
        result = generate_narrative_ai(specs)
        
        plot_acts_json = json.dumps(result.get('plot_acts', []))

        narrative = Narrative(
            project_id=project_id,
            title=result.get('title'),
            synopsis=result.get('synopsis'),
            full_narrative=result.get('full_narrative'),
            world_building=result.get('world_building'),
            main_conflict=result.get('main_conflict'),
            themes=result.get('themes'),
            plot_acts=plot_acts_json,
            **specs
        )
        db.session.add(narrative)
        project.title = result.get('title', project.title)
        project.genre = specs.get('genre', project.genre)
        db.session.commit()
        return redirect(url_for('view_narrative', project_id=project_id))
    return render_template('create_narrative.html', project=project)

@app.route('/project/<int:project_id>/narrative')
def view_narrative(project_id):
    project = Project.query.get_or_404(project_id)
    narrative = project.narrative
    plot_acts = []
    if narrative and narrative.plot_acts:
        try:
            plot_acts = json.loads(narrative.plot_acts)
        except:
            plot_acts = []
    return render_template('view_narrative.html', project=project, narrative=narrative, plot_acts=plot_acts)

@app.route('/project/<int:project_id>/narrative/edit', methods=['GET', 'POST'])
def edit_narrative(project_id):
    project = Project.query.get_or_404(project_id)
    narrative = project.narrative
    plot_acts = []
    if narrative and narrative.plot_acts:
        try:
            plot_acts = json.loads(narrative.plot_acts)
        except:
            plot_acts = []

    if request.method == 'POST':
        narrative.title = request.form.get('title', narrative.title)
        narrative.synopsis = request.form.get('synopsis', narrative.synopsis)
        narrative.full_narrative = request.form.get('full_narrative', narrative.full_narrative)
        narrative.world_building = request.form.get('world_building', narrative.world_building)
        narrative.main_conflict = request.form.get('main_conflict', narrative.main_conflict)
        narrative.themes = request.form.get('themes', narrative.themes)
        narrative.genre = request.form.get('genre', narrative.genre)
        narrative.tone = request.form.get('tone', narrative.tone)
        narrative.setting = request.form.get('setting', narrative.setting)
        narrative.extra_notes = request.form.get('extra_notes', narrative.extra_notes)
        
        # Update plot acts
        acts = []
        act_titles = request.form.getlist('act_title[]')
        act_descs = request.form.getlist('act_desc[]')
        for t, d in zip(act_titles, act_descs):
            acts.append({"act": t, "description": d})
        narrative.plot_acts = json.dumps(acts)
        project.title = narrative.title
        db.session.commit()
        return redirect(url_for('view_narrative', project_id=project_id))

    return render_template('edit_narrative.html', project=project, narrative=narrative, plot_acts=plot_acts)

@app.route('/project/<int:project_id>/characters')
def view_characters(project_id):
    project = Project.query.get_or_404(project_id)
    characters = Character.query.filter_by(project_id=project_id).all()
    return render_template('characters.html', project=project, characters=characters)

@app.route('/project/<int:project_id>/characters/generate', methods=['POST'])
def generate_characters(project_id):
    project = Project.query.get_or_404(project_id)
    narrative = project.narrative
    if not narrative:
        return jsonify({'error': 'No narrative found'}), 400
    
    count = int(request.form.get('count', 4))
    # Clear existing characters
    Character.query.filter_by(project_id=project_id).delete()
    db.session.commit()
    
    chars_data = generate_characters_ai(narrative, count)
    for c in chars_data:
        name = c.get('name', 'Unknown')
        initials = ''.join([w[0].upper() for w in name.split()[:2]])
        char = Character(
            project_id=project_id,
            name=name,
            role=c.get('role'),
            archetype=c.get('archetype'),
            age=c.get('age'),
            gender=c.get('gender'),
            appearance=c.get('appearance'),
            personality=c.get('personality'),
            backstory=c.get('backstory'),
            motivations=c.get('motivations'),
            abilities=c.get('abilities'),
            flaws=c.get('flaws'),
            relationships=c.get('relationships'),
            arc=c.get('arc'),
            quotes=c.get('quotes'),
            avatar_color=c.get('avatar_color', '#6c63ff'),
            avatar_initials=initials
        )
        db.session.add(char)
    db.session.commit()
    return redirect(url_for('view_characters', project_id=project_id))

@app.route('/project/<int:project_id>/character/<int:char_id>')
def view_character(project_id, char_id):
    project = Project.query.get_or_404(project_id)
    character = Character.query.get_or_404(char_id)
    return render_template('character_detail.html', project=project, character=character)

@app.route('/project/<int:project_id>/character/<int:char_id>/edit', methods=['GET', 'POST'])
def edit_character(project_id, char_id):
    project = Project.query.get_or_404(project_id)
    character = Character.query.get_or_404(char_id)
    if request.method == 'POST':
        character.name = request.form.get('name', character.name)
        character.role = request.form.get('role', character.role)
        character.archetype = request.form.get('archetype', character.archetype)
        character.age = request.form.get('age', character.age)
        character.gender = request.form.get('gender', character.gender)
        character.appearance = request.form.get('appearance', character.appearance)
        character.personality = request.form.get('personality', character.personality)
        character.backstory = request.form.get('backstory', character.backstory)
        character.motivations = request.form.get('motivations', character.motivations)
        character.abilities = request.form.get('abilities', character.abilities)
        character.flaws = request.form.get('flaws', character.flaws)
        character.relationships = request.form.get('relationships', character.relationships)
        character.arc = request.form.get('arc', character.arc)
        character.quotes = request.form.get('quotes', character.quotes)
        character.avatar_color = request.form.get('avatar_color', character.avatar_color)
        initials = ''.join([w[0].upper() for w in character.name.split()[:2]])
        character.avatar_initials = initials
        db.session.commit()
        return redirect(url_for('view_character', project_id=project_id, char_id=char_id))
    return render_template('edit_character.html', project=project, character=character)

@app.route('/project/<int:project_id>/character/add', methods=['GET', 'POST'])
def add_character(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        name = request.form.get('name', 'New Character')
        initials = ''.join([w[0].upper() for w in name.split()[:2]])
        char = Character(
            project_id=project_id,
            name=name,
            role=request.form.get('role'),
            archetype=request.form.get('archetype'),
            age=request.form.get('age'),
            gender=request.form.get('gender'),
            appearance=request.form.get('appearance'),
            personality=request.form.get('personality'),
            backstory=request.form.get('backstory'),
            motivations=request.form.get('motivations'),
            abilities=request.form.get('abilities'),
            flaws=request.form.get('flaws'),
            relationships=request.form.get('relationships'),
            arc=request.form.get('arc'),
            quotes=request.form.get('quotes'),
            avatar_color=request.form.get('avatar_color', '#6c63ff'),
            avatar_initials=initials
        )
        db.session.add(char)
        db.session.commit()
        return redirect(url_for('view_characters', project_id=project_id))
    return render_template('add_character.html', project=project)

@app.route('/project/<int:project_id>/character/<int:char_id>/delete', methods=['POST'])
def delete_character(project_id, char_id):
    char = Character.query.get_or_404(char_id)
    db.session.delete(char)
    db.session.commit()
    return redirect(url_for('view_characters', project_id=project_id))

@app.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/api/check-key')
def check_key():
    key = os.getenv('GEMINI_API_KEY')
    return jsonify({'has_key': bool(key)})

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        api_key = request.form.get('api_key', '')
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_path, 'w') as f:
            f.write(f'GEMINI_API_KEY={api_key}\n')
        load_dotenv(override=True)
        return redirect(url_for('settings'))
    has_key = bool(os.getenv('GEMINI_API_KEY'))
    return render_template('settings.html', has_key=has_key)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
