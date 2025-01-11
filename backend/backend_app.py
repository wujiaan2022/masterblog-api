from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import OrderedDict

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve and optionally sort blog posts.

    This endpoint fetches all posts and allows optional sorting by
    specified fields ('id', 'title', 'content'). Sorting order can be
    specified as ascending ('asc') or descending ('desc').

    Query Parameters:
        sort_by (str): The field to sort posts by. Acceptable values are
            'id', 'title', and 'content'. Defaults to None for no sorting.
        order (str): The sorting order, 'asc' for ascending (default) or 'desc'
            for descending.

    Returns:
        Response: A JSON response containing the sorted (or unsorted) list of posts
        with a 200 status code, or a 400 error if invalid parameters are provided.
    """

    # Get optional sorting parameters from query string
    sort_by = request.args.get("sort_by")  
    order = request.args.get("order", "asc") 

    # Validate the sort_by parameter
    if sort_by not in [None, "id", "title", "content"]:
        return jsonify({"error": "Invalid sort_by field. Must be 'id', 'title', or 'content'."}), 400

    # Sort the posts if a valid sort_by field is provided
    if sort_by:
        reverse = (order == "desc")
        try:
            sorted_posts = sorted(POSTS, key=lambda post: post[sort_by], reverse=reverse)
        except KeyError:
            return jsonify({"error": f"Cannot sort by '{sort_by}'. Field does not exist."}), 400
    else:
        # If no sorting is specified, keep the original order
        sorted_posts = POSTS

    # Return the sorted or original list of posts as JSON
    return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Add a new blog post.

    This endpoint allows the addition of a new blog post with a title and content.
    The function validates that both 'title' and 'content' are provided in the 
    request body and assigns a unique ID to each new post.

    Request Body (JSON):
        title (str): The title of the new post.
        content (str): The content of the new post.

    Returns:
        Response: A JSON response containing the new post with its assigned ID and a 201 
        status code if successful. If either 'title' or 'content' is missing, returns a 
        400 error with details of the missing fields.
    """

    # Get JSON data from request body
    data = request.get_json()  
    
    # Check if 'title' and 'content' are in the data
    missing_fields = [field for field in ['title', 'content'] if field not in data]
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    # Generate a new id for the post
    new_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1
    new_post = OrderedDict([
        ("id", new_id),
        ("title", data["title"]),
        ("content", data["content"])
    ])

    POSTS.append(new_post)
    return jsonify(new_post), 201


# DELETE endpoint to delete a post by id
@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    """
    Delete a blog post by ID.

    This endpoint deletes a blog post identified by its unique ID. If the post
    exists, it is removed from the list of posts. If the post with the given
    ID does not exist, a 404 error is returned.

    Path Parameters:
        id (int): The unique identifier of the post to delete.

    Returns:
        Response: A JSON response with a success message and a 200 status code 
        if deletion is successful. If the post is not found, returns a 404 
        error with an appropriate message.
    """

    # Find the post by id
    post_to_delete = next((post for post in POSTS if post["id"] == id), None)
    
    # If post not found, return 404 error
    if post_to_delete is None:
        return jsonify({"error": f"Post with id {id} not found"}), 404

    # If post is found, delete it
    POSTS.remove(post_to_delete)
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200



# PUT endpoint to update a post by post_id
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update a blog post by its ID.

    This endpoint allows updating a blog post's title and content by its unique ID.
    If a post with the specified ID is not found, a 404 error is returned.

    Path Parameters:
        post_id (int): The unique identifier of the post to update.

    Returns:
        Response: A JSON response containing the updated post and a 200 status code
        if successful. If the post is not found, returns a 404 error with an appropriate message.
    """
    # Find the post by post_id
    post_to_update = next((post for post in POSTS if post["id"] == post_id), None)
    
    # If post not found, return 404 error
    if post_to_update is None:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    # Get JSON data from request body
    data = request.get_json()
    
    # Update fields if provided, else keep current values
    title = data.get("title", post_to_update["title"])
    content = data.get("content", post_to_update["content"])
    
    # Update the post in place
    post_to_update["title"] = title
    post_to_update["content"] = content

    # Return the updated post
    updated_post = OrderedDict([
        ("id", post_to_update["id"]),
        ("title", post_to_update["title"]),
        ("content", post_to_update["content"])
    ])
    
    return jsonify(updated_post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for blog posts by title and/or content.

    This endpoint allows searching through posts by title and content keywords.
    The search terms are case-insensitive and optional; if no search term is
    provided, all posts are returned.

    Query Parameters:
        title (str): The title search term.
        content (str): The content search term.

    Returns:
        Response: A JSON response containing a list of filtered posts with a
        200 status code.
    """
    # Get search terms from query parameters
    title_query = request.args.get("title", "").lower()
    content_query = request.args.get("content", "").lower()

    # Filter posts based on title and content queries
    filtered_posts = [
        post for post in POSTS
        if (title_query in post["title"].lower() if title_query else True) and
           (content_query in post["content"].lower() if content_query else True)
    ]

    # Return filtered posts
    return jsonify(filtered_posts), 200



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
