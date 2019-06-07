'''
This file contains all models in this system, and the tables in the database are created according to this file.

In "routes.py" file, any record in the database can be searched according to these attributed defined in these models.

Users filling the information should obey the constrains defined in each model.
'''
from datetime import datetime
from hashlib import md5
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import app, db, login


# The user class and it is indispensable in the model.
# Students and hosts are included in the user model,and they are distinguished by their roles.
# The User class inherits the UserMixin class and the instance of the User class has three attributes and one function.
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(140))
    role = db.Column(db.String, default='Host', nullable=False)

    def __repr__(self):
        return '<Use r {}>'.format(self.username)

    # The property of User
    @property
    # Get the user's role.
    def get_role(self):
        return self.role

    # Judge if the user is an administrator.
    def is_administrator(self):
        return self.role == 'Administrator'

    # When users register the system, set the password by hash transformation.
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check the hashed string, and if it is the same with correct hash values, then it returns "True".
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Generate an avatar.
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    # Get the reset password token.
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    # Query the user's identity.
    def query_user_identity(self):
        obj = User.query.filter_by(role=self.role).first()
        return obj.role

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


# This function must be used when using "LoginManager" handle the login function.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# It is the host model containing host's basic attributes.
class Host(db.Model):
    __tablename__ = 'host'
    # The foreign key in this model and it cascades with 'user.username'.
    hostname = db.Column(db.String(120), db.ForeignKey('user.username'), unique=True)
    description = db.Column(db.String(400))
    nation = db.Column(db.String(120))
    state = db.Column(db.String(120))
    city = db.Column(db.String(120))
    address = db.Column(db.String(200), nullable=True)
    # The primary kay in this model.
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    email = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return (self.city)


# It is the state model containing state's basic attributes.
# The 'state' table is a static table in the database.
class State(db.Model):
    __tablename__ = 'state'
    id = db.Column(db.Integer, primary_key=True)
    nation = db.Column(db.String(120), nullable=True)
    name = db.Column(db.String(120), nullable=True)


# It is the city model containing state's basic attributes.
# The 'city' table is a static table in the database.
class City(db.Model):
    __tablename__ = 'city1'
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(120), nullable=True)
    name = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return (self.name)


# It is the student model, and it contains student's basic information.
class Student(db.Model):
    __tablename__ = 'student'
    # The primary key
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    nation = db.Column(db.String(120))
    state = db.Column(db.String(120))
    city = db.Column(db.String(120))
    address = db.Column(db.String(200))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(120))
    major = db.Column(db.String(120))
    education_level = db.Column(db.String(120))
    email = db.Column(db.String(120), nullable=False)
    visa = db.Column(db.String(120))
    disability = db.Column(db.Boolean, default=False)
    field_category = db.Column(db.String(120))
    internship_category = db.Column(db.String(120))
    language = db.Column(db.String(120))
    work_experience = db.Column(db.Boolean, default=False)
    work_experience_describe = db.Column(db.Text(400))


# It is the internship model, and it contains internship's basic information.
class Internship(db.Model):
    __tablename__ = 'internship'
    # The primary key
    id = db.Column(db.Integer, primary_key=True)
    # The foreign key and it cascades with "host.hostname".
    hostname = db.Column(db.String(120), db.ForeignKey('host.hostname'))
    field_category = db.Column(db.String(120))
    internship_name = db.Column(db.String(120), unique=True)
    age = db.Column(db.Integer)
    age_flex = db.Column(db.Boolean, default=False)
    gender_requirement = db.Column(db.String(120))
    gender_flex = db.Column(db.Boolean, default=False)
    major = db.Column(db.String(120))
    major_flex = db.Column(db.Boolean, default=False)
    education_requirement = db.Column(db.String(120))
    education_flex = db.Column(db.Boolean, default=False)
    internship_category = db.Column(db.String(120))
    salary = db.Column(db.Integer)
    salary_flex = db.Column(db.Boolean, default=False)
    visa = db.Column(db.String(120))
    visa_flex = db.Column(db.Boolean, default=False)
    workplace_nation = db.Column(db.String(120))
    nation_flex = db.Column(db.Boolean, default=False)
    workplace_state = db.Column(db.String(120))
    state_flex = db.Column(db.Boolean, default=False)
    workplace_city = db.Column(db.String(120))
    city_flex = db.Column(db.Boolean, default=False)
    workdays = db.Column(db.String(120))
    workdays_flex = db.Column(db.Boolean, default=False)
    opportunity_to_fulltime_job = db.Column(db.Boolean, default=False)
    fulltime_flex = db.Column(db.Boolean, default=False)
    language_requirement = db.Column(db.String(120))
    language_flex = db.Column(db.Boolean, default=False)
    disability = db.Column(db.Boolean, default=False)
    disability_flex = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.hostname


# The model serves the matching result.
# The match model contains the most representative fields between students and hosts.
# These fields in the model can pinpoint an accurate student or host.
class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)
    stu_username = db.Column(db.String(120), db.ForeignKey('student.username'))
    hostname = db.Column(db.String(120), db.ForeignKey('host.hostname'))
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'))
    internship_name = db.Column(db.String(120))
    match_rate = db.Column(db.FLOAT)


# The application model is used when students get their results and they can apply some suitable internships.
# These fields in the model can pinpoint an accurate student or host.
class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    stu_username = db.Column(db.String(120), db.ForeignKey('student.username'))
    hostname = db.Column(db.String(120), db.ForeignKey('host.hostname'))
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'))
    internship_name = db.Column(db.String(120))
    match_rate = db.Column(db.FLOAT)


# The application model is used when hosts get their matching results and they can invite some suitable students.
# These fields in the model can pinpoint an accurate student or host.
class Invitation(db.Model):
    __tablename__ = 'invitation'
    id = db.Column(db.Integer, primary_key=True)
    stu_username = db.Column(db.String(120), db.ForeignKey('student.username'))
    hostname = db.Column(db.String(120), db.ForeignKey('host.hostname'))
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'))
    internship_name = db.Column(db.String(120))
    match_rate = db.Column(db.FLOAT)


# This model provides fields of student requirements for the internship.
class URequirement(db.Model):
    __tablename__ = 'userrequirement'
    # The primary key
    id = db.Column(db.Integer, primary_key=True)
    # The foreign key
    username = db.Column(db.String(120), db.ForeignKey('student.username'))
    education_requirement = db.Column(db.String(120))
    education_flex = db.Column(db.Boolean, default=False)
    salary = db.Column(db.Integer)
    salary_flex = db.Column(db.Boolean, default=False)
    workplace_nation = db.Column(db.String(120))
    nation_flex = db.Column(db.Boolean, default=False)
    workplace_state = db.Column(db.String(120))
    state_flex = db.Column(db.Boolean, default=False)
    workplace_city = db.Column(db.String(120))
    city_flex = db.Column(db.Boolean, default=False)
    workdays_requirement = db.Column(db.String(120))
    workdays_flex = db.Column(db.Boolean, default=False)
    opportunity_to_fulltime_job = db.Column(db.Boolean, default=False)
    fulltime_flex = db.Column(db.Boolean, default=False)
    language_requirement = db.Column(db.String(120))
    language_flex = db.Column(db.Boolean, default=False)
    desired_position = db.Column(db.String(120))
    desired_position_flex = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.username


# This model is used to show what internship categories is in the field category
# This is a static model, the data will be filled into the database in advance
class InternshipCategory(db.Model):
    __tablename__ = 'internship_category'
    id = db.Column(db.Integer, primary_key=True)
    field_category = db.Column(db.String(120))
    name = db.Column(db.String(120))

    def __repr__(self):
        return (self.name)


# This model is used to show what jobs in a internship category
# This is a static model, the data will be filled into the database in advance
class UInternshipPosition(db.Model):
    __tablename__ = 'u_internship_position'
    id = db.Column(db.Integer, primary_key=True)
    internship_category = db.Column(db.String(120), db.ForeignKey('internship_category.name'))
    internship_position = db.Column(db.String(120))


# This model is used by hosts and stores the requirements of each IT internship.
class ItFieldDb(db.Model):
    __tablename__ = 'host_it_field'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(120))
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), unique=True)
    java_level = db.Column(db.String(120))
    java_flex = db.Column(db.Boolean, default=False)
    r_level = db.Column(db.String(120))
    r_flex = db.Column(db.Boolean, default=False)
    python_level = db.Column(db.String(120))
    python_flex = db.Column(db.Boolean, default=False)
    cplusplus_level = db.Column(db.String(120))
    cplusplus_flex = db.Column(db.Boolean, default=False)
    php_level = db.Column(db.String(120))
    php_flex = db.Column(db.Boolean, default=False)
    backend_level = db.Column(db.String(120))
    backend_flex = db.Column(db.Boolean, default=False)
    frontend_level = db.Column(db.String(120))
    frontend_flex = db.Column(db.Boolean, default=False)
    android_ios_level = db.Column(db.String(120))
    android_ios_flex = db.Column(db.Boolean, default=False)
    docker_level = db.Column(db.String(120))
    docker_flex = db.Column(db.Boolean, default=False)
    cloud_level = db.Column(db.String(120))
    cloud_flex = db.Column(db.Boolean, default=False)
    linux_level = db.Column(db.String(120))
    linux_flex = db.Column(db.Boolean, default=False)
    database_level = db.Column(db.String(120))
    database_flex = db.Column(db.Boolean, default=False)
    machine_learning_level = db.Column(db.String(120))
    machine_learning_flex = db.Column(db.Boolean, default=False)
    statistics_level = db.Column(db.String(120))
    statistics_flex = db.Column(db.Boolean, default=False)


'''

# This model is used by hosts and stores the requirements of each education internship.
# This model is not used in current system, but may be used in the future.
class EducationFieldDb(db.Model):
    __tablename__ = 'host_education_field'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(120))
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), unique=True)
    interpersonal_skills = db.Column(db.String(120))
    interpersonal_flex = db.Column(db.Boolean, default=False)
    time_management_skills = db.Column(db.String(120))
    time_management_flex = db.Column(db.Boolean, default=False)
    teaching_qualification = db.Column(db.String(120))
    teaching_qualification_flex = db.Column(db.Boolean, default=False)
    years_experience = db.Column(db.String(120))
    years_experience_flex = db.Column(db.Boolean, default=False)
    language_requirement = db.Column(db.String(120))
    language_requirement_flex = db.Column(db.Boolean, default=False)
    teaching_field = db.Column(db.String(120))
    teaching_field_flex = db.Column(db.Boolean, default=False)
    character = db.Column(db.String(120))
    character_flex = db.Column(db.Boolean, default=False)
    monitor_experience = db.Column(db.String(120))
    monitor_flex = db.Column(db.Boolean, default=False)
    assess_experience = db.Column(db.String(120))
    assess_flex = db.Column(db.Boolean, default=False)
    teaching_strategies = db.Column(db.String(120))
    teaching_strategies_flex = db.Column(db.Boolean, default=False)
    literacy_numeracy_skills = db.Column(db.String(120))
    literacy_numeracy_flex = db.Column(db.Boolean, default=False)
    address_adult_language = db.Column(db.String(120))
    address_adult_language_flex = db.Column(db.Boolean, default=False)


# This model is used by hosts and stores the requirements of each education engineer internship.
# This model is not used in current system, but may be used in the future.
class EngineerFieldDb(db.Model):
    __tablename__ = 'host_engineer_field'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(120))
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), unique=True)
    years_of_work_experience = db.Column(db.String(120))
    work_experience_flex = db.Column(db.Boolean, default=False)
    knowledge_oil_gas = db.Column(db.String(120))
    oil_gas_flex = db.Column(db.Boolean, default=False)
    oilfield_petrochemical_experience = db.Column(db.String(120))
    oilfield_petrochemical_flex = db.Column(db.Boolean, default=False)
    communicating_interfacing_skills = db.Column(db.String(120))
    communicating_interfacing_flex = db.Column(db.Boolean, default=False)
    knowledge_of_the_latest_telecommunications_technology = db.Column(db.String(120))
    the_latest_telecommunications_technology_flex = db.Column(db.Boolean, default=False)
    familiar_with_industry_projects = db.Column(db.String(120))
    industry_projects_flex = db.Column(db.Boolean, default=False)
    engineering_design_experience = db.Column(db.String(120))
    engineering_design_flex = db.Column(db.Boolean, default=False)
    knowledge_applicable_codes_standards = db.Column(db.String(120))
    applicable_codes_standards_flex = db.Column(db.Boolean, default=False)

'''


# This model is used by students and stores the requirements of each IT internship.
class UItFieldDb(db.Model):
    __tablename__ = 'student_it_field'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), unique=True)
    category_name = db.Column(db.String(120))
    java_level = db.Column(db.String(120))
    java_flex = db.Column(db.Boolean, default=False)
    r_level = db.Column(db.String(120))
    r_flex = db.Column(db.Boolean, default=False)
    python_level = db.Column(db.String(120))
    python_flex = db.Column(db.Boolean, default=False)
    cplusplus_level = db.Column(db.String(120))
    cplusplus_flex = db.Column(db.Boolean, default=False)
    php_level = db.Column(db.String(120))
    php_flex = db.Column(db.Boolean, default=False)
    backend_level = db.Column(db.String(120))
    backend_flex = db.Column(db.Boolean, default=False)
    frontend_level = db.Column(db.String(120))
    frontend_flex = db.Column(db.Boolean, default=False)
    android_ios_level = db.Column(db.String(120))
    android_ios_flex = db.Column(db.Boolean, default=False)
    docker_level = db.Column(db.String(120))
    docker_flex = db.Column(db.Boolean, default=False)
    cloud_level = db.Column(db.String(120))
    cloud_flex = db.Column(db.Boolean, default=False)
    linux_level = db.Column(db.String(120))
    linux_flex = db.Column(db.Boolean, default=False)
    database_level = db.Column(db.String(120))
    database_flex = db.Column(db.Boolean, default=False)
    machine_learning_level = db.Column(db.String(120))
    machine_learning_flex = db.Column(db.Boolean, default=False)
    statistics_level = db.Column(db.String(120))
    statistics_flex = db.Column(db.Boolean, default=False)


'''
# This model is used by students and stores the requirements of each education internship.
# This model is not used in current system, but may be used in the future.
class UEducationFieldDb(db.Model):
    __tablename__ = 'student_education_field'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), unique=True)
    category_name = db.Column(db.String(120))
    interpersonal_skills = db.Column(db.String(120))
    interpersonal_flex = db.Column(db.Boolean, default=False)
    time_management_skills = db.Column(db.String(120))
    time_management_flex = db.Column(db.Boolean, default=False)
    teaching_qualification = db.Column(db.String(120))
    teaching_qualification_flex = db.Column(db.Boolean, default=False)
    years_experience = db.Column(db.String(120))
    years_experience_flex = db.Column(db.Boolean, default=False)
    language_requirement = db.Column(db.String(120))
    language_requirement_flex = db.Column(db.Boolean, default=False)
    teaching_field = db.Column(db.String(120))
    teaching_field_flex = db.Column(db.Boolean, default=False)
    character = db.Column(db.String(120))
    character_flex = db.Column(db.Boolean, default=False)
    monitor_experience = db.Column(db.String(120))
    monitor_flex = db.Column(db.Boolean, default=False)
    assess_experience = db.Column(db.String(120))
    assess_flex = db.Column(db.Boolean, default=False)
    teaching_strategies = db.Column(db.String(120))
    teaching_strategies_flex = db.Column(db.Boolean, default=False)
    literacy_numeracy_skills = db.Column(db.String(120))
    literacy_numeracy_flex = db.Column(db.Boolean, default=False)
    address_adult_language = db.Column(db.String(120))
    address_adult_language_flex = db.Column(db.Boolean, default=False)


# This model is used by students and stores the requirements of each engineer internship.
# This model is not used in current system, but may be used in the future.
class UEngineerFieldDb(db.Model):
    __tablename__ = 'student_engineer_field'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), unique=True)
    category_name = db.Column(db.String(120))
    years_of_work_experience = db.Column(db.String(120))
    work_experience_flex = db.Column(db.Boolean, default=False)
    knowledge_oil_gas = db.Column(db.String(120))
    oil_gas_flex = db.Column(db.Boolean, default=False)
    oilfield_petrochemical_experience = db.Column(db.String(120))
    oilfield_petrochemical_flex = db.Column(db.Boolean, default=False)
    communicating_interfacing_skills = db.Column(db.String(120))
    communicating_interfacing_flex = db.Column(db.Boolean, default=False)
    knowledge_of_the_latest_telecommunications_technology = db.Column(db.String(120))
    the_latest_telecommunications_technology_flex = db.Column(db.Boolean, default=False)
    familiar_with_industry_projects = db.Column(db.String(120))
    industry_projects_flex = db.Column(db.Boolean, default=False)
    engineering_design_experience = db.Column(db.String(120))
    engineering_design_flex = db.Column(db.Boolean, default=False)
    knowledge_applicable_codes_standards = db.Column(db.String(120))
    applicable_codes_standards_flex = db.Column(db.Boolean, default=False)
'''
