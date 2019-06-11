# Internship Match-making
2019 Semester 1: COMP90055 Computing Project(25 credits)
  
  
Supervisor:       Prof. Richard Sinnott  
Project Manager:  Prof. Lea Campbell  
Author:           Shiqi Wang, Mingyuan Cui  
  
    
Our presentation video:    <br>
https://drive.google.com/file/d/14lO3wrx0y_MXyDCsqcKEYHdaTcAkpS0C/view?usp=sharing    
  
Our presentation slides:  <br>
https://drive.google.com/file/d/1BTHaPaJPSbmw2ccWBMTkYz4RtS6e7t3T/view?usp=sharing    
  
The structure of the code:  <br>
>Folders:  <br>
>>app: core code here:   
>>>routes.py: for running logic (jumping between pages, functions, parsing the forms)  
>>>forms.py: all forms used in the webpages are defined here   
>>>models.py: this class has the same structure as the tables in the database ("app.db")  <br>
>>>The three clases above are the most important classes in this project.  <br>
  
>>>Folder: templates  
>>>>all frontend webpages are defined here.  <br>
  
>>>emails and tasks: interfaces for some potential future work (automatically sending emails, etc)  <br>
>>>__init__.py: all the dependencies are listed here, and doing some configration before running the system.  <br>
  
>>files: uploaded files are stored here, for example, the CVs of the students. The "AceStream.pdf" is a test, please ignore it.<br>
>>migrations: deals the migrated databases, this is used to decrease coupling. <br>
>>logs: logs are here <br>  
  
>Other files:  <br>
>>config.py for configrations, settings.py for settings, run.py for running the system.   <br> 
    
How to run the system:    <br>
>Please execute "run.py" with no argument. (Please install the packages needed first, as listed below or have a look at "__init__.py")   
    <br>  
      
Running Environment:  <br>
Armin, R. (2010). The Python micro framework for building web applications.  
Retrieved from: https://github.com/pallets/flask   
  
Asif Saif, U. (2009). Celery. Retrieved from:  
http://flask.pocoo.org/docs/1.0/patterns/celery/  
  
Hsiaoming, Y. (2010). Flask-WTF. Retrieved from:  
https://flask-wtf.readthedocs.io/en/stable/   
  
Kush, T. (2010). Flask-SQLAlchemy. Retrieved from:   
https://github.com/pallets/flask-sqlalchemy  
  
Marc, B. (2012). Flask-Bootstrap. Retrieved from:   
https://pythonhosted.org/Flask-Bootstrap/  
  
Max, C. (2013). Flask-Login. Retrieved from:  
https://flask-login.readthedocs.io/en/latest/  
  
Miguel G. (2013). Flask-Migrate. Retrieved from:   
https://flask-migrate.readthedocs.io/en/latest/  
   
Miguel, G. (2014). Flask-Moment. Reteieved from:   
https://github.com/miguelgrinberg/Flask-Moment  
   


