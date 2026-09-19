from app.context.builder import ContextBuilder
from app.context.context_store import ContextStore


def refresh_context():

    builder = ContextBuilder()

    store = ContextStore()

    try:

        store.build_and_save_all(
            builder
        )

        print(
            "Context layer successfully refreshed."
        )

    finally:

        builder.close()


if __name__ == "__main__":

    refresh_context()