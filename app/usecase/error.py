from typing import List, Union


class EntityNotFoundError(Exception):
    """エンティティが見つからない場合の例外"""

    def __init__(
        self,
        entity_name: str,
        entity_id: Union[List[int], int],
        message: str | None = None,
    ):
        if message is None:
            message = f"{entity_name} with ID {entity_id} was not found."
        super().__init__(message)
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.message = message


class DuplicateError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ConflictError(Exception):
    def __init__(self, entity_name: str):
        super().__init__(
            f"他のユーザが先に更新したため、{entity_name}の更新に失敗しました。"
        )


class ValidationParamError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class GetListUserOrganizationByUserIdEmptyError(Exception):
    def __init__(self, user_id: int):
        super().__init__(f"ユーザが組織に所属していません。 user_id: {user_id}")


class MemberAccessDeniedError(Exception):
    def __init__(self) -> None:
        super().__init__("メンバーはこの操作を実行する権限がありません")


class OrgMemberAccessDeniedError(Exception):
    def __init__(self) -> None:
        super().__init__("組織のユーザはこの操作を実行する権限がありません")


class AppAdminAccessDeniedError(Exception):
    def __init__(self) -> None:
        super().__init__("アプリの管理者はこの操作を実行する権限がありません")


class GenerationAccessDeniedError(Exception):
    def __init__(self) -> None:
        super().__init__("この文書を生成する権限がありません")


class PermissionDeniedError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AppAdminOnlyAccessError(Exception):
    def __init__(self) -> None:
        super().__init__("アクセス権がありません。アプリ管理者のみ操作可能です。")


class LackOfPlaceholderInOpenAIResponseError(Exception):
    def __init__(self, missing_keys: List[str]):
        message = "OpenAIのレスポンスに必要なキーが見つかりません。 不足しているキー: "
        for i, key in enumerate(missing_keys):
            message += key if i == 0 else ", " + key
        super().__init__(message)


class LackOfRequiredAnswerError(Exception):
    def __init__(self, missing_items: List[str]):
        message = "回答必須にもかかわらず回答が空欄になっている質問があります。 回答が不足している質問:"
        for i, item in enumerate(missing_items):
            message += f"「{item}」" if i == 0 else ", " + f"「{item}」"
        super().__init__(message)
