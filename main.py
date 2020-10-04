from typing import Optional
from fastapi import FastAPI
import databases,sqlalchemy,datetime,uuid
from pydantic import BaseModel,Field
from typing import List
from sqlalchemy.orm import sessionmaker,relationship,mapper
from fastapi.middleware.cors import CORSMiddleware

##Database 
DATABASE_URL = "sqlite:///jobportal.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


  
jobs=sqlalchemy.Table(
  "job",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
  sqlalchemy.Column("job_title",sqlalchemy.String),
  sqlalchemy.Column("profile_description",sqlalchemy.String),
  sqlalchemy.Column("category",sqlalchemy.String),
  sqlalchemy.Column("package",sqlalchemy.String),
  sqlalchemy.Column("required_skills",sqlalchemy.String),
  sqlalchemy.Column("posted_date",sqlalchemy.String),
 )  
users=sqlalchemy.Table(
  "user",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
  sqlalchemy.Column("username",sqlalchemy.String,primary_key=True,unique=True),
  sqlalchemy.Column("email",sqlalchemy.String),
  sqlalchemy.Column("first_name",sqlalchemy.String),
  sqlalchemy.Column("last_name",sqlalchemy.String),
  sqlalchemy.Column("gender",sqlalchemy.CHAR),
  sqlalchemy.Column("user_type",sqlalchemy.CHAR),
 )
jobapplication=sqlalchemy.Table(
  "application",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
  sqlalchemy.Column("job_id",sqlalchemy.String, ),
  sqlalchemy.Column("user_name",sqlalchemy.String, ),
  sqlalchemy.Column("applied",sqlalchemy.String),
  sqlalchemy.Column("application_date",sqlalchemy.String),
  sqlalchemy.Column("status",sqlalchemy.String),
 )

engine = sqlalchemy.create_engine(DATABASE_URL,echo=True)
metadata.create_all(engine)


##Model
class UserList(BaseModel):
  id : str
  username : str
  email : str
  first_name : str
  last_name : str
  gender : str
  user_type : str

class JobList(BaseModel):
  id : str
  job_title : str
  profile_description : str
  category : str
  package : str
  required_skills : str
  posted_date : str

class JobapplicationList(BaseModel):
  id : str
  job_id : str
  user_name : str
  applied : str
  application_date : str
  status : str

class UserData(BaseModel):
  username : str = Field(..., example="username")
  email : str = Field(..., example="abc@gmail.com")
  first_name : str = Field(..., example="Will")
  last_name : str = Field(..., example="Smith")
  gender : str = Field(..., example="M/F")
  user_type : str = Field(..., example="Admin/Customer")

class JobData(BaseModel):
  job_title : str = Field(..., example="Engineer")
  profile_description : str = Field(..., example="Looking for a Java Developer")
  category : str = Field(..., example="Developer")
  package : str = Field(..., example="4-5 LPA")
  required_skills : str = Field(..., example="Java,MYSql")

class UserchkData(BaseModel):
  username : str = Field(..., example="abc@gmail.com")
 
class UpdateJobData(BaseModel):
  id : str = Field(..., example="Enter Job Id to Update")
  job_title : str = Field(..., example="Engineer")
  profile_description : str = Field(..., example="Looking for a Java Developer")
  category : str = Field(..., example="Developer")
  package : str = Field(..., example="4-5 LPA")
  required_skills : str = Field(..., example="Java,MYSql")

class JobApply(BaseModel):
  job_id : str = Field(..., example="Id of job")
  user_name : str = Field(..., example="Applicant Name")
  
  
app = FastAPI(title="Job API using FastAPI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/jobs", response_model=List[JobList])
async def find_jobs():
  query = jobs.select()
  conn = engine.connect()
  return conn.execute(query).fetchall()
  

@app.get("/jobs/{id}", response_model=JobList)
async def find_job_by_id(id : str):
  query = jobs.select().where(jobs.c.id == id)
  conn = engine.connect()
  return conn.execute(query).fetchone()
  

@app.post("/jobs", response_model=JobList)
async def add_job(job : JobData):
  jid=str(uuid.uuid1())
  pdate=str(datetime.datetime.now())
  query = jobs.insert().values(
    id=jid,
    job_title = job.job_title,
    profile_description = job.profile_description,
    category = job.category,
    package = job.package,
    required_skills = job.required_skills,
    posted_date = pdate
  )
  conn = engine.connect()
  conn.execute(query)
  
  return {
  "id":jid,
  **job.dict(),
  "posted_date": pdate
  }

@app.put("/jobs", response_model=JobList)
async def update_job(job : UpdateJobData):
  pdate=str(datetime.datetime.now())
  query = jobs.update().where(jobs.c.id==job.id).values(
    job_title = job.job_title,
    profile_description = job.profile_description,
    category = job.category,
    package = job.package,
    required_skills = job.required_skills,
    posted_date = pdate
  )
  conn = engine.connect()
  conn.execute(query)
  return await find_job_by_id(job.id)

@app.post("/jobs/{id}/apply")
async def apply_job(jobapply : JobApply):
  adate=str(datetime.datetime.now())
  query = jobapplication.insert().values(
    job_id = jobapply.job_id,
    user_name = jobapply.user_name,
    applied = '0',
    application_date = adate,
    status = "inreview"
  )
  conn = engine.connect()
  conn.execute(query)
  return {
  "Message" : "Application Submited Sucessfully"
  }


@app.delete("/jobs/{id}")
async def delete_job(id : str):
  query = jobs.delete().where(jobs.c.id == id)
  conn = engine.connect()
  conn.execute(query)
  return {
  "id":id,
  "Message":"The Job with above Id is Deleted"
  }


@app.get("/user", response_model=List[UserList])
async def find_users():
  query = users.select()
  conn = engine.connect()
  return conn.execute(query).fetchall()

@app.post("/user", response_model=UserList)
async def find_user_by_name(user : UserchkData):
  query = users.select().where(users.c.username == user.username)
  conn = engine.connect()
  return conn.execute(query).fetchone()

@app.post("/user/add", response_model=UserList)
async def add_user(user : UserData):
  uid=str(uuid.uuid1())
  query = users.insert().values(
    id=uid,
    username = user.username,
    email = user.email,
    first_name = user.first_name,
    last_name = user.last_name,
    gender = user.gender,
    user_type = user.user_type
  )
  conn = engine.connect()
  conn.execute(query)
  return {
  "id":uid,
  **user.dict(),
  }
  
@app.get("/apply", response_model=List[JobapplicationList])
async def find_jobs():
  query = jobapplication.select()
  conn = engine.connect()
  return conn.execute(query).fetchall()


	
