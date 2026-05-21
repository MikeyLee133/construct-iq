from construct_iq.storage import chunk_text


def test_chunk_text_basic():
    text   = "a" * 600
    chunks = chunk_text(text)
    assert len(chunks) > 1


def test_chunk_text_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_short():
    chunks = chunk_text("Short text")
    assert len(chunks) == 1
    assert chunks[0] == "Short text"


def test_chunk_text_overlap():
    # With 500 char chunks and 50 overlap, a 600 char text gives 2 chunks
    text   = "x" * 600
    chunks = chunk_text(text)
    assert len(chunks) == 2


def test_chunk_text_no_empty_chunks():
    text   = "word " * 200
    chunks = chunk_text(text)
    assert all(c.strip() for c in chunks)
