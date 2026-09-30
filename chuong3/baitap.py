from flask import Flask, request, url_for
app = Flask(__name__)
POSTS = [
    {
        "id": 1,
        "title": "Chào Flask",
        "author": "an",
        "content": "Flask là một micro-framework...",
        "created": "2026-09-01"
    }
]
@app.route("/posts/<int:post_id>")
def xem_bai_viet(post_id):
    post = find_post(post_id)
    if post:
        return f"Tiêu đề: {post['title']}<br>Tác giả: {post['author']}<br>Nội dung: {post['content']}<br>Ngày tạo: {post['created']}"
    else:
        return "Bài viết không tồn tại"
    return f"""
    <h1>Tiêu đề: {post['title']}</h1>
    <p>Tác giả: {post['author']}</p>
    <p>Nội dung: {post['content']}</p>
    <p>Ngày tạo: {post['created']}</p>
    """
def find_post(post_id):
    for post in POSTS:
        if post["id"] == post_id:
            return post
    return None
if __name__ == '__main__':
    app.run(debug=True)