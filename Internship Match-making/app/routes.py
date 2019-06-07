from datetime import datetime, tzinfo
import time, os
from flask import render_template, flash, redirect, url_for, request, send_from_directory, session
from flask.json import jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import Aborter
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    HostInformation, UserRequirement, HostRequirement, ITField
from app.models import User, Host, URequirement, Student, Internship, InternshipCategory, State, City, \
    UInternshipPosition, ItFieldDb,  UItFieldDb, \
    Application, Invitation, Match
from werkzeug.utils import secure_filename


timeslot = ["09:00:00 ", "10:30:00 ", "12:00:00 ", "13:30:00 ", "15:00:00 "]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'pdf'])

app.config['UPLOAD_FOLDER'] = os.getcwd() + "/files"


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.is_administrator():
        return redirect(url_for('administrator', username=current_user.username))
    else:
        user = User.query.filter_by(username=current_user.username).first_or_404()
        if user.role == 'Host':
            return redirect(url_for('host_confirmation', hostname=current_user.username))
        else:
            return redirect(url_for('confirm_information', username=current_user.username))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('edit_profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # else:
        # db.session.add(user)
        # db.session.commit()
        login_user(user, remember=form.remember_me.data)
        session['user_id'] = user.id
        print(user.role)
        # print(session['role'])
        # if form.role.data==session['role']:

        if user.role == "Host":
            return redirect(url_for('host_confirmation', hostname=current_user.username))
        if user.role == "Student":
            return redirect(url_for('confirm_information'))
        if user.role == "Administrator":
            return redirect(url_for('viewMatches'))
        # else:
        #     flash("Please choose the correct identity!")
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# @app.route('/register', methods=['GET', 'POST'])
# @login_required
# def host():


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        session['role'] = request.form['role']
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        if request.form['role'] == 'Host':
            host = Host(id=user.id, hostname=user.username, email=user.email)
            db.session.add(host)
            db.session.commit()
        if request.form['role'] == 'Student':
            student = Student(id=user.id, username=user.username, email=user.email)
            db.session.add(student)
            db.session.commit()
        flash('Congratulations, you are now a registered ' + str(user.role) + '!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.role == 'Host':
        return redirect(url_for('host_confirmation', hostname=current_user.username))
    else:
        return redirect(url_for('confirm_information', username=current_user.username))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # form = Form(csrf_enabled=False)
    current_student = Student.query.filter_by(id=current_user.id).first()

    form.internship_category.choices = [(category.name, category.name) for category in
                                        InternshipCategory.query.filter_by(
                                            field_category=form.field_category.data).all()]
    form.state.choices = [(state.name, state.name) for state in
                          State.query.filter_by(
                              nation=form.nation.data).all()]

    # print(form.state.choices)
    form.city.choices = [(city.name, city.name) for city in
                         City.query.filter_by(
                             state=form.state.data).all()]
    if form.next.data and form.validate_on_submit():
        current_student.username = form.username.data
        current_student.nation = form.nation.data
        current_student.state = form.state.data
        current_student.city = form.city.data
        current_student.address = form.address.data
        current_student.gender = str(form.gender.data)
        current_student.education_level = str(form.education_level.data)
        current_student.major = form.major.data
        current_student.age = form.age.data
        current_student.email = form.email.data
        current_student.visa = form.visa.data
        current_student.disability = form.disability.data
        current_student.field_category = form.field_category.data
        current_student.internship_category = form.internship_category.data
        # print(request.form['internship_category'])
        current_student.language = form.language.data
        current_student.work_experience = form.work_experience.data
        current_student.work_experience_describe = form.work_experience_describe.data
        # current_student.salary = form.salary.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('host_req_skills', s_h_id=current_student.id))
    elif request.method == 'GET':
        if current_student.field_category:
            form.internship_category.choices = [(category.name, category.name)
                                                for category in
                                                InternshipCategory.query.filter_by(
                                                    field_category=current_student.field_category).all()]
        else:
            form.internship_category.choices = [(category.name, category.name)
                                                for category in
                                                InternshipCategory.query.filter_by(
                                                    field_category=form.field_category.data).all()]

        if current_student.nation:
            form.state.choices = [(state.name, state.name) for state in
                                  State.query.filter_by(
                                      nation=current_student.nation).all()]
        else:
            form.state.choices = [(state.name, state.name) for state in
                                  State.query.filter_by(
                                      nation=form.nation.data).all()]
        if current_student.state:
            form.city.choices = [(city.name, city.name) for city in
                                 City.query.filter_by(
                                     state=current_student.state).all()]
        else:
            form.city.choices = [(city.name, city.name) for city in
                                 City.query.filter_by(
                                     state=form.state.data).all()]
        print(form.city.choices)
        form.username.data = current_student.username
        form.nation.data = current_student.nation
        form.state.data = current_student.state
        form.city.data = current_student.city
        form.address.data = current_student.address
        form.gender.data = current_student.gender
        form.education_level.data = current_student.education_level
        form.major.data = current_student.major
        form.age.data = current_student.age
        form.email.data = current_student.email
        form.visa.data = current_student.visa
        form.disability.data = current_student.disability
        form.field_category.data = current_student.field_category
        # print(InternshipCategory.query.filter_by(id=current_student.internship_category).first())
        # print(current_student.internship_category)

        form.internship_category.data = str(current_student.internship_category)
        form.language.data = current_student.language
        form.work_experience.data = current_student.work_experience
        form.work_experience_describe.data = current_student.work_experience_describe
        # form.salary.data = current_student.salary
    # elif form.ensure_information.data and form.validate_on_submit():
    #     form.username.data = current_student.username
    #     form.gender.data = current_student.gender
    #     form.education_level.data = current_student.education_level
    #     form.major.data = current_student.major
    #     form.email.data = current_student.email
    #     form.age.data = current_student.age
    #     return redirect(url_for('confirm_information'))
    elif form.upload_file.data and form.validate_on_submit():
        return redirect(url_for('upload_file'))
    return render_template('add_profile.html', title='Edit Profile',
                           form=form, current_student=current_student)


@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("File saved successfully!")
        return redirect(url_for('edit_profile'))
    return render_template('upload_file.html', title='Choose File')


@app.route('/confirm_information', methods=['GET', 'POST'])
@login_required
def confirm_information():
    student = Student.query.filter_by(id=current_user.id).all()
    return render_template('confirm_information.html', students=student)


@app.route('/student_details/<username>', methods=['GET', 'POST'])
@login_required
def student_details(username):
    stu_req = URequirement.query.filter_by(username=username).first()
    stu = Student.query.filter_by(username=username).first()
    student = [(stu, stu_req)]
    return render_template('student_information.html', students=student)


@app.route('/internship_details/<internship_id>', methods=['GET', 'POST'])
@login_required
def internship_details(internship_id):
    internship = Internship.query.filter_by(id=internship_id).all()
    return render_template('internship_details.html', students=internship)


@app.route('/viewMatches', methods=['GET', 'POST'])
@login_required
def viewMatches():
    user = User.query.filter_by(username=current_user.username).first()
    matchedList = []
    if user.role == "Host":
        matchedList = Match.query.filter_by(hostname=current_user.username).order_by(Match.internship_name,
                                                                                     Match.match_rate.desc()).all()
    elif user.role == "Student":
        matchedList = Match.query.filter_by(stu_username=current_user.username).order_by(Match.hostname,
                                                                                         Match.internship_name).all()
    else:
        # print("Is Administrator")
        matchedList = Match.query.filter().order_by(Match.hostname, Match.match_rate.desc()).all()
        # print(matchedList)
    return render_template('match_results.html', students=matchedList)


@app.route('/cancelMatch/<match_id>', methods=['GET', 'POST'])
@login_required
def cancelMatch(match_id):
    matched = Match.query.filter_by(id=match_id).first()
    invited = Invitation.query.filter_by(stu_username=matched.stu_username, hostname=matched.hostname,
                                         internship_name=matched.internship_name).first()
    if invited:
        db.session.delete(invited)
    applied = Application.query.filter_by(stu_username=matched.stu_username, hostname=matched.hostname,
                                          internship_name=matched.internship_name).first()
    if applied:
        db.session.delete(applied)
    db.session.delete(matched)
    db.session.commit()
    flash("Match is canceled successfully!")
    return redirect(url_for('viewMatches'))


@app.route('/cancelInvitation/<invitation_id>', methods=['GET', 'POST'])
@login_required
def cancelInvitation(invitation_id):
    invited = Invitation.query.filter_by(id=invitation_id).first()
    if invited:
        db.session.delete(invited)
        db.session.commit()
        flash("Invitation is canceled successfully!")
    return redirect(url_for('viewInvitation', username=current_user.username))


@app.route('/cancelApplication/<application_id>', methods=['GET', 'POST'])
@login_required
def cancelApplication(application_id):
    applied = Application.query.filter_by(id=application_id).first()
    if applied:
        db.session.delete(applied)
    db.session.commit()
    flash("Application is canceled successfully!")
    return redirect(url_for('viewApplication', hostname=current_user.username))


@app.route('/administrator/<username>')
@login_required
def administrator(username):
    if not current_user.is_administrator():
        flash('Permission Denied')
        return redirect(url_for('user', username=current_user.username))
    return render_template('administrator.html', administrator=current_user)


@app.route('/userlist', methods=['GET', 'POST'])
@login_required
def userlist():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id.asc()).paginate(
        page, 10, False)
    next_url = url_for('userlist', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('userlist', page=users.prev_num) \
        if users.has_prev else None
    return render_template('userlist.html', users=users.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/viewInvitation/<username>', methods=['GET', 'POST'])
@login_required
def viewInvitation(username):
    invitations = Invitation.query.filter_by(stu_username=username).all()
    return render_template('invitations.html', students=invitations)


@app.route('/acceptApplication/<application_id>', methods=['GET', 'POST'])
@login_required
def acceptApplication(application_id):
    application = Application.query.filter_by(id=application_id).first()
    hostname = application.hostname
    invited = Invitation.query.filter_by(internship_id=application.internship_id,
                                         hostname=application.hostname,
                                         stu_username=application.stu_username).first()
    matched = Match()
    matched.internship_name = application.internship_name
    matched.stu_username = application.stu_username
    matched.hostname = application.hostname
    matched.internship_id = application.internship_id
    matched.match_rate = application.match_rate
    db.session.delete(application)
    db.session.add(matched)
    if invited is not None:
        db.session.delete(invited)
    db.session.commit()
    applications = Application.query.filter_by(hostname=hostname).all()
    flash("Application Accepted! Now you have a new match!")
    return render_template('applications.html', students=applications)


@app.route('/acceptInvitation/<invitation_id>', methods=['GET', 'POST'])
@login_required
def acceptInvitation(invitation_id):
    invitation = Invitation.query.filter_by(id=invitation_id).first()
    stu_username = invitation.stu_username
    applied = Application.query.filter_by(internship_id=Invitation.internship_id, hostname=Invitation.hostname,
                                          stu_username=Invitation.stu_username).first()
    matched = Match()
    matched.internship_name = invitation.internship_name
    matched.internship_id = invitation.internship_id
    matched.stu_username = invitation.stu_username
    matched.hostname = invitation.hostname
    matched.match_rate = invitation.match_rate
    db.session.delete(invitation)
    db.session.add(matched)
    if applied is not None:
        db.session.delete(applied)
    db.session.commit()
    invitations = Invitation.query.filter_by(stu_username=stu_username).all()
    flash("Invitation Accepted! Now you have a new match!")
    return render_template('invitations.html', students=invitations)


@app.route('/viewApplication/<hostname>', methods=['GET', 'POST'])
@login_required
def viewApplication(hostname):
    applications = Application.query.filter_by(hostname=hostname).all()
    return render_template('applications.html', students=applications)


@app.route('/apply/<internship_id>', methods=['GET', 'POST'])
@login_required
def apply(internship_id):
    internship = Internship.query.filter_by(id=internship_id).first()
    hostname = str(internship.hostname)
    match_rate = float(request.args.get('match_rate'))
    applied = Application.query.filter_by(internship_id=internship_id, hostname=hostname,
                                          stu_username=current_user.username).first()
    matched = Match.query.filter_by(internship_id=internship_id, hostname=hostname,
                                    stu_username=current_user.username).first()
    if applied == None and matched == None:
        application = Application()
        application.hostname = hostname
        application.internship_id = internship_id
        application.stu_username = current_user.username
        application.internship_name = internship.internship_name
        application.match_rate = match_rate
        db.session.add(application)
        db.session.commit()
        flash("Application has been recorded!")
    else:
        flash("You have already applied or matched this internship!")

    return redirect(url_for('matchedHosts', username=current_user.username))


@app.route('/invite/', methods=['GET', 'POST'])
@login_required
def invite():
    internship_id = request.args.get('internship_id')
    username = request.args.get('username')
    match_rate = float(request.args.get('match_rate'))
    internship = Internship.query.filter_by(id=internship_id).first()
    hostname = internship.hostname
    invited = Invitation.query.filter_by(internship_id=internship_id, hostname=hostname, stu_username=username).first()
    matched = Match.query.filter_by(internship_id=internship_id,
                                    hostname=hostname,
                                    stu_username=username).first()

    if invited == None and matched == None:
        invitation = Invitation()
        invitation.hostname = hostname
        invitation.internship_name = internship.internship_name
        invitation.internship_id = internship_id
        invitation.stu_username = username
        invitation.match_rate = match_rate
        db.session.add(invitation)
        db.session.commit()
        flash("Invitation has been recorded!")
    else:
        flash("You have already invited or matched this student for this internship!")
    return redirect(url_for('matchedUsers', req_id=internship_id))


@app.route('/set_permission/<user_id>:<administrator>', methods=['GET', 'POST'])
@login_required
def set_permission(user_id, administrator):
    if administrator == 'True':
        administrator = True
    else:
        administrator = False
    user = User.query.filter_by(id=user_id).first()
    user.administrator = administrator
    db.session.commit()
    if administrator:
        flash('This user has already been set as a administrator.')
    else:
        flash('This user has already been set as a normal user.')
    return redirect(url_for('userlist'))


@app.route('/host_confirmation/<hostname>', methods=['GET', 'POST'])
@login_required
def host_confirmation(hostname):
    requirements = Internship.query.filter_by(hostname=current_user.username).all()
    return render_template('internship_requirement.html', requirements=requirements)


@app.route('/add_host/<hostname>', methods=['GET', 'POST'])
@login_required
def add_host(hostname):
    current_host = Host.query.filter_by(hostname=hostname).first()
    form = HostInformation(hostname)
    requirements = Internship.query.filter_by(hostname=current_user.username).all()
    form.state.choices = [(state.name, state.name) for state in
                          State.query.filter_by(
                              nation=form.nation.data).all()]

    form.city.choices = [(city.name, city.name) for city in
                         City.query.filter_by(
                             state=form.state.data).all()]

    if form.save.data and form.validate_on_submit():
        current_host.state = form.state.data
        current_host.nation = form.nation.data
        current_host.city = form.city.data
        current_host.address = form.address.data
        current_host.hostname = form.hostname.data
        current_host.description = form.description.data
        db.session.commit()
        flash("Data have been saved!")
        return redirect(url_for('add_host', hostname=hostname))
    # if form.validate_on_submit() and form.matchMaking.data:
    #     return redirect(url_for('matchedUsers', hostname=hostname))
    if form.validate_on_submit() and form.back.data:
        requirements = Internship.query.filter_by(hostname=current_user.username).all()
        return render_template('internship_requirement.html', requirements=requirements)

    elif request.method == 'GET':
        form.hostname.data = hostname
        if current_host:
            if current_host.nation:
                form.state.choices = [(state.name, state.name) for state in
                                      State.query.filter_by(
                                          nation=current_host.nation).all()]
            else:
                form.state.choices = [(state.name, state.name) for state in
                                      State.query.filter_by(
                                          nation=form.nation.data).all()]
            if current_host.state:
                form.city.choices = [(city.name, city.name) for city in
                                     City.query.filter_by(
                                         state=current_host.state).all()]
            else:
                form.city.choices = [(city.name, city.name) for city in
                                     City.query.filter_by(
                                         state=form.state.data).all()]
            # print(current_host.city)
            form.description.data = current_host.description
            form.nation.data = current_host.nation
            form.state.data = current_host.state
            # print(City.query.filter_by(name=current_host.city ))
            # print(current_host.city)
            form.city.data = current_host.city
            form.address.data = current_host.address
    # return render_template('add_host.html', title='Host Information', form=form)
    return render_template('host_information.html', form=form)


level = {}
level['highschool'] = 1
level['undergraduate'] = 2
level['postgraduate'] = 3
level['doctor'] = 4


def matchIT(stu, stu_req, stu_info, host_req, detailed_info):
    score = 0
    not_match = 0
    educationList = [k for k, v in level.items() if
                     v >= level[host_req.education_requirement]]
    edl = [k for k, v in level.items() if
           v >= level[stu_req.education_requirement]]
    if stu.visa != "Citizen" and stu.visa != "Permanent Resident" and stu.visa != host_req.visa:
        not_match -= 1
        if host_req.visa_flex:
            return -1
    score += 1

    if stu.gender != host_req.gender_requirement:
        not_match -= 1
        if host_req.gender_flex:
            return -1
    score += 1

    if stu.disability != host_req.disability:
        not_match -= 1
        if host_req.disability_flex:
            return -1
    score += 1

    if stu.major != host_req.major:
        not_match -= 1
        if host_req.major_flex:
            return -1
    score += 1

    if stu.education_level not in educationList:
        not_match -= 1
        if host_req.education_flex:
            return -1
    score += 1

    if host_req.education_requirement not in edl:
        not_match -= 1
        if stu_req.education_flex:
            return -1
    score += 1

    if stu.age < host_req.age:
        not_match -= 1
        if host_req.age_flex:
            return -1
    score += 1

    if stu_req.workdays_requirement < host_req.workdays:
        not_match -= 1
        if host_req.workdays_flex and stu_req.workdays_flex:
            return -1
    score += 1
    print(111)
    print(detailed_info)
    if detailed_info.java_level > stu_info.java_level:
        not_match -= 1
        if detailed_info.java_flex:
            return -1
    if detailed_info.java_level < stu_info.java_level:
        not_match -= 1
        if stu_info.java_flex:
            return -1
    score += 1

    if detailed_info.r_level > stu_info.r_level:
        not_match -= 1
        if detailed_info.r_flex:
            return -1
    if detailed_info.r_level < stu_info.r_level:
        not_match -= 1
        if stu_info.r_flex:
            return -1
    score += 1

    if detailed_info.python_level > stu_info.python_level:
        not_match -= 1
        if detailed_info.python_flex:
            return -1
    if detailed_info.python_level < stu_info.python_level:
        not_match -= 1
        if stu_info.python_flex:
            return -1
    score += 1

    if detailed_info.cplusplus_level > stu_info.cplusplus_level:
        not_match -= 1
        if detailed_info.cplusplus_flex:
            return -1
    if detailed_info.cplusplus_level < stu_info.cplusplus_level:
        not_match -= 1
        if stu_info.cplusplus_flex:
            return -1
    score += 1

    if detailed_info.php_level > stu_info.php_level:
        not_match -= 1
        if detailed_info.php_flex:
            return -1
    if detailed_info.php_level < stu_info.php_level:
        not_match -= 1
        if stu_info.php_flex:
            return -1
    score += 1

    if detailed_info.backend_level > stu_info.backend_level:
        not_match -= 1
        if detailed_info.backend_flex:
            return -1
    if detailed_info.backend_level < stu_info.backend_level:
        not_match -= 1
        if stu_info.backend_flex:
            return -1
    score += 1

    if detailed_info.frontend_level > stu_info.frontend_level:
        not_match -= 1
        if detailed_info.frontend_flex:
            return -1
    if detailed_info.frontend_level < stu_info.frontend_level:
        not_match -= 1
        if stu_info.frontend_flex:
            return -1
    score += 1

    if detailed_info.android_ios_level > stu_info.android_ios_level:
        not_match -= 1
        if detailed_info.android_ios_flex:
            return -1
    if detailed_info.android_ios_level < stu_info.android_ios_level:
        not_match -= 1
        if stu_info.android_ios_flex:
            return -1
    score += 1

    if detailed_info.docker_level > stu_info.docker_level:
        not_match -= 1
        if detailed_info.docker_flex:
            return -1
    if detailed_info.docker_level < stu_info.docker_level:
        not_match -= 1
        if stu_info.docker_flex:
            return -1
    score += 1

    if detailed_info.cloud_level > stu_info.cloud_level:
        not_match -= 1
        if detailed_info.cloud_flex:
            return -1
    if detailed_info.cloud_level < stu_info.cloud_level:
        not_match -= 1
        if stu_info.cloud_flex:
            return -1
    score += 1

    if detailed_info.database_level > stu_info.database_level:
        not_match -= 1
        if detailed_info.database_flex:
            return -1
    if detailed_info.database_level < stu_info.database_level:
        not_match -= 1
        if stu_info.database_flex:
            return -1
    score += 1

    if detailed_info.machine_learning_level > stu_info.machine_learning_level:
        not_match -= 1
        if detailed_info.machine_learning_flex:
            return -1
    if detailed_info.machine_learning_level < stu_info.machine_learning_level:
        not_match -= 1
        if stu_info.machine_learning_flex:
            return -1
    score += 1

    if detailed_info.statistics_level > stu_info.statistics_level:
        not_match -= 1
        if detailed_info.statistics_flex:
            return -1
    if detailed_info.statistics_level < stu_info.statistics_level:
        not_match -= 1
        if stu_info.statistics_flex:
            return -1
    score += 1

    if stu_req.salary > host_req.salary:
        not_match -= 1
        if host_req.salary_flex and stu_req.salary_flex:
            return -1
    score += 1

    if host_req.workplace_nation != stu_req.workplace_nation:
        not_match -= 1
        if stu_req.nation_flex and host_req.nation_flex:
            return -1
    score += 1

    if stu_req.workplace_state != host_req.workplace_state:
        not_match -= 1
        if stu_req.state_flex and host_req.state_flex:
            return -1
    score += 1

    if stu_req.workplace_city != host_req.workplace_city:
        not_match -= 1
        if stu_req.city_flex and host_req.city_flex:
            return -1
    score += 1

    if stu_req.opportunity_to_fulltime_job != host_req.opportunity_to_fulltime_job:
        not_match -= 1
        if host_req.fulltime_flex and stu_req.fulltime_flex:
            return -1
    score += 1

    if stu_req.language_requirement != host_req.language_requirement:
        not_match -= 1
        if host_req.language_flex and stu_req.language_flex:
            return -1
    score += 1

    return (score + not_match) / score


@app.route('/filtered_user_list/<req_id>', methods=['GET', 'POST'])
@login_required
def matchedUsers(req_id):
    host_req = Internship.query.filter_by(id=req_id).first()
    detailed_info = None
    student_skill = None
    selectedStudent = []
    stu_dict = {}
    if host_req != None:
        students = Student.query.filter_by(field_category=host_req.field_category).all()
        # students = Student.query.filter(
        #     and_(
        #         or_(Student.gender == host_req.gender_requirement, not host_req.gender_flex),
        #         or_(Student.education_level.in_(educationList), not host_req.education_flex),
        #         or_(Student.major == host_req.major, not host_req.major_flex),
        #         or_(Student.age >= host_req.age, not host_req.age_flex),
        #         or_(Student.field_category == host_req.field_category),
        #         or_(Student.workdays_requirement < host_req.workdays, not host_req.workdays_flex)
        #     ))
        # ).order_by(desc((Student.gender == host_req.gender_requirement) +
        #                 (Student.education_level.in_(educationList)) +
        #                 (Student.major == host_req.major) +
        #                 (Student.age >= host_req.age)))

        for stu in students:
            stu_req = URequirement.query.filter_by(username=stu.username).first()
            if host_req.field_category == "IT field":
                if stu_req != None:
                    detailed_info = ItFieldDb.query.filter_by(internship_id=req_id).first()
                    stu_info = UItFieldDb.query.filter_by(student_id=stu.id).first()
                    if stu_info != None:
                        score = matchIT(stu, stu_req, stu_info, host_req, detailed_info)
                        if score > -1:
                            stu_dict[stu] = int(score * 10000) / 100

            # elif host_req.field_category == "Education field":
            #     detailed_info = EducationFieldDb.query.filter_by(internship_id=req_id)
            #
            # else:
            #     detailed_info = EngineerFieldDb.query.filter_by(internship_id=req_id)
    # else:
    #     flash("Please complete at least one internship first!")
    #     return url_for('save_host_req',)
    selectedStudent = sorted(stu_dict.items(), key=lambda x: x[1], reverse=True)
    for i in range(0, len(selectedStudent)):
        tempStu = selectedStudent[i]
        selectedStudent[i] = (tempStu[0], req_id, tempStu[1])
    return render_template('fiiltered_user_list.html', students=selectedStudent)


@app.route('/filtered_host_list/<username>', methods=['GET', 'POST'])
@login_required
def matchedHosts(username):
    student = Student.query.filter_by(username=username).first()
    stu_req = URequirement.query.filter_by(username=username).first()
    stu_info = UItFieldDb.query.filter_by(student_id=student.id).first()
    selectedInternships = []
    host_dict = {}
    if stu_req != None:
        internships = Internship.query.filter_by(field_category=student.field_category).all()
        if student.field_category != None:
            if student.field_category == "IT field":
                stu_info = UItFieldDb.query.filter_by(student_id=student.id).first()
                if stu_info != None:
                    for internship in internships:
                        detailed_info = ItFieldDb.query.filter_by(internship_id=internship.id).first()
                        score = matchIT(student, stu_req, stu_info, internship, detailed_info)
                        if score > -1:
                            host_dict[internship] = int(score * 10000) / 100


    elif stu_req == None and stu_info != None:
        flash("Please complete your requirement first!")
        return redirect(url_for('save_user_req'))
    else:
        flash("Please complete your profile and requirement first!")
        return redirect(url_for('edit_profile'))

    selectedInternships = sorted(host_dict.items(), key=lambda x: x[1], reverse=True)
    for i in range(0, len(selectedInternships)):
        tempIntern = selectedInternships[i]
        selectedInternships[i] = (tempIntern[0], tempIntern[1])
    return render_template('filtered_host_list.html', students=selectedInternships)


@app.route('/save_user_req', methods=['GET', 'POST'])
@login_required
def save_user_req():
    stu = Student.query.filter_by(username=current_user.username).first()
    if stu == None or stu.internship_category == None:
        flash("Please complete your profile first!")
        return redirect(url_for('edit_profile'))
    form = UserRequirement(current_user.username)
    form.username.data = current_user.username
    user_req = URequirement.query.filter_by(username=current_user.username).first()
    student = Student.query.filter_by(username=current_user.username).first()

    form.desired_position.choices = [
        (category.internship_position, category.internship_position) for
        category in UInternshipPosition.query.filter_by
        (internship_category=student.internship_category).all()]
    print(student.internship_category)
    print(form.desired_position.choices)
    form.workplace_state.choices = [(state.name, state.name) for state in
                                    State.query.filter_by(
                                        nation=form.workplace_nation.data).all()]

    form.workplace_city.choices = [(city.name, city.name) for city in
                                   City.query.filter_by(
                                       state=form.workplace_state.data).all()]

    if form.validate_on_submit() and form.submit.data:
        if user_req:
            print("already has a requirement")

            user_req.username = form.username.data
            user_req.education_requirement = form.education_requirement.data
            user_req.education_flex = form.education_flex.data
            user_req.salary = int(form.salary.data)
            user_req.salary_flex = form.salary_flex.data

            user_req.workplace_nation = form.workplace_nation.data
            user_req.nation_flex = form.nation_flex.data
            user_req.workplace_state = form.workplace_state.data
            user_req.state_flex = form.state_flex.data
            user_req.workplace_city = form.workplace_city.data
            user_req.city_flex = form.city_flex.data
            user_req.workdays_requirement = form.workdays_requirement.data
            user_req.workdays_flex = form.workdays_flex.data
            user_req.opportunity_to_fulltime_job = form.opportunity_to_fulltime_job.data
            user_req.fulltime_flex = form.fulltime_flex.data
            user_req.language_requirement = form.language_requirement.data
            user_req.language_flex = form.language_flex.data
            user_req.desired_position = form.desired_position.data
            user_req.desired_position_flex = form.desired_position_flex.data
            flash('Data have been saved')
        else:
            user_req = URequirement()
            user_req.username = form.username.data
            user_req.education_requirement = form.education_requirement.data
            user_req.education_flex = form.education_flex.data
            user_req.salary = int(form.salary.data)
            user_req.salary_flex = form.salary_flex.data

            user_req.workplace_nation = form.workplace_nation.data
            user_req.nation_flex = form.nation_flex.data
            user_req.workplace_state = form.workplace_state.data
            user_req.state_flex = form.state_flex.data
            user_req.workplace_city = form.workplace_city.data
            user_req.city_flex = form.city_flex.data
            user_req.workdays_requirement = form.workdays_requirement.data
            user_req.workdays_flex = form.workdays_flex.data
            user_req.opportunity_to_fulltime_job = form.opportunity_to_fulltime_job.data
            user_req.fulltime_flex = form.fulltime_flex.data
            user_req.language_requirement = form.language_requirement.data
            user_req.language_flex = form.language_flex.data
            user_req.desired_position = form.desired_position.data
            user_req.desired_position_flex = form.desired_position_flex.data
            flash('Data have been saved')
            db.session.add(user_req)
        db.session.commit()
        return redirect(url_for('confirm_information'))

    # elif form.validate_on_submit() and form.match_job.data:
    #     if user_req:
    #         return redirect(url_for('matchedHosts', username=current_user.username))

    elif request.method == 'GET':

        if user_req:
            # form.workplace_state.choices = [(state.name, state.name) for state in
            #                                 State.query.filter_by(
            #                                     nation=user_req.workplace_nation).all()]
            #
            # form.workplace_city.choices = [(city.name, city.name) for city in
            #                                City.query.filter_by(
            #                                    state=user_req.workplace_state).all()]
            if user_req.workplace_nation:
                form.workplace_state.choices = [(state.name, state.name) for state in
                                                State.query.filter_by(
                                                    nation=user_req.workplace_nation).all()]
            else:
                form.workplace_state.choices = [(state.name, state.name) for state in
                                                State.query.filter_by(
                                                    nation=form.workplace_nation.data).all()]
            if user_req.workplace_state:
                form.workplace_city.choices = [(city.name, city.name) for city in
                                               City.query.filter_by(
                                                   state=user_req.workplace_state).all()]
            else:
                form.workplace_city.choices = [(city.name, city.name) for city in
                                               City.query.filter_by(
                                                   state=form.workplace_state.data).all()]
            form.education_requirement.data = user_req.education_requirement
            form.education_flex.data = user_req.education_flex
            form.salary.data = user_req.salary
            form.salary_flex.data = user_req.salary_flex

            form.workplace_nation.data = user_req.workplace_nation
            form.nation_flex.data = user_req.nation_flex
            form.workplace_state.data = user_req.workplace_state
            form.state_flex.data = user_req.state_flex
            form.workplace_city.data = user_req.workplace_city
            form.city_flex.data = user_req.city_flex
            form.workdays_requirement.data = user_req.workdays_requirement
            form.workdays_flex.data = user_req.workdays_flex
            form.opportunity_to_fulltime_job.data = user_req.opportunity_to_fulltime_job
            form.fulltime_flex.data = user_req.fulltime_flex
            form.language_requirement.data = user_req.language_requirement
            form.language_flex.data = user_req.language_flex
            form.desired_position.data = user_req.desired_position
            form.desired_position.data = user_req.desired_position
            form.desired_position_flex.data = user_req.desired_position_flex

    return render_template('save_user_req.html', form=form)


@app.route('/save_host_req/<intern_name>', methods=['GET', 'POST'])
@login_required
def save_host_req(intern_name):
    # field={}
    #
    intern_id = None
    if intern_name != "a_totally_new_page":
        intern_id = request.args.get('req_id')
    hostname = current_user.username
    form = HostRequirement(hostname)
    # form.internship_category.choices=[(internship_category.id,internship_category.name) for internship_category in ]
    form.hostname.data = hostname
    form.internship_category.choices = [(category.name, category.name) for category in
                                        InternshipCategory.query.filter_by(
                                            field_category=form.field_category.data).all()]
    form.workplace_state.choices = [(state.name, state.name) for state in
                                    State.query.filter_by(
                                        nation=form.workplace_nation.data).all()]

    form.workplace_city.choices = [(city.name, city.name) for city in
                                   City.query.filter_by(
                                       state=form.workplace_state.data).all()]

    # form.internship_category.choices=[(name1,name2)for (name1,name2) in ]
    if form.next.data and form.validate_on_submit():
        host_req = Internship.query.filter_by(id=intern_id).first()
        if host_req:
            host_req.field_category = form.field_category.data
            host_req.internship_name = form.internship_name.data
            host_req.internship_category = form.internship_category.data
            host_req.age = form.age.data
            host_req.age_flex = form.age_flex.data
            host_req.education_requirement = form.education_requirement.data
            host_req.education_flex = form.education_flex.data
            host_req.gender_requirement = form.gender_requirement.data
            host_req.gender_flex = form.gender_flex.data
            host_req.major = form.major.data
            host_req.major_flex = form.major_flex.data

            host_req.salary = form.salary.data
            host_req.salary_flex = form.salary_flex.data
            host_req.visa = form.visa.data
            host_req.visa_flex = form.visa_flex.data
            host_req.workplace_nation = form.workplace_nation.data
            host_req.nation_flex = form.nation_flex.data
            host_req.workplace_state = form.workplace_state.data
            host_req.state_flex = form.state_flex.data
            host_req.workplace_city = form.workplace_city.data
            host_req.city_flex = form.city_flex.data
            host_req.workdays = form.workdays.data
            host_req.workdays_flex = form.workdays_flex.data
            host_req.opportunity_to_fulltime_job = form.opportunity_to_fulltime_job.data
            host_req.fulltime_flex = form.fulltime_flex.data
            host_req.language_requirement = form.language_requirement.data
            host_req.language_flex = form.language_flex.data
            host_req.disability = form.disability.data
            host_req.disability_flex = form.disability_flex.data

        else:
            host_req = Internship()
            host_req.hostname = form.hostname.data
            host_req.field_category = form.field_category.data
            host_req.internship_name = form.internship_name.data
            host_req.internship_category = form.internship_category.data
            host_req.age = form.age.data
            host_req.age_flex = form.age_flex.data
            host_req.education_requirement = form.education_requirement.data
            host_req.education_flex = form.education_flex.data
            host_req.gender_requirement = form.gender_requirement.data
            host_req.gender_flex = form.gender_flex.data
            host_req.major = form.major.data
            host_req.major_flex = form.major_flex.data

            host_req.salary = form.salary.data
            host_req.salary_flex = form.salary_flex.data
            host_req.visa = form.visa.data
            host_req.visa_flex = form.visa_flex.data
            host_req.workplace_nation = form.workplace_nation.data
            host_req.nation_flex = form.nation_flex.data
            host_req.workplace_state = form.workplace_state.data
            host_req.state_flex = form.state_flex.data
            host_req.workplace_city = form.workplace_city.data
            host_req.city_flex = form.city_flex.data
            host_req.workdays = form.workdays.data
            host_req.workdays_flex = form.workdays_flex.data
            host_req.opportunity_to_fulltime_job = form.opportunity_to_fulltime_job.data
            host_req.fulltime_flex = form.fulltime_flex.data
            host_req.language_requirement = form.language_requirement.data
            host_req.language_flex = form.language_flex.data
            host_req.disability = form.disability.data
            host_req.disability_flex = form.disability_flex.data

            db.session.add(host_req)
        db.session.commit()
        internship_id = Internship.query.filter_by(hostname=hostname,
                                                   internship_name=form.internship_name.data).first().id

        # return render_template('internship_requirement.html', requirements=requirements)
        return redirect(url_for('host_req_skills', s_h_id=internship_id))
    elif request.method == 'GET':

        if intern_name == "a_totally_new_page":
            pass
        else:

            host_req = Internship.query.filter_by(id=intern_id).first()
            print(host_req.internship_name)
            print(host_req.id)
            print(host_req.opportunity_to_fulltime_job)
            if host_req.field_category:
                form.internship_category.choices = [(category.name, category.name) for category in
                                                    InternshipCategory.query.filter_by(
                                                        field_category=host_req.field_category).all()]
            else:
                form.internship_category.choices = [(category.name, category.name) for category in
                                                    InternshipCategory.query.filter_by(
                                                        field_category=form.field_category.data).all()]
            # print( host_req.field_category)
            if host_req.workplace_nation:
                form.workplace_state.choices = [(state.name, state.name) for state in
                                                State.query.filter_by(
                                                    nation=host_req.workplace_nation).all()]
            else:
                form.workplace_state.choices = [(state.name, state.name) for state in
                                                State.query.filter_by(
                                                    nation=form.workplace_nation.data).all()]
            if host_req.workplace_state:
                form.workplace_city.choices = [(city.name, city.name) for city in
                                               City.query.filter_by(
                                                   state=host_req.workplace_state).all()]
            else:
                form.workplace_city.choices = [(city.name, city.name) for city in
                                               City.query.filter_by(
                                                   state=form.workplace_state.data).all()]
            # form.internship_category.choices = [(category.name, category.name) for category in
            #                                     InternshipCategory.query.filter_by(
            #                                         field_category=host_req.field_category).all()]
            if host_req:
                form.field_category.data = host_req.field_category
                form.internship_name.data = host_req.internship_name
                form.internship_category.data = host_req.internship_category
                form.age.data = host_req.age
                form.age_flex.data = host_req.age_flex
                form.education_requirement.data = host_req.education_requirement
                form.education_flex.data = host_req.education_flex
                form.gender_requirement.data = host_req.gender_requirement
                form.gender_flex.data = host_req.gender_flex
                form.major.data = host_req.major
                form.major_flex.data = host_req.major_flex

                form.salary.data = host_req.salary
                form.salary_flex.data = host_req.salary_flex
                form.visa.data = host_req.visa
                form.visa_flex = host_req.visa_flex
                form.workplace_nation.data = host_req.workplace_nation
                form.nation_flex.data = host_req.nation_flex
                form.workplace_state.data = host_req.workplace_state
                form.state_flex.data = host_req.state_flex
                form.workplace_city.data = host_req.workplace_city
                form.city_flex.data = host_req.city_flex
                form.workdays.data = host_req.workdays
                form.workdays_flex.data = host_req.workdays_flex
                print(host_req.opportunity_to_fulltime_job)
                form.opportunity_to_fulltime_job.data = host_req.opportunity_to_fulltime_job
                form.fulltime_flex.data = host_req.fulltime_flex
                form.language_requirement.data = host_req.language_requirement
                form.language_flex.data = host_req.language_flex
                form.disability.data = host_req.disability
                form.disability_flex.data = host_req.disability_flex

    return render_template('save_host_req.html', form=form)


@app.route('/host_req_skills/<s_h_id>', methods=['GET', 'POST'])
@login_required
def host_req_skills(s_h_id):
    category = None
    if current_user.role == "Host":
        category = Internship.query.filter_by(id=s_h_id).first().field_category
        print(category)
    elif current_user.role == "Student":
        category = Student.query.filter_by(id=s_h_id).first().field_category
        print(category)
    # form = None
    # if category == 'IT field' and current_user.role == "Host":
    #     form = ITField()
    #     form.category_name.data = category
    #
    # elif category == 'IT field' and current_user.role == "Student":
    #     form = UITField()
    #     it_method(s_h_id=s_h_id,form=form,category=category)
    #
    # def it_method(s_h_id,form,category):
    if category == 'IT field':
        form = ITField()
        form.category_name.data = category

        if form.validate_on_submit() and form.submit.data:
            it_field = None
            if current_user.role == "Host":
                it_field = ItFieldDb.query.filter_by(internship_id=s_h_id).first()
            elif current_user.role == "Student":
                it_field = UItFieldDb.query.filter_by(student_id=s_h_id).first()
            if it_field:
                if current_user.role == "Host":
                    it_field.internship_id = s_h_id
                elif current_user.role == "Student":
                    it_field.student_id = s_h_id
                it_field.java_level = form.java_level.data
                it_field.java_flex = form.java_flex.data
                it_field.python_level = form.python_level.data
                it_field.python_flex = form.python_flex.data
                it_field.r_level = form.r_level.data
                it_field.r_flex = form.r_flex.data
                it_field.cplusplus_level = form.cplusplus_level.data
                it_field.cplusplus_flex = form.cplusplus_flex.data
                it_field.php_level = form.php_level.data
                it_field.php_flex = form.php_flex.data
                it_field.backend_level = form.backend_level.data
                it_field.backend_flex = form.backend_flex.data
                it_field.frontend_level = form.frontend_level.data
                it_field.frontend_flex = form.frontend_flex.data
                it_field.android_ios_level = form.android_ios_level.data
                it_field.android_ios_flex = form.android_ios_flex.data
                it_field.docker_level = form.docker_level.data
                it_field.docker_flex = form.docker_flex.data
                it_field.cloud_level = form.cloud_level.data
                it_field.cloud_flex = form.cloud_flex.data
                it_field.linux_level = form.linux_level.data
                it_field.linux_flex = form.linux_flex.data
                it_field.database_level = form.database_level.data
                it_field.database_flex = form.database_flex.data
                it_field.statistics_level = form.statistics_level.data
                it_field.statistics_flex = form.statistics_flex.data
                it_field.machine_learning_level = form.machine_learning_level.data
                it_field.machine_learning_flex = form.machine_learning_flex.data
            else:
                if current_user.role == "Host":
                    it_field = ItFieldDb()
                    it_field.internship_id = s_h_id
                    it_field.category_name = category
                elif current_user.role == "Student":
                    it_field = UItFieldDb()
                    it_field.student_id = s_h_id
                    it_field.category_name = category
                it_field.java_level = form.java_level.data
                it_field.java_flex = form.java_flex.data
                it_field.python_level = form.python_level.data
                it_field.python_flex = form.python_flex.data
                it_field.r_level = form.r_level.data
                it_field.r_flex = form.r_flex.data
                it_field.cplusplus_level = form.cplusplus_level.data
                it_field.cplusplus_flex = form.cplusplus_flex.data
                it_field.php_level = form.php_level.data
                it_field.php_flex = form.php_flex.data
                it_field.backend_level = form.backend_level.data
                it_field.backend_flex = form.backend_flex.data
                it_field.frontend_level = form.frontend_level.data
                it_field.frontend_flex = form.frontend_flex.data
                it_field.android_ios_level = form.android_ios_level.data
                it_field.android_ios_flex = form.android_ios_flex.data
                it_field.docker_level = form.docker_level.data
                it_field.docker_flex = form.docker_flex.data
                it_field.cloud_level = form.cloud_level.data
                it_field.cloud_flex = form.cloud_flex.data
                it_field.linux_level = form.linux_level.data
                it_field.linux_flex = form.linux_flex.data
                it_field.database_level = form.database_level.data
                it_field.database_flex = form.database_flex.data
                it_field.statistics_level = form.statistics_level.data
                it_field.statistics_flex = form.statistics_flex.data
                it_field.machine_learning_level = form.machine_learning_level.data
                it_field.machine_learning_flex = form.machine_learning_flex.data
                db.session.add(it_field)
            # engineer_field1 = None
            # education_field1 = None
            # if current_user.role == "Host":
            #     engineer_field1 = EngineerFieldDb.query.filter_by(internship_id=s_h_id).first()
            #     education_field1 = EducationFieldDb.query.filter_by(internship_id=s_h_id).first()
            # elif current_user.role == "Student":
            #     engineer_field1 = UEngineerFieldDb.query.filter_by(student_id=s_h_id).first()
            #     education_field1 = UEducationFieldDb.query.filter_by(student_id=s_h_id).first()
            # if engineer_field1:
            #     db.session.delete(engineer_field1)
            # if education_field1:
            #     db.session.delete(education_field1)
            db.session.commit()
            flash('Data have been saved')
            if current_user.role == "Host":
                hostname = Internship.query.filter_by(id=s_h_id).first()
                hostname = str(hostname)
                print(hostname)
                requirements = Internship.query.filter_by(hostname=hostname).all()
                return render_template('internship_requirement.html', requirements=requirements)
            elif current_user.role == "Student":
                return redirect(url_for('confirm_information'))

        elif form.back.data and form.validate_on_submit():
            if current_user.role == "Host":
                previous_req = Internship.query.filter_by(id=s_h_id).first()
                return redirect(url_for('save_host_req', intern_name=previous_req.internship_name))
            elif current_user.role == "Student":
                return redirect(url_for('edit_profile'))

        elif request.method == "GET":
            it_field = None
            if current_user.role == "Host":
                it_field = ItFieldDb.query.filter_by(internship_id=s_h_id).first()
            elif current_user.role == "Student":
                it_field = UItFieldDb.query.filter_by(student_id=s_h_id).first()
            # print(s_h_id)
            # print(it_field.java_level)
            if it_field:
                form.java_level.data = it_field.java_level
                form.java_flex.data = it_field.java_flex
                form.python_level.data = it_field.python_level
                form.python_flex.data = it_field.python_flex
                form.r_level.data = it_field.r_level
                form.r_flex.data = it_field.r_flex
                form.cplusplus_level.data = it_field.cplusplus_level
                form.cplusplus_flex.data = it_field.cplusplus_flex
                form.php_level.data = it_field.php_level
                form.php_flex.data = it_field.php_flex
                form.backend_level.data = it_field.backend_level
                form.backend_flex.data = it_field.backend_flex
                form.frontend_level.data = it_field.frontend_level
                form.frontend_flex.data = it_field.frontend_flex
                form.android_ios_level.data = it_field.android_ios_level
                form.android_ios_flex.data = it_field.android_ios_flex
                form.database_level.data = it_field.database_level
                form.database_flex.data = it_field.database_flex
                form.cloud_level.data = it_field.cloud_level
                form.cloud_flex.data = it_field.cloud_flex
                form.machine_learning_level.data = it_field.machine_learning_level
                form.machine_learning_flex.data = it_field.machine_learning_flex
                form.statistics_level.data = it_field.statistics_level
                form.statistics_flex.data = it_field.statistics_flex
                form.linux_level.data = it_field.linux_level
                form.linux_flex.data = it_field.linux_flex
                form.docker_level.data = it_field.docker_level
                form.docker_flex.data = it_field.docker_flex
            if current_user.role == "Host":
                return render_template('host_it_field.html', form=form)
            elif current_user.role == "Student":
                return render_template('student_it_field.html', form=form)
    # elif category == 'Engineer field':
    #     form = EngineerField()
    #     form.category_name.data = category
    #     if form.validate_on_submit() and form.submit.data:
    #         engineer_field = None
    #         if current_user.role == "Host":
    #             engineer_field = EngineerFieldDb.query.filter_by(internship_id=s_h_id).first()
    #             print(engineer_field)
    #         elif current_user.role == "Student":
    #             engineer_field = UEngineerFieldDb.query.filter_by(student_id=s_h_id).first()
    #         if engineer_field:
    #             if current_user.role == "Host":
    #                 engineer_field.internship_id = s_h_id
    #             elif current_user.role == "Student":
    #                 engineer_field.student_id = s_h_id
    #             engineer_field.years_of_work_experience = form.years_of_work_experience.data
    #             engineer_field.work_experience_flex = form.work_experience_flex.data
    #             engineer_field.knowledge_oil_gas = form.knowledge_oil_gas.data
    #             engineer_field.oil_gas_flex = form.oil_gas_flex.data
    #             engineer_field.oilfield_petrochemical_experience = form.oilfield_petrochemical_experience.data
    #             engineer_field.oilfield_petrochemical_flex = form.oilfield_petrochemical_flex.data
    #             engineer_field.communicating_interfacing_skills = form.communicating_interfacing_skills.data
    #             engineer_field.communicating_interfacing_flex = form.communicating_interfacing_flex.data
    #             engineer_field.knowledge_of_the_latest_telecommunications_technology = \
    #                 form.knowledge_of_the_latest_telecommunications_technology.data
    #             engineer_field.the_latest_telecommunications_technology_flex = \
    #                 form.the_latest_telecommunications_technology_flex.data
    #             engineer_field.familiar_with_industry_projects = form.familiar_with_industry_projects.data
    #             engineer_field.industry_projects_flex = form.industry_projects_flex.data
    #             engineer_field.engineering_design_experience = form.engineering_design_experience.data
    #             engineer_field.engineering_design_flex = form.engineering_design_flex.data
    #             engineer_field.knowledge_applicable_codes_standards = form.knowledge_applicable_codes_standards.data
    #             engineer_field.applicable_codes_standards_flex = form.applicable_codes_standards_flex.data
    #         else:
    #             if current_user.role == "Host":
    #                 engineer_field = EngineerFieldDb()
    #                 engineer_field.internship_id = s_h_id
    #                 engineer_field.category_name = category
    #             elif current_user.role == "Student":
    #                 engineer_field = UEngineerFieldDb()
    #                 engineer_field.student_id = s_h_id
    #                 engineer_field.category_name = category
    #             engineer_field.years_of_work_experience = form.years_of_work_experience.data
    #             engineer_field.work_experience_flex = form.work_experience_flex.data
    #             engineer_field.knowledge_oil_gas = form.knowledge_oil_gas.data
    #             engineer_field.oil_gas_flex = form.oil_gas_flex.data
    #             engineer_field.oilfield_petrochemical_experience = form.oilfield_petrochemical_experience.data
    #             engineer_field.oilfield_petrochemical_flex = form.oilfield_petrochemical_flex.data
    #             engineer_field.communicating_interfacing_skills = form.communicating_interfacing_skills.data
    #             engineer_field.communicating_interfacing_flex = form.communicating_interfacing_flex.data
    #             engineer_field.knowledge_of_the_latest_telecommunications_technology = \
    #                 form.knowledge_of_the_latest_telecommunications_technology.data
    #             engineer_field.the_latest_telecommunications_technology_flex = \
    #                 form.the_latest_telecommunications_technology_flex.data
    #             engineer_field.familiar_with_industry_projects = form.familiar_with_industry_projects.data
    #             engineer_field.industry_projects_flex = form.industry_projects_flex.data
    #             engineer_field.engineering_design_experience = form.engineering_design_experience.data
    #             engineer_field.engineering_design_flex = form.engineering_design_flex.data
    #             engineer_field.knowledge_applicable_codes_standards = form.knowledge_applicable_codes_standards.data
    #             engineer_field.applicable_codes_standards_flex = form.applicable_codes_standards_flex.data
    #             db.session.add(engineer_field)
    #         it_field1 = None
    #         education_field1 = None
    #         if current_user.role == "Host":
    #             it_field1 = ItFieldDb.query.filter_by(internship_id=s_h_id).first()
    #             education_field1 = EducationFieldDb.query.filter_by(internship_id=s_h_id).first()
    #         elif current_user.role == "Student":
    #             it_field1 = UItFieldDb.query.filter_by(student_id=s_h_id).first()
    #             education_field1 = UEducationFieldDb.query.filter_by(student_id=s_h_id).first()
    #         if it_field1:
    #             db.session.delete(it_field1)
    #         if education_field1:
    #             db.session.delete(education_field1)
    #
    #         db.session.commit()
    #         flash('Data have been saved')
    #         # print(Internship.query.filter_by(id=internship_id).all())
    #         if current_user.role == "Host":
    #             hostname = Internship.query.filter_by(id=s_h_id).first()
    #             hostname = str(hostname)
    #             # print(hostname)
    #             requirements = Internship.query.filter_by(hostname=hostname).all()
    #             return render_template('internship_requirement.html', requirements=requirements)
    #         elif current_user.role == "Student":
    #             return redirect(url_for('confirm_information'))
    #     elif form.back.data and form.validate_on_submit():
    #         if current_user.role == "Host":
    #             previous_req = Internship.query.filter_by(id=s_h_id).first()
    #             return redirect(url_for('save_host_req', intern_name=previous_req.internship_name))
    #         elif current_user.role == "Student":
    #             return redirect(url_for('edit_profile'))
    #
    #     elif request.method == "GET":
    #         engineer_field = None
    #         if current_user.role == "Host":
    #             engineer_field = EngineerFieldDb.query.filter_by(internship_id=s_h_id).first()
    #         elif current_user.role == "Student":
    #             engineer_field = UEngineerFieldDb.query.filter_by(student_id=s_h_id).first()
    #
    #         if engineer_field:
    #             form.years_of_work_experience.data = engineer_field.years_of_work_experience
    #             form.work_experience_flex.data = engineer_field.work_experience_flex
    #             form.knowledge_oil_gas.data = engineer_field.knowledge_oil_gas
    #             form.oil_gas_flex.data = engineer_field.oil_gas_flex
    #             form.oilfield_petrochemical_experience.data = engineer_field.oilfield_petrochemical_experience
    #             form.oilfield_petrochemical_flex.data = engineer_field.oilfield_petrochemical_flex
    #             form.communicating_interfacing_skills.data = engineer_field.communicating_interfacing_skills
    #             form.communicating_interfacing_flex.data = engineer_field.communicating_interfacing_flex
    #             form.knowledge_of_the_latest_telecommunications_technology.data = \
    #                 engineer_field.knowledge_of_the_latest_telecommunications_technology
    #             form.the_latest_telecommunications_technology_flex.data = \
    #                 engineer_field.the_latest_telecommunications_technology_flex
    #             form.familiar_with_industry_projects.data = engineer_field.familiar_with_industry_projects
    #             form.industry_projects_flex.data = engineer_field.industry_projects_flex
    #             form.engineering_design_experience.data = engineer_field.engineering_design_experience
    #             form.engineering_design_flex.data = engineer_field.engineering_design_flex
    #             form.knowledge_applicable_codes_standards.data = engineer_field.knowledge_applicable_codes_standards
    #             form.applicable_codes_standards_flex.data = engineer_field.applicable_codes_standards_flex
    #         if current_user.role == "Host":
    #             return render_template('host_it_field.html', form=form)
    #         elif current_user.role == "Student":
    #             return render_template('student_it_field.html', form=form)
    # elif category == 'Education field':
    #     form = EducationField()
    #     form.category_name.data = category
    #     if form.validate_on_submit() and form.submit.data:
    #         education_field = None
    #         if current_user.role == "Host":
    #             education_field = EducationFieldDb.query.filter_by(internship_id=s_h_id).first()
    #             print(education_field)
    #         elif current_user.role == "Student":
    #             education_field = UEducationFieldDb.query.filter_by(student_id=s_h_id).first()
    #         if education_field:
    #             print('there')
    #             if current_user.role == "Host":
    #                 education_field.internship_id = s_h_id
    #             elif current_user.role == "Student":
    #                 education_field.student_id = s_h_id
    #             education_field.character = form.character.data
    #             education_field.character_flex = form.character_flex.data
    #             education_field.interpersonal_skills = form.interpersonal_skills.data
    #             education_field.interpersonal_flex = form.interpersonal_flex.data
    #             education_field.time_management_skills = form.time_management_skills.data
    #             education_field.time_management_flex = form.time_management_flex.data
    #             education_field.teaching_qualification = form.teaching_qualification.data
    #             education_field.teaching_qualification_flex = form.teaching_qualification_flex.data
    #             education_field.years_experience = form.years_experience.data
    #             education_field.years_experience_flex = form.years_experience_flex.data
    #             education_field.language_requirement = form.language_requirement.data
    #             education_field.language_requirement_flex = form.language_requirement_flex.data
    #             education_field.teaching_field = form.teaching_field.data
    #             education_field.teaching_field_flex = form.teaching_field_flex.data
    #             education_field.monitor_experience = form.monitor_experience.data
    #             education_field.monitor_flex = form.monitor_flex.data
    #             education_field.assess_experience = form.assess_experience.data
    #             education_field.assess_flex = form.assess_flex.data
    #             education_field.teaching_strategies = form.teaching_strategies.data
    #             education_field.teaching_strategies_flex = form.teaching_strategies_flex.data
    #             education_field.literacy_numeracy_skills = form.literacy_numeracy_skills.data
    #             education_field.literacy_numeracy_flex = form.literacy_numeracy_flex.data
    #             education_field.address_adult_language = form.address_adult_language.data
    #             education_field.address_adult_language_flex = form.address_adult_language_flex.data
    #
    #         else:
    #             if current_user.role == "Host":
    #                 # print("there none")
    #                 education_field = EducationFieldDb()
    #                 education_field.internship_id = s_h_id
    #                 education_field.category_name = category
    #             elif current_user.role == "Student":
    #                 education_field = UEducationFieldDb()
    #                 education_field.student_id = s_h_id
    #                 education_field.category_name = category
    #             education_field.character = form.character.data
    #             education_field.character_flex = form.character_flex.data
    #             education_field.interpersonal_skills = form.interpersonal_skills.data
    #             education_field.interpersonal_flex = form.interpersonal_flex.data
    #             education_field.time_management_skills = form.time_management_skills.data
    #             education_field.time_management_flex = form.time_management_flex.data
    #             education_field.teaching_qualification = form.teaching_qualification.data
    #             education_field.teaching_qualification_flex = form.teaching_qualification_flex.data
    #             education_field.years_experience = form.years_experience.data
    #             education_field.years_experience_flex = form.years_experience_flex.data
    #             education_field.language_requirement = form.language_requirement.data
    #             education_field.language_requirement_flex = form.language_requirement_flex.data
    #             education_field.teaching_field = form.teaching_field.data
    #             education_field.teaching_field_flex = form.teaching_field_flex.data
    #             education_field.monitor_experience = form.monitor_experience.data
    #             education_field.monitor_flex = form.monitor_flex.data
    #             education_field.assess_experience = form.assess_experience.data
    #             education_field.assess_flex = form.assess_flex.data
    #             education_field.teaching_strategies = form.teaching_strategies.data
    #             education_field.teaching_strategies_flex = form.teaching_strategies_flex.data
    #             education_field.literacy_numeracy_skills = form.literacy_numeracy_skills.data
    #             education_field.literacy_numeracy_flex = form.literacy_numeracy_flex.data
    #             education_field.address_adult_language = form.address_adult_language.data
    #             education_field.address_adult_language_flex = form.address_adult_language_flex.data
    #             db.session.add(education_field)
    #         it_field1 = None
    #         engineer_field1 = None
    #         if current_user.role == "Host":
    #             it_field1 = ItFieldDb.query.filter_by(internship_id=s_h_id).first()
    #             engineer_field1 = EngineerFieldDb.query.filter_by(internship_id=s_h_id).first()
    #         elif current_user.role == "Student":
    #             it_field1 = UItFieldDb.query.filter_by(student_id=s_h_id).first()
    #             engineer_field1 = UEngineerFieldDb.query.filter_by(student_id=s_h_id).first()
    #         if it_field1:
    #             db.session.delete(it_field1)
    #         if engineer_field1:
    #             db.session.delete(engineer_field1)
    #         db.session.commit()
    #         flash('Data have been saved')
    #         # print(Internship.query.filter_by(id=internship_id).all())
    #         if current_user.role == "Host":
    #             hostname = Internship.query.filter_by(id=s_h_id).first()
    #             hostname = str(hostname)
    #             # print(hostname)
    #             requirements = Internship.query.filter_by(hostname=hostname).all()
    #             return render_template('internship_requirement.html', requirements=requirements)
    #         elif current_user.role == "Student":
    #             return redirect(url_for('confirm_information'))
    #     elif form.back.data and form.validate_on_submit():
    #         if current_user.role == "Host":
    #             previous_req = Internship.query.filter_by(id=s_h_id).first()
    #             return redirect(url_for('save_host_req', intern_name=previous_req.internship_name))
    #         elif current_user.role == "Student":
    #             return redirect(url_for('edit_profile'))
    #     elif request.method == "GET":
    #         education_field = None
    #         if current_user.role == "Host":
    #             education_field = EducationFieldDb.query.filter_by(internship_id=s_h_id).first()
    #         elif current_user.role == "Student":
    #             education_field = UEducationFieldDb.query.filter_by(student_id=s_h_id).first()
    #         if education_field:
    #             form.character.data = education_field.character
    #             form.character_flex.data = education_field.character_flex
    #             form.interpersonal_skills.data = education_field.interpersonal_skills
    #             form.interpersonal_flex.data = education_field.interpersonal_flex
    #             form.time_management_skills.data = education_field.time_management_skills
    #             form.time_management_flex.data = education_field.time_management_flex
    #             form.teaching_qualification.data = education_field.teaching_qualification
    #             form.teaching_qualification_flex.data = education_field.teaching_qualification_flex
    #             form.years_experience.data = education_field.years_experience
    #             form.years_experience_flex.data = education_field.years_experience_flex
    #             form.language_requirement.data = education_field.language_requirement
    #             form.language_requirement_flex.data = education_field.language_requirement_flex
    #             form.teaching_field.data = education_field.teaching_field
    #             form.teaching_field_flex.data = education_field.teaching_field_flex
    #             form.monitor_experience.data = education_field.monitor_experience
    #             form.monitor_flex.data = education_field.monitor_flex
    #             form.assess_experience.data = education_field.assess_experience
    #             form.assess_flex.data = education_field.assess_flex
    #             form.teaching_strategies.data = education_field.teaching_strategies
    #             form.teaching_strategies_flex.data = education_field.teaching_strategies_flex
    #             form.literacy_numeracy_skills.data = education_field.literacy_numeracy_skills
    #             form.literacy_numeracy_flex.data = education_field.literacy_numeracy_flex
    #             form.address_adult_language.data = education_field.address_adult_language
    #             form.address_adult_language_flex.data = education_field.address_adult_language_flex
    #         if current_user.role == "Host":
    #             return render_template('host_it_field.html', form=form)
    #         elif current_user.role == "Student":
    #             return render_template('student_it_field.html', form=form)


'''
@app.route('/invite/<req_id>',methods=['GET', 'POST'])
@login_required
def invite(req_id):
    host_req = 
'''


@app.route('/host_internship_category/<field>', methods=['GET', 'POST'])
def host_internship_category(field):
    internship_categories = InternshipCategory.query.filter_by(field_category=field).all()
    internshipArray = []
    for category in internship_categories:
        internshipObj = {}
        internshipObj['id'] = category.id
        internshipObj['name'] = category.name
        internshipArray.append(internshipObj)
    return jsonify({'internship_categories': internshipArray})


@app.route('/nation_state/<nation>', methods=['GET', 'POST'])
def nation_state(nation):
    states = State.query.filter_by(nation=nation).all()
    statesArray = []
    for state in states:
        stateObj = {}
        stateObj['id'] = state.id
        stateObj['name'] = state.name
        statesArray.append(stateObj)
    return jsonify({'states': statesArray})


@app.route('/state_city/<state>', methods=['GET', 'POST'])
def state_city(state):
    cities = City.query.filter_by(state=state).all()
    citiesArray = []
    for city in cities:
        cityObj = {}
        cityObj['id'] = city.id
        cityObj['name'] = city.name
        citiesArray.append(cityObj)
    return jsonify({'cities': citiesArray})
