db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), unique=False, nullable=False)
    first_name = db.Column(db.String(30), unique=False, nullable=False)
    last_name = db.Column(db.String(30), unique=False, nullable=False)
    DoB = db.Column(db.datetime, unique=False, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    ethnicity = db.Column(db.String(10), unique=False)
    address = db.Column(db.String(60), unique=False, nullable=False)
    insurance = db.Column(db.String(30), unique=False)
    income = db.Column(db.Integer)
    education = db.Column(db.String(30))
    
    
class Center(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(60), unique=True, nullable=False)
    google_review = db.Column(db.String(150))
    email = db.Column(db.String(30), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    
class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    type = db.Column(db.String(30), unique=False, nullable=False) # Integer? 
    duration = db.Column(db.String(30), unique=False, nullable=False) # date time? Integer (in days or hours)
    
class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(30), uniqure=False, nullable=False)
    company = db.Column(db.String(20), unique=False, nullable=False)
    coverage = db.Column(db.Boolean)
    


    
    