import bcrypt

# Helper function to hash passwords natively using bcrypt.
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")

# Helper function to verify passwords against the stored hash.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# Helper function to print SQLAlchemy queries in a human-readable format.
def print_query(query):
    sql_statement = query.statement.compile(
        bind = query.session.get_bind(),
        compile_kwargs = {"literal_binds": True}
    )
    print(sql_statement, "\n")
