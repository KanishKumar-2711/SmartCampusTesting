
from campus import connect

db = connect("campus.db")

print("Smart Campus Facility Platform")
print("Application started successfully")
print("Database connected successfully")

db.close()
