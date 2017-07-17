from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from app import app

s=URLSafeTimedSerializer(app.config['SECRET_KEY']) #Serializer for token generation

def generate_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    email = serializer.loads(token,salt='email-confirm',max_age=expiration)
    return email
