from app.utils.nickname_gen import generate_nickname

def test_generate_nickname():
    nicknames = [generate_nickname() for _ in range(5)]
    
    # Check format
    for nickname in nicknames:
        assert len(nickname) >= 8  # Minimum length
        # Allow underscores in nicknames
        assert all(c.isalnum() or c == '_' for c in nickname)
        
    # Check uniqueness
    assert len(set(nicknames)) == len(nicknames)