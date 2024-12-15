from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
UPLOAD_FOLDER = '/home/user/PycharmProjects/indeed_scraper/uploads'
ALLOWED_EXTENSIONS = {'json'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def display_jobs():
    jobs = []
    job_count = 0

    if request.method == 'POST':
        # Check if the post request has the file part
        if 'json_file' not in request.files:
            return redirect(request.url)
        file = request.files['json_file']
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            jobs = load_json_file(filepath)
            job_count = len(jobs)

    return render_template("table.html", jobs=jobs, job_count=job_count)

def load_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

if __name__ == '__main__':
    app.run(debug=True)