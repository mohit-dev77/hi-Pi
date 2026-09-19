import json
from pathlib import Path


class ContextStore:

    def __init__(self):

        self.path = (
            Path(__file__).resolve().parents[2]
            / "context_store.json"
        )

    def save(self, user_id, context):

        existing = self.load_all()

        existing[user_id] = context

        self.path.write_text(
            json.dumps(
                existing,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

    def get(self, user_id):

        data = self.load_all()

        return data.get(user_id)

    def load_all(self):

        if not self.path.exists():

            return {}

        return json.loads(
            self.path.read_text(
                encoding="utf-8"
            )
        )

    def build_and_save_all(
        self,
        context_builder
    ):

        from app.database.models import User

        users = (
            context_builder.db
            .query(User)
            .all()
        )

        for user in users:

            context = (
                context_builder
                .get_user_context(
                    user.user_id
                )
            )

            self.save(
                user.user_id,
                context
            )