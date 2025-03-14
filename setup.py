import os
import sys
import secrets
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Create models
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

def create_tables():
    """Create all database tables"""
    db.create_all()
    print("Tables created successfully!")

def create_admin_user(username, password):
    """Create an admin user"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user '{username}' created successfully!")
    else:
        print(f"User '{username}' already exists.")

def create_env_file():
    """Create a .env file with secure settings"""
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(f"SECRET_KEY={secrets.token_hex(16)}\n")
            f.write(f"DB_NAME={input('Database name [contas]: ') or 'contas'}\n")
            f.write(f"DB_USER={input('Database user [postgres]: ') or 'postgres'}\n")
            
            # Hide password input
            import getpass
            db_password = getpass.getpass('Database password: ')
            f.write(f"DB_PASSWORD={db_password}\n")
            
            f.write(f"DB_HOST={input('Database host [localhost]: ') or 'localhost'}\n")
        print(".env file created successfully!")
    else:
        print(".env file already exists.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'create_env':
            create_env_file()
        elif sys.argv[1] == 'create_tables':
            create_tables()
        elif sys.argv[1] == 'create_admin':
            if len(sys.argv) < 4:
                print("Usage: python setup.py create_admin <username> <password>")
            else:
                create_admin_user(sys.argv[2], sys.argv[3])
        else:
            print("Unknown command. Available commands:")
            print("  create_env: Create a .env file")
            print("  create_tables: Create database tables")
            print("  create_admin <username> <password>: Create an admin user")
    else:
        print("Please specify a command. Available commands:")
        print("  create_env: Create a .env file")
        print("  create_tables: Create database tables")
        print("  create_admin <username> <password>: Create an admin user")
