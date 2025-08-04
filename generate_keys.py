import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

with open('C:/Users/Rohan/Projects/Project_8/FinancialAgent/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
stauth.Hasher.hash_passwords(config['credentials'])