import uuid


def generate_registration_id():
    return f"zep-{str(uuid.uuid4())[:5]}"

def generate_transaction_id():
    return f"tnx-{str(uuid.uuid4())[:5]}"