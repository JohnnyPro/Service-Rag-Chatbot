def transform_dict_to_text_chunk(data: dict) -> str:
    """
    Transform a dictionary of service data into a formatted text chunk.
    
    Args:
        data (dict): Dictionary containing service attributes.
        
    Returns:
        str: Formatted text chunk representing the service data.
    """
    
    lines = []
    if "service_name" in data:
        lines.append(f"service_name: {data['service_name']}.")
        data.pop("service_name")
        
    for key, value in data.items():
        lines.append(f"{key}: {value}")
        
    return ". ".join(lines).strip()

def transform_doc_id_to_url(doc_id: str) -> str:
    """
    Transform a Google Doc ID into a full URL.
    
    Args:
        doc_id (str): The Google Doc ID.
        
    Returns:
        str: The full URL to access the Google Doc.
    """
    return f"https://docs.google.com/document/d/{doc_id}/edit"