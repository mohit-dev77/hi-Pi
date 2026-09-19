from app.database.seed import seed
from app.matching.similarity import similar_users


def test_similar_users_works_without_sklearn():
    seed()
    matched = similar_users("U1001", limit=3)

    assert len(matched) == 3
    assert all(item["user_id"] != "U1001" for item in matched)
    assert all(0.0 <= item["similarity"] <= 1.0 for item in matched)
