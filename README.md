# Sickle Cell Disease Patient/Provider Match Tool
![image](https://github.com/LLI1234/scd_tool/assets/48495973/1c4e31db-b0c7-408d-b804-2cea56141564)

This application was developed in collaboration with Novo Nordisk to support sickle cell disease (SCD) patients in finding their ideal care providers and addressing the data gap related to SCD.

## Key Features
* **User Registration**: Answer demographic questions during registration to contribute to anonymized data collection for future research.
* **Care Provider Matching**: Get matched with physicians based on accessibility, quality of care, and compatibility.
* **Symptom Tracking**: Track your symptoms within the app to help physicians provide better treatment.

## Technologies Used
**Languages**
* Python
* MySQL

**Packages**
* Flask
* Flask-Login
* SQLAlchemy
* Google Maps
* pandas
* scikit-learn

## Run Locally
### Frontend:
[https://github.com/LLI1234/scd_tool](https://github.com/LLI1234/scd_tool)

### Backend:
Configure .env file with:
* **APP_SECRET_KEY**
* **GOOGLE_MAP_API_KEY**
* **SQLALCHEMY_DATABASE_URI**: URI of the database using PyMySQL client library (mysql+pymysql://...)
* **HOST**: Host service IP

`conda env create -f environment.yml`

`flask run`
