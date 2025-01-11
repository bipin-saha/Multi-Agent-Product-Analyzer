import json

def g2validator(json_data):
    """
    Validate links in the given JSON data.

    :param json_data: List of dictionaries containing 'title' and 'link'.
    :return: List of links that meet the validation criteria.
    """
    try:
        valid_links = []
        for item in json_data:
            link = item.get("link", "")
            # Check if the main domain is 'www.g2.com' and it ends with '/reviews'
            if "www.g2.com" in link and link.endswith("/reviews"):
                valid_links.append(link)
                return valid_links
            else:
                return "No valid G2 links found."
    
    except Exception as e:
        return f"An error occurred: {str(e)}"
    

def crunchbaseValidator(json_data):
    """
    Validate Crunchbase links in the given JSON data.

    :param json_data: List of dictionaries containing 'title' and 'link'.
    :return: List of links that meet the validation criteria.
    """
    try:
        valid_links = []
        for item in json_data:
            link = item.get("link", "")
            # Check if the link starts with 'https://www.crunchbase.com/organization/'
            if link.startswith("https://www.crunchbase.com/organization/"):
                valid_links.append(link)
        
        if valid_links:
            return valid_links
        else:
            return "No valid Crunchbase links found."
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

# # Example JSON input
# json_input = [
#     {
#         "title": "Jira Reviews from January 2025 - G2",
#         "link": "https://www.g2.com/products/jira/reviews"
#     },
#     {
#         "title": "IGT JIRA I2B: Log in",
#         "link": "https://jira.g2-networks.net/"
#     },
#     {
#         "title": "Jira Service Management Reviews 2025 - G2",
#         "link": "https://www.g2.com/products/jira-service-management/reviews"
#     },
#     {
#         "title": "Jira – G2 – Atlassian",
#         "link": "https://atlassian.gedos.es/category/jira/"
#     },
#     {
#         "title": "16 Best Scrum Tools for Different Types of Scrum Teams ...",
#         "link": "https://geekbot.com/blog/scrum-tools/"
#     }
# ]

# # Validate the links
# result = g2validator(json_input)
# print(result)
