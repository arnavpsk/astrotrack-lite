from pathlib import Path
import io
import csv
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, send_file, flash, redirect, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / 'data' / 'astronomy_catalogue.csv'
app = Flask(__name__)
app.secret_key = 'astrotrack-lite-local-demo-key'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
CATEGORIES = ['Galaxy', 'Moon', 'Nebula', 'Planet', 'Satellite', 'Star']
RESOURCES = [
 ('ISRO Official Website','Indian space missions, launches, and programme updates','ISRO','https://www.isro.gov.in/'),
 ('ISRO Student Resources','Learning and student outreach information','Education','https://www.isro.gov.in/Students.html'),
 ('ISRO Science Data','Scientific data and mission resources','Data','https://www.isro.gov.in/Sciencedata.html'),
 ('Bhuvan Geoportal','Indian geospatial imagery and thematic maps','Earth observation','https://bhuvan.nrsc.gov.in/'),
 ('Bhoonidhi Satellite Data','Satellite remote-sensing data access portal','Earth observation','https://bhoonidhi.nrsc.gov.in/'),
 ('NASA Eyes','Explore planets, spacecraft, and missions in 3D','NASA','https://eyes.nasa.gov/'),
 ('Your Name in Landsat','Explore patterns in Earth imagery','Earth observation','https://science.nasa.gov/specials/your-name-in-landsat/'),
 ('NASA Open Data','Search NASA open datasets','Data','https://data.nasa.gov/')]
QUESTIONS = [
 {'topic':'Solar System','q':'Which planet is known as the Red Planet?','options':['Venus','Mars','Jupiter','Mercury'],'answer':'Mars','why':'Iron-rich dust gives Mars its familiar reddish appearance.'},
 {'topic':'Solar System','q':'Which is the largest planet in our Solar System?','options':['Earth','Saturn','Jupiter','Neptune'],'answer':'Jupiter','why':'Jupiter is the largest planet by diameter and mass.'},
 {'topic':'Solar System','q':'What is the name of Earth’s natural satellite?','options':['Europa','Titan','The Moon','Phobos'],'answer':'The Moon','why':'The Moon is Earth’s only natural satellite.'},
 {'topic':'Stars and Galaxies','q':'What is the closest star to Earth?','options':['Sirius','The Sun','Proxima Centauri','Vega'],'answer':'The Sun','why':'The Sun is the star at the centre of our Solar System.'},
 {'topic':'Stars and Galaxies','q':'What type of galaxy is the Milky Way?','options':['Elliptical','Irregular','Spiral barred','Ring only'],'answer':'Spiral barred','why':'The Milky Way is classified as a barred spiral galaxy.'},
 {'topic':'Stars and Galaxies','q':'A light-year measures what?','options':['Time','Distance','Brightness','Temperature'],'answer':'Distance','why':'A light-year is the distance light travels in one year.'},
 {'topic':'Space Missions','q':'Which Indian mission made a soft landing near the Moon’s south polar region in 2023?','options':['Mangalyaan','Chandrayaan-3','Aditya-L1','Astrosat'],'answer':'Chandrayaan-3','why':'Chandrayaan-3 achieved a lunar soft landing in August 2023.'},
 {'topic':'Space Missions','q':'Which space telescope observes primarily in infrared?','options':['James Webb Space Telescope','Hubble only','Voyager 1','MAVEN'],'answer':'James Webb Space Telescope','why':'JWST is designed to observe mainly infrared wavelengths.'},
 {'topic':'Space Missions','q':'What does ISRO stand for?','options':['Indian Space Research Organisation','International Satellite Research Office','Indian Science Rocket Office','Interstellar Space Research Organisation'],'answer':'Indian Space Research Organisation','why':'ISRO is India’s national space agency.'},
 {'topic':'Satellites/Earth Observation','q':'What is a common use of Earth-observation satellites?','options':['Measure soil and vegetation','Create gravity','Stop weather','Produce oxygen'],'answer':'Measure soil and vegetation','why':'Remote-sensing satellites help monitor land, water, crops, and environmental change.'},
 {'topic':'Satellites/Earth Observation','q':'A geostationary satellite appears fixed relative to which point?','options':['The Moon','A point on Earth','The Sun at all times','Mars'],'answer':'A point on Earth','why':'Its orbital period matches Earth’s rotation, above the equator.'},
 {'topic':'Satellites/Earth Observation','q':'What does GPS help determine?','options':['Location and time','Star age directly','Planet composition','Solar temperature'],'answer':'Location and time','why':'GNSS satellites transmit signals used to calculate position and precise time.'}]

def load_catalogue():
    return pd.read_csv(DATA_PATH)

def make_chart(series, kind='bar', xlabel='', ylabel='Count'):
    fig, ax = plt.subplots(figsize=(7, 3.2))
    if kind == 'hist':
        ax.hist(series.dropna(), bins=10, edgecolor='white', color='#8b7cf6')
    else:
        series.plot(kind='bar', ax=ax, color='#5d9cff')
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_facecolor('#111b32'); fig.patch.set_facecolor('#111b32')
    ax.tick_params(colors='#dbe7ff'); ax.xaxis.label.set_color('#dbe7ff'); ax.yaxis.label.set_color('#dbe7ff')
    for spine in ax.spines.values(): spine.set_color('#344362')
    fig.tight_layout(); out = io.BytesIO(); fig.savefig(out, format='png', dpi=130, facecolor=fig.get_facecolor()); plt.close(fig); out.seek(0)
    import base64
    return base64.b64encode(out.read()).decode('ascii')

@app.route('/')
def dashboard():
    df = load_catalogue()
    counts = df['category'].value_counts().reindex(CATEGORIES, fill_value=0)
    facts = [
      ('A day on Venus','Venus rotates so slowly that one rotation takes longer than its orbit around the Sun.' ,'https://science.nasa.gov/venus/'),
      ('The scale of the Milky Way','Our Solar System is one small part of the Milky Way galaxy.','https://science.nasa.gov/universe/galaxies/'),
      ('Earth observation','Satellites help monitor land use, vegetation, oceans, and natural hazards.','https://earthdata.nasa.gov/')]
    return render_template('dashboard.html', df=df, total=len(df), ncat=df.category.nunique(), meanmag=round(df.apparent_magnitude.mean(),2), farthest=df.loc[df.distance_ly.idxmax()], counts=counts, category_chart=make_chart(counts), mag_chart=make_chart(df.apparent_magnitude,'hist','Apparent magnitude','Objects'), years=f"{int(df.discovery_year.min())}–{int(df.discovery_year.max())}", facts=facts)

@app.route('/explore', methods=['GET','POST'])
def explore():
    df = load_catalogue()
    query = request.values.get('q','').strip()
    category = request.values.get('category','All')
    if query: df = df[df['name'].str.contains(query, case=False, na=False)]
    if category in CATEGORIES: df = df[df.category == category]
    result = None
    if request.method == 'POST' and 'csvfile' in request.files:
        file = request.files['csvfile']
        if not file.filename or not file.filename.lower().endswith('.csv'):
            flash('Choose a CSV file with a .csv extension.', 'error')
        else:
            try:
                uploaded = pd.read_csv(file, nrows=10000)
                if uploaded.empty: raise ValueError('The CSV contains no data rows.')
                if len(uploaded.columns) == 0: raise ValueError('No columns were found.')
                num = uploaded.select_dtypes(include=np.number)
                result = {'preview': uploaded.head(8).to_html(classes='data-table', index=False, border=0), 'rows':len(uploaded), 'cols':len(uploaded.columns), 'missing':int(uploaded.isna().sum().sum()), 'summary':num.describe().round(2).to_html(classes='data-table', border=0) if not num.empty else None, 'numeric':not num.empty}
                if not num.empty:
                    col = num.columns[0]
                    result['hist'] = make_chart(num[col], 'hist', col, 'Frequency')
                result['columns'] = ', '.join(map(str, uploaded.columns))
            except Exception as exc:
                flash(f'Could not read this CSV: {exc}', 'error')
    return render_template('explore.html', objects=df.to_dict('records'), categories=CATEGORIES, selected=category, q=query, result=result)

@app.route('/download')
def download():
    df = load_catalogue(); output = io.BytesIO(df.to_csv(index=False).encode('utf-8'))
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='astrotrack_catalogue.csv')

@app.route('/quiz', methods=['GET','POST'])
def quiz():
    index = int(request.values.get('index', 0))
    index = max(0, min(index, len(QUESTIONS)-1))
    selected = request.form.get('answer') if request.method == 'POST' else None
    score = int(request.form.get('score',0)) if request.method == 'POST' else 0
    answered = int(request.form.get('answered',0)) if request.method == 'POST' else 0
    feedback = None
    if request.method == 'POST':
        if selected:
            correct = selected == QUESTIONS[index]['answer']; score += int(correct); answered += 1
            feedback = {'correct':correct,'message':'Correct!' if correct else 'Not quite.', 'why':QUESTIONS[index]['why'], 'answer':QUESTIONS[index]['answer']}
        if request.form.get('action') == 'restart': index=0; score=0; answered=0; feedback=None
        elif request.form.get('action') == 'next': index = (index + 1) % len(QUESTIONS); feedback=None
    return render_template('quiz.html', question=QUESTIONS[index], index=index, total=len(QUESTIONS), score=score, answered=answered, feedback=feedback)

@app.route('/resources')
def resources(): return render_template('resources.html', resources=RESOURCES)

@app.errorhandler(413)
def too_large(_): return 'File too large. Maximum upload size is 5 MB.', 413

if __name__ == '__main__': app.run(debug=True)
