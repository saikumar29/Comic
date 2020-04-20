from main import start_application
from main import ask_data_to_user

def run_application():
# if __name__=="main":
    application=start_application()
    application.store_user_information_db()
    Ask=ask_data_to_user(application)
    Ask.process_to_model()