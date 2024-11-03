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
    ordered_posts = [
        OrderedDict([
            ("id", post["id"]),
            ("title", post["title"]),
            ("content", post["content"])
        ])
        for post in POSTS
    ]
    return app.response_class(
        response=json.dumps(ordered_posts, indent=4),
        status=200,
        mimetype='application/json'
    )


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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)