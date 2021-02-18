from flask import render_template, redirect, url_for, abort, flash,current_app
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import Role, User,Files
from ..decorators import admin_required


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
#    files =Files.query.get(filerecipient=user.phone)
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    app = current_app._get_current_object()
    form = EditProfileForm()
    if form.validate_on_submit():
        filename = form.uploadfile.data.filename
        files = Files(filesender = form.filesender.data,
                        filerecipient = form.filerecipient.data,
                        filediscription = form.filediscription.data,
                        filename = form.uploadfile.data.filename)
        if Files.query.filter_by(filename=filename).first():
            flash('系统中已存在此文件名，请修改文件名.')
        else:
            db.session.add(files)
            db.session.commit()        
            form.uploadfile.data.save(app.config['UPLOAD_FOLDER']+filename)
            flash('文件上传成功.')
        # return redirect(url_for('.user', username=current_user.username))
    form.filesender.data=current_user.phone
    # form.name.data = current_user.name
    # form.location.data = current_user.location
    # form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.phone = form.phone.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.phone.data = user.phone
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
