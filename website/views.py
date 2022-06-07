import flask
from flask import Blueprint, render_template, request, url_for, redirect, flash, jsonify, send_file, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import json
from .models import File, db, User
from . import UPLOAD_FOLDER, app
from os import path, remove

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
                file_name = secure_filename(file.filename)
                file_exists = File.query.filter_by(file_name=file_name, file_owner=current_user.id).first()
                if file and allowed_file(file.filename) and not file_exists:
                    print(path.join(app.config['UPLOAD_FOLDER'], current_user.username, file_name))
                    file.save(path.join(app.config['UPLOAD_FOLDER'], current_user.username, file_name))
                    completeName = path.join(UPLOAD_FOLDER, current_user.username, file_name)
                    print(file_name)
                    new_file = File(file_owner=current_user.id, file_name=file.filename, file_location=completeName,
                                    is_owner=1)
                    db.session.add(new_file)
                    db.session.commit()
                    flash(file.filename + ' uploaded successfully', category='success')
                else:
                    flash('File ' + file.filename + ' is not allowed', category='error')
    return render_template("home.html", user=current_user)


@views.route('/delete-file', methods=['POST'])
@login_required
def delete_file():
    if request.method == 'POST':
        data = json.loads(request.data)
        fileId = data['fileId']
        types = data['type']
        print(types)
        file = File.query.get(fileId)
        if file:
            # type 1->delete 2->share 3->download
            if types == 1:  # delete file
                if file.file_owner == current_user.id:
                    db.session.delete(file)
                    db.session.commit()
                    file_path = file.file_location
                    filename = file.file_name
                    print(file_path)
                    if path.exists(file_path) and file.is_owner == 1:
                        # all files with the same name that are not the owner aka owner=0 aka shared file
                        shared_files = File.query.filter_by(file_name=filename, is_owner=0).first()
                        if shared_files:
                            if shared_files is not list:
                                sharedfile_path = shared_files.file_location
                                remove(sharedfile_path)
                                db.session.delete(shared_files)
                                db.session.commit()
                            else:
                                for shared_file in shared_files:
                                    db.session.delete(shared_file)
                                    db.session.commit()
                        # check if owner is deleting
                        remove(file_path)
                        flash(filename + ' deleted successfully', category='success')
            if types == 2:  # share file
                username = data['username']
                print(username)
                user = User.query.filter_by(username=username).first()
                if user:
                    user_file = File.query.filter_by(file_owner=user.id, file_name=file.file_name).first()
                    if not user_file:
                        new_file = File(file_owner=user.id, file_name=file.file_name, file_location=file.file_location,
                                        is_owner=0)
                        db.session.add(new_file)
                        db.session.commit()
                        flash(file.file_name + ' shared with ' + username + ' successfully', category='success')
                    else:
                        flash(file.file_name + ' already shared with this user', category='error')
                else:
                    flash('User ' + username + ' does not exist', category='error')
            if types == 3:
                return redirect(url_for('views.download', file_name=file.file_name))

    return jsonify({})


@views.route('/download/<file_id>',methods=['GET','POST'])
@login_required
def download(file_id):
    print(file_id)
    test = path.join(app.config['UPLOAD_FOLDER'], current_user.username,file_id)
    print(test)
    return send_file(path.join(app.config['UPLOAD_FOLDER'], current_user.username,file_id), as_attachment=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
