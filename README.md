# backend-template

## 実績のある動作環境

- OS: mac

## 前提

- `make` と `docker-compose`、`pyenv`、`pip` がインストール済みであること

## 環境構築

1. **依存ライブラリのインストール**

    ```bash
    make setup
    ```

    pyenv、python、poetry を使用してライブラリをインストールする。

2. **pre-commitのインストール**

    ```bash
    pre-commit install
    ```

3. **logsフォルダを作成**

    ```bash
    mkdir logs
    ```

4. **.env.exampleを元に.envを作成**

    ```bash
    cp .env.example .env
    ```

5. **コンテナのビルド**

    ```bash
    make build
    ```

6. **コンテナの立ち上げ**

    ```bash
    make up
    ```

7. **Swaggerドキュメントの確認**
    ブラウザで <http://localhost:8000/docs#> にアクセスし、Swaggerを確認します。

8. **テストの実行**

    ```bash
    make test
    ```

    pytest を使用してテストを実行します。

## データベースのマイグレーション
xxxという名前のテーブルを新たに追加する場合

1. **テーブルを追加**

    以下のようにDB設計の通りに二つのファイルを作成する。

    app/infra/models/xxx.py
    ```python
    # 例
    from sqlalchemy import Column, Integer, String

    from app.infra.models.base import Base


    class Xxx(Base):
        __tablename__ = "xxx"

        id = Column(Integer, primary_key=True, index=True)
        xxx_string = Column(String, nullable=False)
    ```

    app/domain/entity/xxx.py
    ```python
    # 例
    from datetime import datetime

    from pydantic import BaseModel, ConfigDict, Field


    class Xxx(BaseModel):
        id: int
        xxx_string: str = Field(default="")
        created_at: datetime = Field(default_factory=datetime.now)
        updated_at: datetime = Field(default_factory=datetime.now)

        model_config = ConfigDict(from_attributes=True)

    ```

2. **マイグレーションの更新**

    ```bash
    make alembic_autogenerate
    ```
    ファイル名はcreate_xxxに設定する。
    app/infra/alembic/versionsの下にマイグレーションファイルが生成されたことを確認する。

3. **新しいマイグレーションをデータベースに適用**

    ```bash
    make alembic_head
    ```
