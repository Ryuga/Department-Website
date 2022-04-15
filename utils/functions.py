import uuid


def generate_registration_id():
    return f"zep-{str(uuid.uuid4())[:5]}"


def generate_transaction_id():
    return f"tnx-{str(uuid.uuid4())[:5]}"


def generate_css_text_animation(events):
    num = 0
    part = 100//len(events)
    generated_css = "@keyframes spin {"
    for event in events:
        generated_css += f"{num}%" + " { content:\"" + event.name + " Registration" + "\"; }"
        num += part
    return generated_css + "}"
