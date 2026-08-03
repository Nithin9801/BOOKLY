from fastapi import APIRouter, status, Depends,BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.redis import add_token_to_blocklist
from src.db.main import get_session
from src.errors import (
    UserAlreadyExists,
    InvalidCredentials,
    InvalidToken,
    UserNotFound
)
from src.mail import mail,create_message
from src.config import Config
from src.celery_tasks import send_email

from .service import UserService
from .schemas import UserCreateModel, UserLoginModel , UserBookResponse,EmailModel,PasswordResetRequestModel,PasswordResetConfirmModel
from .utils import verify_password, create_access_token,create_url_safe_token,decode_url_safe_token,generate_passwd_hash
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker
)

from datetime import timedelta, datetime

REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["user"])

@auth_router.post('/send_mail')
async def send_mail(emails:EmailModel,bg_tasks:BackgroundTasks):
    emails = emails.adresses

    
    subject="Hi!, welcome to our website",
    template_body={"verification_url":"google.com"}
    

    send_email.delay(emails,subject,template_body)
                        

    return {"message":"message sent successfully"}



@auth_router.post('/signup',status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    """
    Create user account using email, username, first_name, last_name
    params:
        user_data: UserCreateModel
    """
    email = user_data.email

    user_exist = await user_service.user_exists(email, session)

    if user_exist:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data,session)

    token = create_url_safe_token({"email":email})
    link = f"http://{Config.DOMAIN}/api/v1/user/verify/{token}"

    message = create_message(
            recipients=[email],
            subject="welcome",
            template_body={"verification_url":link}
        )

    await mail.send_message(message,template_name="verification.html")

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.post('/login')
async def user_login(login_data:UserLoginModel,session:AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email,session)

    if user is not None:
        password_valid = verify_password(password,user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    "email":email,
                    "user_uid":str(user.uid),
                    "role":user.role
                }
            )

            refresh_token = create_access_token(
                user_data={
                    "email":email,
                    "user_uid":str(user.uid),
                    "role":user.role
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(
               content={"message":"login successful",
                "email":user.email,
                "user_uid":str(user.uid),
                "json_access_token":access_token,
                "json_refresh_token":refresh_token}
            )

    raise InvalidCredentials()

@auth_router.post("/password-reset-request")
async def password_reset_request(email_data:PasswordResetRequestModel,session:AsyncSession=Depends(get_session)):
    email = email_data.email

    token = create_url_safe_token({"email":email})

    link = f"http://{Config.DOMAIN}/api/v1/user/password-reset-confirm/{token}"
    user = await user_service.get_user_by_email(email,session)
    message = create_message(
                recipients=[email],
                subject="Password reset",
                template_body={"username":user.username,
                               "reset_url":link}
            )
    
    await mail.send_message(message,template_name="password_reset.html")

    return JSONResponse(
        content={"message": "Please check your email for instructions to reset your password"},
        status_code=status.HTTP_200_OK
    )

@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(token: str,
                                 passwords: PasswordResetConfirmModel,
                                 session: AsyncSession = Depends(get_session)):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(
            detail="passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )

    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email,session)

        if not user:
            raise UserNotFound()

        password_hash = generate_passwd_hash(new_password)
        await user_service.update_user(user,{"password_hash":password_hash},session)

        return JSONResponse(
            content={"message":"password reset successfull"},
            status_code=status.HTTP_200_OK
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.get('/me',response_model=UserBookResponse)
async def get_current_user(user = Depends(get_current_user),_:bool = Depends(role_checker)):
    return user

@auth_router.get('/logout')
async def revoke_token(token_details:dict = Depends(AccessTokenBearer())):

    jti = token_details['jti']

    await add_token_to_blocklist(jti)

    return JSONResponse(
        content={
            "message":"Logged out successful"
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.get('/refresh_token')
async def get_new_access_token(token_details:dict = Depends(RefreshTokenBearer())):
    exp_timestamp = token_details['exp']

    if datetime.fromtimestamp(exp_timestamp) > datetime.now():
        new_accesstoken = create_access_token(user_data=token_details['user'])

        return JSONResponse(
            content={"Access Token ":new_accesstoken}
        )

    raise InvalidToken()
