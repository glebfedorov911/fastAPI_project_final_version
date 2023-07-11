from fastapi_users import FastAPIUsers

from src.auth.base_config import auth_backend
from src.auth.manager import get_user_manager
from src.auth.models import User

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)

current_active_user = fastapi_users.current_user(active=True)