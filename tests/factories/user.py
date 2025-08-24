from typing import Optional, cast

from app.infra.models import user
from app.infra.models.user import User
from tests.common import fixed_time
from tests.factories.base import DBModelFactory


class UserFactory(DBModelFactory[User]):
    class Meta:
        model = user.User


def create_user(
    cognito_user_id: str,
    email: str,
    display_name: str,
    id: Optional[int] = None,
) -> user.User:

    attrs: dict[str, object] = {
        "cognito_user_id": cognito_user_id,
        "email": email,
        "display_name": display_name,
        "created_at": fixed_time,
        "updated_at": fixed_time,
        "deleted": False,
    }
    if id is not None:
        attrs["id"] = id

    return cast(
        User,
        UserFactory.create(**attrs),
    )
