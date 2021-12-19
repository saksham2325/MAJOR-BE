import uuid


def token_generator():
    token = uuid.uuid4()
    token_key = str(token)
    return token_key
