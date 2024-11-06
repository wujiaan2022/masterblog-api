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
    # Get optional sorting parameters from query string
    sort_by = request.args.get("sort_by")  # e.g., "id", "title", "content"
    order = request.args.get("order", "asc")  # "asc" or "desc", default to "asc"

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
    data = request.get_json()  # Get JSON data from request body

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
    # Find the post by id
    post_to_delete = next((post for post in POSTS if post["id"] == id), None)

    # If post not found, return 404 error
    if post_to_delete is None:
        return jsonify({"error": f"Post with id {id} not found"}), 404

    # If post is found, delete it
    POSTS.remove(post_to_delete)
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200


# PUT endpoint to update a post by id
@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    # Find the post by id
    post_to_update = next((post for post in POSTS if post["id"] == id), None)

    # If post not found, return 404 error
    if post_to_update is None:
        return jsonify({"error": f"Post with id {id} not found"}), 404

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
