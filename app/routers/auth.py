import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.models import models
from app.configs.db import get_session
import uuid
from jose import jwt
from app.configs.config import SECRET_KEY, ALGORITHM
from app.auth.bearer import JWTBearer
from app.auth.email_verification import send_verification_email
from app.auth.utils import verify_password, create_access_token, create_refresh_token, get_hashed_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post('/login' ,response_model=schemas.TokenSchema)
def login(request: schemas.requestdetails, db: Session = Depends(get_session)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password or email")
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password or email"
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verfied"
        )
    role = user.role
    access=create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = models.TokenTable(uid=user.id,  access_token=access,role=role,  refresh_token=refresh, status=True)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "role": role,
    }


@router.post("/register")
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    existing_email_user = session.query(models.User).filter_by(email=user.email).first()
    existing_phone_user = session.query(models.User).filter_by(phone=user.phone).first()

    if existing_email_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if existing_phone_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    encrypted_password = get_hashed_password(user.password)
    verification_token_str = str(uuid.uuid4())

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
        verification_token=verification_token_str,
        country=user.country,
        is_verified=False,
        role=user.role,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    send_verification_email(user.email, verification_token_str)

    return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message: user created successfully. Please check your email to verify your account."},
            media_type="application/json"
        )


@router.post('/change-password')
def change_password(request: schemas.changepassword, db: Session = Depends(get_session), dependencies=Depends(JWTBearer())):
    token = dependencies
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    existing_token = db.query(models.TokenTable).filter(
        models.TokenTable.uid == user_id,
        models.TokenTable.access_token == token
    ).first()

    if existing_token:
        user = db.query(models.User).filter(models.User.email == request.email).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
        
        if not verify_password(request.old_password, user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")
        
        encrypted_password = get_hashed_password(request.new_password)
        user.password = encrypted_password
        db.commit()
        return JSONResponse(    
            status_code=status.HTTP_200_OK,
            content={"message": "Password Changed Successfully"}
        )  
    else: 
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Token not valid"},
            media_type="application/json"
        )



@router.get('/logout')
def logout(dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    user_id = payload['sub']

    existing_token = session.query(models.TokenTable).filter(
        models.TokenTable.uid == user_id,
        models.TokenTable.access_token == token
    ).first()

    if existing_token:
        session.delete(existing_token)
        session.commit()
        return JSONResponse(    
            status_code=status.HTTP_200_OK,
            content={"message": "Logout Successfully"}
        )    
    else:
        # Handle the case where the token is not found (optional)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Token not valid"},
            media_type="application/json"
        )


   
@router.get("/verify/{token}")
def verify_email(token: str, session: Session = Depends(get_session)):
    user = session.query(models.User).filter_by(verification_token=token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.is_verified = True
    user.verification_token = None  # Clear the token once verified
    session.commit()

    return JSONResponse(    
        status_code=status.HTTP_200_OK,
        content={"message": "Email Verified Successfully"}
    )    