'''
This file contains all forms in this system. Users can fill their information through these forms.

In each form, there are many fields according different scenarios.

In "routes.py", each form in this file will be created and users can provide their information.
'''
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, IntegerField, DecimalField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length, NumberRange
from app.models import User, Host, Internship, InternshipCategory


# This class is used when users login the system.
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# This class is used when users register the system.
class RegistrationForm(FlaskForm):
    def email_unique(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Do not use other email?')

    def password_noblank(self, field):
        for s in field.data:
            if s == ' ':
                raise ValidationError('Do not use whitespace!')

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), email_unique])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(6, message='The password is too short'), password_noblank])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired('Please confirm your password!'), EqualTo('password')])
    role = RadioField('Identity', choices=[('Student', 'Student'), ('Host', 'Host')], default='Student')

    submit = SubmitField('Register')

    # Make sure the user enters a username that is not in the database.
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    # Make sure the user enters a email that is not in the database
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


# This class is used when students edit their self information.
# These fields are the basic information describing the students.
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    gender = SelectField('Gender', validators=[DataRequired()],
                         choices=[('male', 'male'), ('female', 'female'),
                                  ('Not to choose', 'Not to choose')])
    age = IntegerField('Age', validators=[NumberRange(min=1, max=100)])
    email = StringField('Email', validators=[DataRequired()])
    nation = SelectField('Nation Name', validators=[DataRequired()],
                         choices=[('Australia', 'Australia'),
                                  ('America', 'America'),
                                  ('China', 'China'),
                                  ('Japan', 'Japan'),
                                  ('Germany', 'Germany'),
                                  ('Korea', "Korea"),
                                  ('Russia', 'Russia'),
                                  ('New Zealand', 'New Zealand'),
                                  ('Canada', 'Canada')], default='Australia')
    state = SelectField('State Name', validators=[DataRequired()], choices=[], default='New South Wales')
    city = SelectField('City Name', validators=[DataRequired()], choices=[])

    address = TextAreaField('Detailed Address', validators=[Length(min=0, max=200), DataRequired()])
    field_category = SelectField('Select the Field Category', validators=[DataRequired()],
                                 choices=[('IT field', 'IT field'), ('Engineer field', 'Engineer field'),
                                          ('Medicine field', 'Medicine field'), ('Education field', 'Education field')],
                                 default='IT field')
    internship_category = SelectField('Select the Internship Category Requirement', validators=[DataRequired()],
                                      choices=[])
    education_level = SelectField('Education', validators=[DataRequired('Select a choice')],
                                  choices=[('highschool', 'highschool'), ('undergraduate', 'undergraduate'),
                                           ('postgraduate', 'postgraduate'),
                                           ('doctor', 'doctor')]
                                  )
    major = SelectField('Major', validators=[DataRequired()],
                        choices=[('Computer Science', 'Computer Science'), ('Art', 'Art'), ('Education', 'Education'),
                                 ('Eletric', 'Eletric'), ('Medicine', 'Medicine')]
                        )
    visa = SelectField('Visa Type', validators=[DataRequired()],
                       choices=[('Student visa((subclass 500))', 'Student visa((subclass 500))'),
                                ('Visitor visa(subclass 600)', 'Visitor visa (subclass 600)'),
                                ('Work and Holiday visa(subclass 462)', 'Work and Holiday visa (subclass 462)'),
                                ('Skilled Independent visa(subclass 189) ', 'Skilled Independent visa (subclass 189)'),
                                ('Skilled Nominated visa(subclass 190)', 'Skilled Nominated visa (subclass 190)'),
                                ('Skilled Regional (provisional) visa(subclass 489)',
                                 'Skilled Regional (provisional) visa(subclass 489)'),
                                ('Temporary Graduate visa(subclass 485)', 'Temporary Graduate visa (subclass 485)'),
                                ('Employer Nomination Scheme visa(subclass 186)',
                                 'Employer Nomination Scheme visa(subclass 186)'),
                                ('Business Innovation and Investment (provisional／permanent) visa(subclass 188／888)',
                                 'Business Innovation and Investment (provisional／permanent) visa (subclass 188／888)'),
                                (
                                    'Partner (Provisional and Migration) visa(offshore subclass 309/100)(onshore subclass 820/801)',
                                    'Partner (Provisional and Migration) visa(offshore subclass 309/100)(onshore subclass 820/801)'),
                                ('Citizen', 'Citizen'),
                                ('Permanent Resident', 'Permanent Resident')])
    disability = BooleanField('Disability', default=False)

    language = SelectField('Select your preferred language', validators=[DataRequired()],
                           choices=[('English', 'English'), ('French', 'French'), ('Spanish', 'Spanish'),
                                    ('Arabic', 'Arabic'), ('Mandarin', 'Mandarin'), ('Russian', 'Russian'),
                                    ('Portuguese', 'Portuguese'), ('German', 'German'), ('Japanese', 'Japanese'),
                                    ('Hindustani ', 'Hindustani'), ('Malay', 'Malay'), ('Italian', 'Italian'),
                                    ('Dutch', 'Dutch'), ('Vietnamese', 'Vietnamese'), ('Polish', 'Polish'),
                                    ('Thai Language', 'Thai Language'), ('Korean', 'Korean')])

    work_experience = BooleanField('Work Experience? '
                                   '(If you don not have, please ignore the following textbox)',
                                   default=False)
    work_experience_describe = TextAreaField('Please input your detailed work experience.')
    next = SubmitField('Next Page')
    upload_file = SubmitField('Upload Your CV')

    # Initialize the user name
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    # Determine if it is a reasonable user name
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


# This class is used when hosts edit their self information.
# The dynamic cascade selection is used here.
class HostInformation(FlaskForm):
    hostname = StringField('Host Name', validators=[DataRequired()])
    description = TextAreaField('Host Description',
                                validators=[DataRequired('Please input description about your company')])
    nation = SelectField('Nation Name', validators=[DataRequired()],
                         choices=[('Australia', 'Australia'),
                                  ('America', 'America'),
                                  ('China', 'China'),
                                  ('Japan', 'Japan'),
                                  ('Germany', 'Germany'),
                                  ('Korea', "Korea"),
                                  ('Russia', 'Russia'),
                                  ('New Zealand', 'New Zealand'),
                                  ('Canada', 'Canada')], default='Australia')
    state = SelectField('State Name', validators=[DataRequired()], choices=[], default='New South Wales')
    city = SelectField('City Name', validators=[DataRequired()], choices=[])
    address = StringField('Detailed Host address', validators=[DataRequired()])
    save = SubmitField('Save')
    back = SubmitField("Back")

    # Initialize the user name
    def __init__(self, original_hostname, *args, **kwargs):
        super(HostInformation, self).__init__(*args, **kwargs)
        self.original_hostname = original_hostname

    # Determine if it is a reasonable hostname
    def validate_username(self, hostname):
        if hostname.data != self.original_hostname:
            host = Host.query.filter_by(hostname=self.hostname.data).first()
            if host is not None:
                raise ValidationError('Please use a different hostname.')


# This class describes students' requirements to internships.
class UserRequirement(FlaskForm):
    username = StringField('User Name', validators=[DataRequired()])
    desired_position = SelectField('Select Your Desired Position', validators=[DataRequired()],
                                   choices=[])
    desired_position_flex = BooleanField('Inflexible', default=False)
    education_requirement = SelectField('Education Requirement', validators=[DataRequired()],
                                        choices=[('highschool', 'highschool'),
                                                 ('undergraduate', 'undergraduate'),
                                                 ('postgraduate', 'postgraduate'),
                                                 ('doctor', 'doctor')])
    education_flex = BooleanField('Inflexible', default=False)
    salary = IntegerField('Salary(Au$, per week, lower bound)', validators=[NumberRange(min=0, max=1000000)])
    salary_flex = BooleanField('Inflexible', default=False)
    workplace_nation = SelectField('Nation Name of Workplace', validators=[DataRequired()],
                                   choices=[('Australia', 'Australia'),
                                            ('America', 'America'),
                                            ('China', 'China'),
                                            ('Japan', 'Japan'),
                                            ('Germany', 'Germany'),
                                            ('Korea', "Korea"),
                                            ('Russia', 'Russia'),
                                            ('New Zealand', 'New Zealand'),
                                            ('Canada', 'Canada')], default='Australia')
    nation_flex = BooleanField('Inflexible', default=False)
    workplace_state = SelectField('State Name of Workplace', validators=[DataRequired()], choices=[],
                                  default='New South Wales')
    state_flex = BooleanField('Inflexible', default=False)
    workplace_city = SelectField('City Name of Workplace', validators=[DataRequired()], choices=[])
    city_flex = BooleanField('Inflexible', default=False)
    # The front end displays strings and the database stores numbers for better matches.
    workdays_requirement = SelectField('Workdays(per week, upper bound) ', validators=[DataRequired()],
                                       choices=[('1', 'One Day'),
                                                ('2', 'Two Days'),
                                                ('3', 'Three Days'),
                                                ('4', 'Four Days'),
                                                ('5', 'Five Days'),
                                                ('6', 'Six Days'),
                                                ('7', 'Seven Days')])
    workdays_flex = BooleanField('Inflexible', default=False)
    opportunity_to_fulltime_job = BooleanField('Offer Opportunities to Become a Full-time Job ',
                                               default=False)
    fulltime_flex = BooleanField('Inflexible', default=False)
    language_requirement = SelectField('Preferred Language', validators=[DataRequired()],
                                       choices=[('English', 'English'), ('French', 'French'), ('Spanish', 'Spanish'),
                                                ('Arabic', 'Arabic'), ('Mandarin', 'Mandarin'), ('Russian', 'Russian'),
                                                ('Portuguese', 'Portuguese'), ('German', 'German'),
                                                ('Japanese', 'Japanese'),
                                                ('Hindustani ', 'Hindustani'), ('Malay', 'Malay'),
                                                ('Italian', 'Italian'),
                                                ('Dutch', 'Dutch'), ('Vietnamese', 'Vietnamese'), ('Polish', 'Polish'),
                                                ('Thai Language', 'Thai Language'), ('Korean', 'Korean')])
    language_flex = BooleanField('Inflexible', default=False)
    submit = SubmitField('submit')

    # initialize students' username
    def __init__(self, original_username, *args, **kwargs):
        super(UserRequirement, self).__init__(*args, **kwargs)
        self.original_username = original_username

    # using a valid username
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


# This class describes hosts' requirements to students.
class HostRequirement(FlaskForm):
    hostname = StringField('Host Name', validators=[DataRequired()])
    internship_name = StringField('Internship Name', validators=[DataRequired()])
    field_category = SelectField('Field Category Requirement', validators=[DataRequired()],
                                 choices=[('IT field', 'IT field'), ('Engineer field', 'Engineer field'),
                                          ('Medicine field', 'Medicine field'), ('Education field', 'Education field')],
                                 default='IT field')
    internship_category = SelectField('Internship Category Requirement', validators=[DataRequired()],
                                      choices=[])
    age = IntegerField('Age Requirement', validators=[DataRequired()])
    age_flex = BooleanField('Inflexible', default=False)

    education_requirement = SelectField('Education Requirement', validators=[DataRequired()],
                                        choices=[('highschool', 'highschool'),
                                                 ('undergraduate', 'undergraduate'),
                                                 ('postgraduate', 'postgraduate'),
                                                 ('doctor', 'doctor')])
    education_flex = BooleanField('Inflexible', default=False)
    gender_requirement = SelectField('Gender Requirement', validators=[DataRequired()]
                                     , choices=[('male', 'male'), ('female', 'female'), ('unlimited', 'unlimited')]
                                     )
    gender_flex = BooleanField('Inflexible', default=False)
    major = SelectField('Major Requirement', validators=[DataRequired()],
                        choices=[('Computer Science', 'Computer Science'), ('Electric', 'Electric'),
                                 ('Medicine', 'Medicine'), ('Education', 'Education')]
                        )
    major_flex = BooleanField('Inflexible', default=False)
    salary = IntegerField('Salary(Au$,per week,upper bound)', validators=[NumberRange(min=0, max=1000000)])
    salary_flex = BooleanField('Inflexible', default=False)
    visa = SelectField('Visa Type', validators=[DataRequired()],
                       choices=[('Student visa((subclass 500))',
                                 'Student visa((subclass 500))'),
                                ('Visitor visa(subclass 600)',
                                 'Visitor visa (subclass 600)'),
                                ('Work and Holiday visa(subclass 462)',
                                 'Work and Holiday visa (subclass 462)'),
                                ('Skilled Independent visa(subclass 189) ',
                                 'Skilled Independent visa (subclass 189)'),
                                ('Skilled Nominated visa(subclass 190)',
                                 'Skilled Nominated visa (subclass 190)'),
                                (
                                    'Skilled Regional (provisional) visa(subclass 489)',
                                    'Skilled Regional (provisional) visa(subclass 489)'),
                                ('Temporary Graduate visa(subclass 485)',
                                 'Temporary Graduate visa (subclass 485)'),
                                (
                                    'Employer Nomination Scheme visa(subclass 186)',
                                    'Employer Nomination Scheme visa(subclass 186)'),
                                (
                                    'Business Innovation and Investment (provisional／permanent) visa(subclass 188／888)',
                                    'Business Innovation and Investment (provisional／permanent) visa (subclass 188／888)'),
                                (
                                    'Partner (Provisional and Migration) visa(offshore subclass 309/100)(onshore subclass 820/801)',
                                    'Partner (Provisional and Migration) visa(offshore subclass 309/100)(onshore subclass 820/801)'),
                                ('Citizen', 'Citizen'),
                                ('Permanent Resident', 'Permanent Resident')])
    visa_flex = BooleanField('Inflexible', default=False)
    workplace_nation = SelectField('Nation Name of Workplace',
                                   validators=[DataRequired()],
                                   choices=[('Australia', 'Australia'),
                                            ('America', 'America'),
                                            ('China', 'China'),
                                            ('Japan', 'Japan'),
                                            ('Germany', 'Germany'),
                                            ('Korea', "Korea"),
                                            ('Russia', 'Russia'),
                                            ('New Zealand', 'New Zealand'),
                                            ('Canada', 'Canada')], default='Australia')
    nation_flex = BooleanField('Inflexible', default=False)
    workplace_state = SelectField('State Name of Workplace',
                                  validators=[DataRequired()], choices=[], default='New South Wales')
    state_flex = BooleanField('Inflexible', default=False)
    workplace_city = SelectField('City Name of Workplace',
                                 validators=[DataRequired()], choices=[])
    city_flex = BooleanField('Inflexible', default=False)
    # The front end displays strings and the database stores numbers for better matches.
    workdays = SelectField('Workdays (per week, lower bound)',
                           validators=[DataRequired()],
                           choices=[('1', 'One Day'),
                                    ('2', 'Two Days'),
                                    ('3', 'Three Days'),
                                    ('4', 'Four Days'),
                                    ('5', 'Five Days'),
                                    ('6', 'Six Days'),
                                    ('7', 'Seven Days')])
    workdays_flex = BooleanField('Inflexible', default=False)
    opportunity_to_fulltime_job = BooleanField('Offer opportunities to become a full-time job ',
                                               default=False)

    fulltime_flex = BooleanField('Inflexible', default=False)
    language_requirement = SelectField('Preferred Language',
                                       validators=[DataRequired()],
                                       choices=[('English', 'English'),
                                                ('French', 'French'),
                                                ('Spanish', 'Spanish'),
                                                ('Arabic', 'Arabic'),
                                                ('Mandarin', 'Mandarin'),
                                                ('Russian', 'Russian'),
                                                ('Portuguese', 'Portuguese'),
                                                ('German', 'German'),
                                                ('Japanese', 'Japanese'),
                                                ('Hindustani ', 'Hindustani'),
                                                ('Malay', 'Malay'),
                                                ('Italian', 'Italian'),
                                                ('Dutch', 'Dutch'),
                                                ('Vietnamese', 'Vietnamese'),
                                                ('Polish', 'Polish'),
                                                ('Thai Language',
                                                 'Thai Language'),
                                                ('Korean', 'Korean')])
    language_flex = BooleanField('Inflexible', default=False)
    disability = BooleanField('Priority for Disability', default=False)
    disability_flex = BooleanField('Inflexible', default=False)
    next = SubmitField('Next Page')

    # initialize the username
    def __init__(self, original_hostname, *args, **kwargs):
        super(HostRequirement, self).__init__(*args, **kwargs)
        self.original_hostname = original_hostname

    # using a valid username
    def validate_username(self, hostname):
        if hostname.data != self.original_hostname:
            host = Host.query.filter_by(hostname=self.hostname.data).first()
            if host is not None:
                raise ValidationError('Please use a different hostname.')


# This class contains academic skills of IT,which is used for students and hosts.
class ITField(FlaskForm):
    category_name = StringField('Internship Field', validators=[DataRequired()], id='contentcode')
    # The front end displays strings and the database stores numbers for better matches.
    # The following codes are similar.
    java_level = SelectField('Please select Java level', validators=[DataRequired()],
                             choices=[('1', 'Novice Level'),
                                      ('2', 'General Level'),
                                      ('3', 'Proficient Level'),
                                      ('4', 'Expert Level')])
    java_flex = BooleanField('Inflexible', default=False)

    python_level = SelectField('Please select Python level', validators=[DataRequired()],
                               choices=[('1', 'Novice Level'),
                                        ('2', 'General Level'),
                                        ('3', 'Proficient Level'),
                                        ('4', 'Expert Level')])
    python_flex = BooleanField('Inflexible', default=False)

    r_level = SelectField('Please select R level', validators=[DataRequired()],
                          choices=[('1', 'Novice Level'),
                                   ('2', 'General Level'),
                                   ('3', 'Proficient Level'),
                                   ('4', 'Expert Level')])
    r_flex = BooleanField('Inflexible', default=False)

    cplusplus_level = SelectField('Please select C++ level', validators=[DataRequired()],
                                  choices=[('1', 'Novice Level'),
                                           ('2', 'General Level'),
                                           ('3', 'Proficient Level'),
                                           ('4', 'Expert Level')])
    cplusplus_flex = BooleanField('Inflexible', default=False)

    php_level = SelectField('Please select PHP level', validators=[DataRequired()],
                            choices=[('1', 'Novice Level'),
                                     ('2', 'General Level'),
                                     ('3', 'Proficient Level'),
                                     ('4', 'Expert Level')])
    php_flex = BooleanField('Inflexible', default=False)

    backend_level = SelectField('Please select Backend level', validators=[DataRequired()],
                                choices=[('1', 'Novice Level'),
                                         ('2', 'General Level'),
                                         ('3', 'Proficient Level'),
                                         ('4', 'Expert Level')])

    backend_flex = BooleanField('Inflexible', default=False)

    frontend_level = SelectField('Please select Frontend level', validators=[DataRequired()],
                                 choices=[('1', 'Novice Level'),
                                          ('2', 'General Level'),
                                          ('3', 'Proficient Level'),
                                          ('4', 'Expert Level')])
    frontend_flex = BooleanField('Inflexible', default=False)

    android_ios_level = SelectField('Please select Android/IOS level', validators=[DataRequired()],
                                    choices=[('1', 'Novice Level'),
                                             ('2', 'General Level'),
                                             ('3', 'Proficient Level'),
                                             ('4', 'Expert Level')])
    android_ios_flex = BooleanField('Inflexible', default=False)

    docker_level = SelectField('Please select Docker level', validators=[DataRequired()],
                               choices=[('1', 'Novice Level'),
                                        ('2', 'General Level'),
                                        ('3', 'Proficient Level'),
                                        ('4', 'Expert Level')])
    docker_flex = BooleanField('Inflexible', default=False)

    cloud_level = SelectField('Please select Cloud Technique level', validators=[DataRequired()],
                              choices=[('1', 'Novice Level'),
                                       ('2', 'General Level'),
                                       ('3', 'Proficient Level'),
                                       ('4', 'Expert Level')])
    cloud_flex = BooleanField('Inflexible', default=False)

    linux_level = SelectField('Please select Linux level', validators=[DataRequired()],
                              choices=[('1', 'Novice Level'),
                                       ('2', 'General Level'),
                                       ('3', 'Proficient Level'),
                                       ('4', 'Expert Level')])
    linux_flex = BooleanField('Inflexible', default=False)

    database_level = SelectField('Please select Database level', validators=[DataRequired()],
                                 choices=[('1', 'Novice Level'),
                                          ('2', 'General Level'),
                                          ('3', 'Proficient Level'),
                                          ('4', 'Expert Level')])
    database_flex = BooleanField('Inflexible', default=False)

    statistics_level = SelectField('Please select Statistics level', validators=[DataRequired()],
                                   choices=[('1', 'Novice Level'),
                                            ('2', 'General Level'),
                                            ('3', 'Proficient Level'),
                                            ('4', 'Expert Level')])
    statistics_flex = BooleanField('Inflexible', default=False)

    machine_learning_level = SelectField('Please select Machine Learning level', validators=[DataRequired()],
                                         choices=[('1', 'Novice Level'),
                                                  ('2', 'General Level'),
                                                  ('3', 'Proficient Level'),
                                                  ('4', 'Expert Level')])
    machine_learning_flex = BooleanField('Inflexible', default=False)
    # Return to previous page
    back = SubmitField('Previous Page')
    submit = SubmitField('Submit')


'''
# This class contains attributes of education field and it is not used in our system.
# However, the subsequent extensions of the system may use this class. 
class EducationField(FlaskForm):
    category_name = StringField('Internship Field', validators=[DataRequired()], id='contentcode')
    character = SelectField('Please select the most suitable character for you ', validators=[DataRequired()],
                            choices=[('1 ', 'introvert'),
                                     ('2', 'lively'),
                                     ('3 ', 'silent '),
                                     ('4', 'easy going'),
                                     ('5', 'impulsive'),
                                     ('6', 'passionate')])
    character_flex = BooleanField('Inflexible', default=False)
    interpersonal_skills = SelectField('Please select interpersonal skills level', validators=[DataRequired()],
                                       choices=[('1', 'bad'),
                                                ('2', 'normal'),
                                                ('3', 'good'),
                                                ('4', 'excellent')])
    interpersonal_flex = BooleanField('Inflexible', default=False)
    time_management_skills = SelectField('Please select time management skills level', validators=[DataRequired()],
                                         choices=[('1', 'bad'),
                                                  ('2', 'normal'),
                                                  ('3', 'good'),
                                                  ('4', 'excellent')])
    time_management_flex = BooleanField('Inflexible', default=False)
    teaching_qualification = SelectField('Please choose if you have teaching qualification',
                                         validators=[DataRequired()],
                                         choices=[('1', 'I have teaching qualification'),
                                                  ('2', 'I don\'t have teaching qualification'),
                                                  ])
    teaching_qualification_flex = BooleanField('Inflexible', default=False)

    years_experience = SelectField('Please select teaching years ', validators=[DataRequired()],
                                   choices=[('1', '0 year'),
                                            ('2', '0-3 years'),
                                            ('3', '3-6 years'),
                                            ('4', 'more than 6 years')])
    years_experience_flex = BooleanField('Inflexible', default=False)
    language_requirement = SelectField('Please select teaching language ', validators=[DataRequired()],
                                       choices=[('English', 'English'), ('French', 'French'), ('Spanish', 'Spanish'),
                                                ('Arabic', 'Arabic'), ('Mandarin', 'Mandarin'), ('Russian', 'Russian'),
                                                ('Portuguese', 'Portuguese'), ('German', 'German'),
                                                ('Japanese', 'Japanese'),
                                                ('Hindustani ', 'Hindustani'), ('Malay', 'Malay'),
                                                ('Italian', 'Italian'),
                                                ('Dutch', 'Dutch'), ('Vietnamese', 'Vietnamese'), ('Polish', 'Polish'),
                                                ('Thai Language', 'Thai Language'), ('Korean', 'Korean')])
    language_requirement_flex = BooleanField('Inflexible', default=False)
    teaching_field = SelectField('Please select preferred teaching field ', validators=[DataRequired()],
                                 choices=[('English', 'English'), ('Drama', 'Drama'), ('Humanities', 'Humanities'),
                                          ('History', 'History'), ('Geography', 'Geography'),
                                          ('Mathematics', 'Mathematics'),
                                          ('Chemistry', 'Chemistry'), ('Physics', 'Physics'),
                                          ('Psychology', 'Psychology'),
                                          ('Biology ', 'Biology'), ('Business Studies', 'Business Studies'),
                                          ('IT / ICT / Technology', 'IT / ICT / Technology'),
                                          (
                                              'LOTE',
                                              'LOTE-French / Italian / German / Mandarin / Chinese / Japanese / Indonesian / Spanish / Arabic')
                                          ])
    teaching_field_flex = BooleanField('Inflexible', default=False)
    monitor_experience = SelectField('Please select monitoring experience ', validators=[DataRequired()],
                                     choices=[('1', 'Not much'), ('2 ', 'General '), ('3', 'Rich')])
    monitor_flex = BooleanField('Inflexible', default=False)
    assess_experience = SelectField('Please select assessing experience ', validators=[DataRequired()],
                                    choices=[('1', 'Not much'), ('2 ', 'General '), ('3', 'Rich')])
    assess_flex = BooleanField('Inflexible', default=False)
    teaching_strategies = SelectField('Please select teaching strategies ', validators=[DataRequired()],
                                      choices=[('1', 'Not much'), ('2 ', 'General '), ('3', 'Rich')])
    teaching_strategies_flex = BooleanField('Inflexible', default=False)
    literacy_numeracy_skills = SelectField('Please select teaching literacy and numeracy skills ',
                                           validators=[DataRequired()],
                                           choices=[('1', 'Not much'), ('2 ', 'General '),
                                                    ('3', 'Rich')])
    literacy_numeracy_flex = BooleanField('Inflexible', default=False)
    address_adult_language = SelectField('Please select addressing adult language ability ',
                                         validators=[DataRequired()],
                                         choices=[('1', 'Not good'), ('2 ', 'Normal '),
                                                  ('3', 'Good'), ('4', 'Excellent')])
    address_adult_language_flex = BooleanField('Inflexible', default=False)
    back = SubmitField('Previous Page')
    submit = SubmitField('Submit')

# This class contains attributes of engineer field and it is not used in our system.
# However, the subsequent extensions of the system may use this class. 
class EngineerField(FlaskForm):
    category_name = StringField('Internship Field', validators=[DataRequired()], id='contentcode')
    years_of_work_experience = SelectField('Please select the working years ', validators=[DataRequired()],
                                           choices=[('1', '0 year'),
                                                    ('2', '0-3 years'),
                                                    ('3', '3-6 years'),
                                                    ('4', 'more than 6 years')])

    work_experience_flex = BooleanField('Inflexible', default=False)
    knowledge_oil_gas = SelectField('Please select the knowledge of oil and gas',
                                    validators=[DataRequired()],
                                    choices=[('1', 'Not much'), ('2 ', 'General '),
                                             ('3', 'Rich')])
    oil_gas_flex = BooleanField('Inflexible', default=False)
    oilfield_petrochemical_experience = SelectField(
        'Please select the degree of experience on oilfield and petrochemical',
        validators=[DataRequired()],
        choices=[('1', 'Not much'), ('2 ', 'General '),
                 ('3', 'Rich')])
    oilfield_petrochemical_flex = BooleanField('Inflexible', default=False)
    knowledge_of_the_latest_telecommunications_technology = SelectField(
        'Please select the  knowledge of the latest telecommunications technology',
        validators=[DataRequired()],
        choices=[('1', 'Not much'), ('2 ', 'General '),
                 ('3', 'Rich')])
    the_latest_telecommunications_technology_flex = BooleanField('Inflexible', default=False)
    familiar_with_industry_projects = SelectField('Please select familiar degree with industry project  ',
                                                  validators=[DataRequired()],
                                                  choices=[('1', 'Not good'), ('2 ', 'Normal '),
                                                           ('3', 'Good'), ('4', 'Excellent')])
    industry_projects_flex = BooleanField('Inflexible', default=False)
    engineering_design_experience = SelectField(
        'Please select the degree of experience on oilfield and petrochemical',
        validators=[DataRequired()],
        choices=[('1', 'Not much'), ('2 ', 'General '),
                 ('3', 'Rich')])
    engineering_design_flex = BooleanField('Inflexible', default=False)
    knowledge_applicable_codes_standards = SelectField(
        'Please select the  degree of the knowledge of the applicable codes standards',
        validators=[DataRequired()],
        choices=[('1', 'Not good'), ('2 ', 'Normal '),
                 ('3', 'Good'), ('4', 'Excellent')])
    applicable_codes_standards_flex = BooleanField('Inflexible', default=False)
    communicating_interfacing_skills = SelectField(
        'Please select the  degree of communicating interfacing skills',
        validators=[DataRequired()],
        choices=[('1', 'Not good'), ('2 ', 'Normal '),
                 ('3', 'Good'), ('4', 'Excellent')])
    communicating_interfacing_flex = BooleanField('Inflexible', default=False)
    back = SubmitField('Previous Page')
    submit = SubmitField('Submit')
'''
