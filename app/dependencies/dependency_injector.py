from injector import Binder, Injector, Module

from app.domain.i_repository.organization import OrganizationIRepository
from app.domain.i_repository.s3 import S3IRepository
from app.domain.i_repository.user import UserIRepository
from app.domain.i_repository.user_organization import UserOrganizationIRepository
from app.infra.repository.organization import OrganizationRepository
from app.infra.repository.s3 import S3Repository
from app.infra.repository.user import UserRepository
from app.infra.repository.user_organization import UserOrganizationRepository


def get_injector() -> Injector:
    dependency = Dependency()
    return Injector([dependency])


class Dependency(Module):
    def configure(self, binder: Binder) -> None:
        # NOTE: mypy のバグ。cf: https://qiita.com/yuji38kwmt/items/9ff5f0562c2b3d4787c3
        binder.bind(interface=OrganizationIRepository, to=OrganizationRepository)  # type: ignore[type-abstract]
        binder.bind(interface=UserIRepository, to=UserRepository)  # type: ignore[type-abstract]
        binder.bind(interface=UserOrganizationIRepository, to=UserOrganizationRepository)  # type: ignore[type-abstract]
        binder.bind(interface=S3IRepository, to=S3Repository)  # type: ignore[type-abstract]
