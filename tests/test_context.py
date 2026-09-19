from app.database.seed import seed
from app.context.builder import ContextBuilder

def test_context():
    seed()
    builder = ContextBuilder()
    ctx = builder.get_user_context("U1001")
    assert ctx["name"] == "Rahul Sharma"
    assert ctx["ordering_profile"]["total_orders"] > 0
    assert ctx["ordering_profile"]["favorite_cuisines"]
    builder.close()
