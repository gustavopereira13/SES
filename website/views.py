import flask
from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from .models import File, db
from . import UPLOAD_FOLDER, app
from os import path

views = Blueprint('views', __name__)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part', category='error')
            return redirect(request.url)
        files = request.files.getlist('files[]')

        print(len(files))
        if len(files) >= 1:
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(path.join(app.config['UPLOAD_FOLDER'], filename))
                    completeName = path.join(UPLOAD_FOLDER, filename + ".txt")
                    print(filename)
                    new_file = File(file_owner=current_user.id,file_name=file.filename, file_location=completeName)
                    db.session.add(new_file)
                    db.session.commit()
                else:
                    flash('File '+file.filename+' is not allowed', category='error')
    return render_template("home.html", user=current_user)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
