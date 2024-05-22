from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.configs.db import get_session
from app.schemas import schemas
from app.models import models
from jose import jwt
from app.configs.config import SECRET_KEY, ALGORITHM
from app.auth.bearer import JWTBearer
from app.auth.utils import verify_password, create_access_token, create_refresh_token, get_hashed_password

router = APIRouter(prefix="/users", tags=["users"])
    
@router.get('/me')
def get_current_user(dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    user_id = payload['sub']

    existing_token = session.query(models.TokenTable).filter(
        models.TokenTable.uid == user_id,
        models.TokenTable.access_token == token
    ).first()
    if existing_token: 
        user = session.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Token not valid"},
            media_type="application/json"
        )
    
@router.put('/me')
def edit_user(user_data: schemas.UserIn, dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    user_id = payload['sub']

    existing_token = session.query(models.TokenTable).filter(
        models.TokenTable.uid == user_id,
        models.TokenTable.access_token == token
    ).first()
    if existing_token: 
        user = session.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user.email=user_data.email
        user.phone=user_data.phone
        user.full_name=user_data.full_name
        user.address=user_data.address
        user.date_of_birth=user_data.date_of_birth
        user.gender=user_data.gender
        user.country=user_data.country
    
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

@router.delete('/me')
def delete_user( dependencies=Depends(JWTBearer()),confirm_password:str = Query(...), session: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    user_id = payload['sub']

    existing_token = session.query(models.TokenTable).filter(
        models.TokenTable.uid == user_id,
        models.TokenTable.access_token == token
    ).first()
    
    if existing_token:
        user = session.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(confirm_password, user.password):
            raise HTTPException(status_code=401, detail="Incorrect password")

        session.delete(user)
        session.delete(existing_token)
        session.commit()
        return JSONResponse(    
            status_code=status.HTTP_200_OK,
            content={"message": "User deleted successfully"}
        )    
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Token not valid"},
            media_type="application/json"
        )

    