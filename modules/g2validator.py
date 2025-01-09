import json

def g2validator(json_data):
    """
    Validate links in the given JSON data.

    :param json_data: List of dictionaries containing 'title' and 'link'.
    :return: List of links that meet the validation criteria.
    """
    valid_links = []
    for item in json_data:
        link = item.get("link", "")
        # Check if the main domain is 'www.g2.com' and it ends with '/reviews'
        if "www.g2.com" in link and link.endswith("/reviews"):
            valid_links.append(link)
    return valid_links

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
