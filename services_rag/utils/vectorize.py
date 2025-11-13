from sentence_transformers import SentenceTransformer

# model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
e5_model = SentenceTransformer('intfloat/e5-base-v2')
def embed_text(text: str, is_query:bool = False) -> list:
    """
    Generate vector embeddings for the given text using a pre-trained SentenceTransformer model.
    
    Args:
        text (str): The input text to be embedded.

    Returns:
        list: A list of float embeddings representing the input text.
    """
    # return model.encode(text).tolist()
    if is_query:
        return e5_model.encode(f"query: {text}").tolist()
    else:
        return e5_model.encode(f"passage: {text}").tolist()
