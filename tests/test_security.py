from app.security import hash_password, verify_password


def test_hash_password_returns_non_plaintext_value():
    plain = "supersecure123"
    hashed = hash_password(plain)

    assert hashed != plain
    assert hashed


def test_verify_password_accepts_correct_password():
    plain = "supersecure123"
    hashed = hash_password(plain)

    assert verify_password(plain, hashed) is True


def test_verify_password_rejects_incorrect_password():
    hashed = hash_password("supersecure123")

    assert verify_password("wrongpassword", hashed) is False
