import getpass
from email_validator import validate_email,EmailNotValidError
from sqlalchemy import or_,select
from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.entities import User,Role
print("M99 CREATE SUPER ADMIN")
username=input("Username: ").strip()
email=input("Email: ").strip().lower()
full_name=input("Full name: ").strip()
if not username:raise SystemExit("Username is required.")
try:email=validate_email(email,check_deliverability=False).normalized
except EmailNotValidError as e:raise SystemExit(f"Invalid email: {e}")
p1=getpass.getpass("Password: ");p2=getpass.getpass("Repeat password: ")
if p1!=p2:raise SystemExit("Passwords do not match.")
if len(p1)<12:raise SystemExit("Password must be at least 12 characters.")
with SessionLocal() as db:
    if db.scalar(select(User).where(or_(User.username==username,User.email==email))):raise SystemExit("Username or email already exists.")
    role=db.scalar(select(Role).where(Role.code=="M99_SUPER_ADMIN"))
    if not role:raise SystemExit("Run scripts/init_db.py first.")
    u=User(username=username,email=email,full_name=full_name,password_hash=hash_password(p1),is_superuser=True,active=True)
    u.roles.append(role);db.add(u);db.commit()
print("Super admin created successfully.")
