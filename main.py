import json
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from my_modules.models import Profile, Schedule, Activity, User
from my_modules.settings.db_settings import create_database, engine
from my_modules.settings.constants import ALLOWED_ORIGINS
from my_modules.utils import get_hashed_password, verify_password
from my_modules.user.jwt_authentication import create_access_token, create_refresh_token

app = FastAPI()

if ALLOWED_ORIGINS is None:
    raise Exception("No environment variables ALLOWED_ORIGINS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]

)
@app.on_event("startup")
def on_startup():
    create_database()


@app.post("/new_user")
async def add_user(email: str, password: str, password2: str) -> Response:
    hashed_password = get_hashed_password(password)
    if not verify_password(password2, hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    new_user = User(email=email, password=hashed_password)
    with Session(engine) as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        user_profile = Profile(email=email, user_id=User.id)
        session.add(user_profile)
        session.commit()
        session.refresh(user_profile)
    return Response(content=json.dumps({"Success": "New user account created."}), status_code=status.HTTP_201_CREATED)


@app.post("/login")
async def login_user(email: str, password: str) -> Dict:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email and User.password == password))
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
        access_token = create_access_token(email)
        refresh_token = create_refresh_token(email)
        return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/schedule")
async def new_schedule(new_schedule: Schedule)-> Response:
     with Session(engine) as session:
        session.add(new_schedule)
        session.commit()
        session.refresh(new_schedule)
        return Response(content=json.dumps({"Success": "New schedule created."}), status_code=status.HTTP_201_CREATED)


@app.put("/schedule/{id}")
async def edit_schedule(new_name: str, id: int) -> None:
    with Session(engine) as session:
        schedule_for_change = session.exec(select(Schedule).where(Schedule.id == id)).one()
        changed_schedule = schedule_for_change.name = new_name
        session.add(changed_schedule)
        session.commit()
        session.refresh(changed_schedule)


@app.get("/schedule")
async def get_all_schedule(limit: int | None = None, offset: int | None = None) -> List[Schedule]:
    with Session(engine) as session:
        schedules = session.exec(select(Schedule).limit(limit).offset(offset)).all()
        return schedules


@app.get("/schedule/{id}")
async def get_one_schedule(id: int) -> Response:
    with Session(engine) as session:
        schedule = session.exec(select(Schedule).where(Schedule.id == id)).one()
        if not schedule:
            return Response(content=json.dumps({"Error": "schedule with this id doesn't exist."}), status_code=status.HTTP_404_NOT_FOUND)
        return Response(content=schedule, status_code=status.HTTP_200_OK)


@app.delete("/schedule/{id}/delete")
async def delete_schedule(id: int) -> Response:
    with Session(engine) as session:
        schedule_for_deletion = session.exec(select(Schedule).where(Schedule.id == id)).one()
        if not schedule_for_deletion:
            return Response(content=json.dumps({"Error": "schedule with this id doesn't exist."}), status_code=status.HTTP_404_NOT_FOUND)
        session.delete(schedule_for_deletion)
        session.commit()
    return Response(content=json.dumps({"Success": "Activity deleted"}), status_code=status.HTTP_200_OK)


@app.post("/schedule/{id}/activity")
async def add_activity(request: Request) -> Response:
    body = await request.body()
    activity = dict(json.loads(body))
    print(body)
    new_activity = Activity(name=activity["name"], description=activity["description"], time=datetime.strptime(activity["time"], "%Y-%m-%dT%H:%M"), repetitive=activity["repetitive"], completed=False, schedule_id=activity["schedule_id"])
    with Session(engine) as session:
        session.add(new_activity)
        session.commit()
        session.refresh(new_activity)
    return Response(content=json.dumps({"Success": "Activity added"}), status_code=status.HTTP_200_OK)


@app.get("/schedule/{id}/activity")
async def get_activities(id: int) -> List[Activity]:
    with Session(engine) as session:
        activities = session.exec(select(Activity).where(Activity.schedule_id == id)).all()
    return activities


@app.put("schedule/activity/{id}")
async def edit_activity(
    id: int, name: str | None = None, time: str | None = None,
    description: str | None = None, repetitive: bool = False, completed: bool = False
    ) -> Response:
    with Session(engine) as session:
        activity = session.exec(select(Activity).where(Activity.id == id)).one()
        if name: activity.name = name
        if time: activity.time = datetime.strptime(time, "%Y-%m-%dT%H:%m:%sZ")
        if description: activity.description = description
        if repetitive: activity.repetitive = repetitive
        if completed: activity.completed = completed
        session.commit()
        session.refresh(activity)
    return Response(content=json.dumps({"Success": "Activity changed"}), status_code=status.HTTP_200_OK)


@app.delete("/schedule/activity/{id}/delete")
async def delete_activity(id: int) -> Response:
    with Session(engine) as session:
        activity_to_delete = session.exec(select(Activity).where(Activity.id == id)).one()
        session.delete(activity_to_delete)
        session.commit()
    return Response(content=json.dumps({"Success": "Activity deleted"}), status_code=status.HTTP_200_OK)
