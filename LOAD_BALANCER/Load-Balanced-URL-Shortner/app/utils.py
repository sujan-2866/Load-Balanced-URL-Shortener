import shortuuid

def generate_short_url():
    """Generate a short, unique URL identifier"""
    return shortuuid.uuid()[:8]