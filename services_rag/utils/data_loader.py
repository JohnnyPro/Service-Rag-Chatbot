import requests
import re
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs


def scrape_google_doc(url: str) -> str:
    """
    Scrape content from a public Google Doc URL.
    
    Args:
        url (str): Public Google Doc URL
        
    Returns:
        str: Raw text content from the document
        
    Raises:
        Exception: If unable to access or parse the document
    """
    try:
        # Convert Google Doc sharing URL to export format
        if 'docs.google.com' in url:
            # Extract document ID from various Google Docs URL formats
            if '/document/d/' in url:
                doc_id = url.split('/document/d/')[1].split('/')[0]
            elif 'id=' in url:
                doc_id = parse_qs(urlparse(url).query).get('id', [None])[0]
            else:
                raise ValueError("Unable to extract document ID from URL")
            
            # Convert to export URL
            export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
            
            # Make request to get the document content
            response = requests.get(export_url)
            response.raise_for_status()
            
            return response.text
            
        else:
            raise ValueError("URL must be a Google Docs URL")
            
    except Exception as e:
        raise Exception(f"Failed to scrape Google Doc: {str(e)}")


def parse_services(content: str) -> List[Dict]:
    """
    Parse services from document content and extract structured information.
    
    Args:
        content (str): Raw text content from the document
        
    Returns:
        List[Dict]: List of service dictionaries with extracted attributes
    """
    services = []
    lines = content.split('\n')
   #  print('\n##'.join(lines[100:200]))
    # State tracking variables
    current_institution = None
    service_hierarchy = []  # Stack to track service hierarchy
    current_service = None
    
    # Regex patterns for attribute extraction
    inst_pattern = r'^\s*Institution:'
    service_pattern = r'^\s*-\s*Service:'
    sub_service_pattern = r'^\s*-\s*(Sub-)+Service:'
    requirements_pattern = r'^\s*-\s*Requirements:'
    processing_time_pattern = r'^\s*-\s*Processing Time:'
    fee_pattern = r'^\s*-\s*Fee:'
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for Institution
        if re.match(inst_pattern, line):
            current_institution = re.sub(inst_pattern, '', line).strip()
            service_hierarchy = []  # Reset hierarchy for new institution
            current_service = None
            
        # Check for regular service (with bullet point)
        elif re.match(service_pattern, line):
            # print("starts with regular service")

            service_name = re.sub(service_pattern, '', line).strip()
            service_hierarchy = [service_name]  # Reset hierarchy to just this service
            current_service = None

        # Check for Sub-Service (any level)
        elif re.match(sub_service_pattern, line):

            # Extract the service name (remove the bullet point and "Sub-Service:" part)
            service_name = re.sub(sub_service_pattern, '', line).strip()
            sub_depth = len(re.findall(r'Sub-', line))  # count "Sub-"

            # Trim or expand hierarchy to correct depth
            service_hierarchy = service_hierarchy[:sub_depth]
            service_hierarchy.append(service_name)

            current_service = None

            
        # Check for attributes (Requirements, Processing Time, Fee)
        elif re.match(requirements_pattern, line) or re.match(processing_time_pattern, line) or re.match(fee_pattern, line):
            # print(current_institution)
            if service_hierarchy and current_institution:
                # Create service name from hierarchy
                full_service_name = ' \\ '.join(service_hierarchy)
                
                # Initialize service if not exists
                if current_service is None:
                    current_service = {
                        'service_name': full_service_name,
                        'institution_name': current_institution,
                        'requirements': '',
                        'processing_time': '',
                        'fee': '',
                        'other': []
                    }
                
                # Extract the attribute value
                if re.match(requirements_pattern, line):
                    current_service['requirements'] = re.sub(requirements_pattern, '', line).strip()
                elif re.match(processing_time_pattern, line):
                    current_service['processing_time'] = re.sub(processing_time_pattern, '', line).strip()
                elif re.match(fee_pattern, line):
                    current_service['fee'] = re.sub(fee_pattern, '', line).strip()
        
        # Check for other attributes (anything that doesn't match the standard ones)
        elif line and not re.match(inst_pattern, line) and not re.match(service_pattern, line) and not re.match(sub_service_pattern, line):
            # print("starts with other")
            # print(line)
            if current_service and line.strip():
                # This is likely an "other" attribute
                current_service['other'].append(line.strip())
        
        # Check if we should finalize the current service
        # This happens when we encounter a new service or reach the end
        if current_service and (
            i == len(lines) - 1 or  # End of document
            (i < len(lines) - 1 and (
                re.match(service_pattern, lines[i + 1].strip()) or
                re.match(sub_service_pattern, lines[i + 1].strip()) or
                re.match(inst_pattern, lines[i + 1].strip())
            ))
        ):
            # Only add services that have at least one of the required attributes
            if current_service['requirements'] or current_service['processing_time'] or current_service['fee']:
                if "other" in current_service and not current_service['other']:
                    del current_service['other']
                    
                services.append(current_service.copy())
            current_service = None
        
        i += 1
    
    # Handle the last service if it exists
    if current_service and (current_service['requirements'] or current_service['processing_time'] or current_service['fee']):
        if "other" in current_service and not current_service['other']:
            del current_service['other']
        services.append(current_service)
    
    return services


def load_services_from_google_doc(url: str) -> List[Dict]:
    """
    Main function to load and parse services from a Google Doc.
    
    Args:
        url (str): Public Google Doc URL
        
    Returns:
        List[Dict]: List of service dictionaries with extracted attributes
    """
    try:
        # Scrape the document content
        content = scrape_google_doc(url)
        # Parse services from content
        services = parse_services(content)
        
        return services
        
    except Exception as e:
        raise Exception(f"Failed to load services from Google Doc: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Example URL - replace with your actual Google Doc URL
    doc_url = "https://docs.google.com/document/d/1dG0pUNLwpZtzo5UhXsyAY7ldNwlYbaUuqbDlomVyjUU/edit"
    
    try:
        services = load_services_from_google_doc(doc_url)
        
        print(f"Found {len(services)} services:")
        for i, service in enumerate(services, 1):
            print(f"\n{i}. {service['service_name']}")
            print(f"   Institution: {service['institution_name']}")
            print(f"   Requirements: {service['requirements']}")
            print(f"   Processing Time: {service['processing_time']}")
            print(f"   Fee: {service['fee']}")
            if "other" in service:
                print(f"   Other: {', '.join(service['other'])}")
                
    except Exception as e:
        print(f"Error: {e}")
