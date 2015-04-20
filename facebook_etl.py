__author__ = 'eliashussen'
from facepy import GraphAPI

# Initialize the Graph API with a valid access token (optional,
# but will allow you to do all sorts of fun stuff).
graph = GraphAPI(oauth_access_token)

# Get my latest posts
graph.get('me/posts')

# Post a photo of a parrot
graph.post(
    path = 'me/photos',
    source = open('parrot.jpg', 'rb')
)