import re
import hashlib
from dataclasses import dataclass
from datetime import datetime
from sqlmodel import Session
from ..databases import auth_database

@dataclass
class User:
    user_id: int | None = None
    name: str = ""
    age: str = ""
    gender: str = ""
    email: str = ""
    password: str = ""
    created_on: datetime | None = None

    def get_pronounce(self) -> str:
        if (self.gender == "Male"):
            return "He/Him"
        if (self.gender == "Female"):
            return "She/Her"
        if (self.gender == "Rather not say"):
            return "They/Them"
        return ""

    def validate(self, session: Session) -> list[str]:
        errors = []
        
        # 1. Required Fields Check
        # We check the attributes of 'self' instead of a form_data dict
        if not self.name: errors.append("Name is required.")
        if not self.age: errors.append("Age is required.")
        if not self.gender: errors.append("Gender is required.")
        if not self.email: errors.append("Email is required.")
        if not self.password: errors.append("Password is required.")

        # 2. Database Check
        if self.email:
            existing_user = auth_database.fetchByEmail(session, self.email)
            if existing_user:
                errors.append("An account with this email already exists.")

        # 3. Email Format Check
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if self.email and not re.match(email_regex, self.email):
            errors.append("Please enter a valid email address.")

        # 4. Age Numeric Check
        if self.age and not str(self.age).isdigit():
            errors.append("Age must be a number.")

        # 5. Password Strength Check
        if self.password and len(self.password) < 5:
            errors.append("Password must be at least 5 characters long.")

        return errors

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes the current password stored in the object."""
        if password:
            return hashlib.sha256(password.encode()).hexdigest()
        return ""

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.user_id == other.user_id
    
    def __hash__(self):
        return hash(self.user_id)