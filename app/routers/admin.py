from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.configs.db import get_session
from app.schemas import schemas
from app.models import models
from jose import jwt
from app.configs.config import SECRET_KEY, ALGORITHM
from app.auth.bearer import JWTBearer
import uuid, datetime
from app.auth.utils import verify_password, create_access_token, create_refresh_token, get_hashed_password
router = APIRouter(prefix="/admin", tags=["admin"])

@router.get('/users')
def get_users(dependencies=Depends(JWTBearer()),session: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    admin_id = payload['sub']

    existing_token = session.query(models.TokenTable).filter(
        models.TokenTable.uid == admin_id,
        models.TokenTable.access_token == token
    ).first()

    if existing_token:
        user = session.query(models.User).filter(models.User.id == admin_id).first()
        if user.role == 'admin':
            users = session.query(models.User).all()
            return users
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )
    else:
        return {"message": "Invalid or expired token"}
    
@router.post("/users/create")
def register_user(user: schemas.UserCreate,dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    admin_id = payload['sub']
    existing_token = session.query(models.TokenTable).filter(
        models.TokenTable.uid == admin_id,
        models.TokenTable.access_token == token
    ).first()

    if existing_token:
        admin = session.query(models.User).filter(models.User.id == admin_id).first()
        if admin.role == 'admin':
            existing_user = session.query(models.User).filter_by(email=user.email).first()
            existing_phone_user = session.query(models.User).filter_by(phone=user.phone).first()

            if existing_phone_user:
                raise HTTPException(status_code=400, detail="Phone number already registered")

            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")

            encrypted_password = get_hashed_password(user.password)

            new_user = models.User(
                id=str(uuid.uuid4()),
                created_at=datetime.datetime.now(),
                email=user.email,
                password=encrypted_password,
                phone=user.phone,
                full_name=user.full_name,
                address=user.address,
                date_of_birth=user.date_of_birth,
                gender=user.gender,
                country=user.country,
                is_verified=True,
                role=user.role,
            )

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return {"message": "User created successfully."}
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )
    else:
        return {"message": "Invalid or expired token"}



@router.delete("/users/{user_id}")
def delete_user(user_id:str, dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    admin_id = payload['sub']
    existing_token = session.query(models.TokenTable).filter(
        models.TokenTable.uid == admin_id,
        models.TokenTable.access_token == token
    ).first()
    
    if existing_token:
        admin = session.query(models.User).filter(models.User.id == admin_id).first()
        user = session.query(models.User).filter(models.User.id == user_id).first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if admin.role == 'admin':
            session.delete(user)
            session.commit()
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Token not valid"},
            media_type="application/json"
        )
    
@router.put('/users/{user_id}')
def edit_user(user_data: schemas.UserAdminIn, user_id:str, dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    admin_id = payload['sub']
    existing_token = session.query(models.TokenTable).filter(
        models.TokenTable.uid == admin_id,
        models.TokenTable.access_token == token
    ).first()
    
    if existing_token:
        admin = session.query(models.User).filter(models.User.id == admin_id).first()
        user = session.query(models.User).filter(models.User.id == user_id).first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if admin.role == 'admin':
            user.full_name=user_data.full_name
            user.address=user_data.address
            user.date_of_birth=user_data.date_of_birth
            user.gender=user_data.gender
            user.country=user_data.country
            user.role=user_data.role

            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Token not valid"},
            media_type="application/json"
        )
