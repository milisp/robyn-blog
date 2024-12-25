from robyn import Request, Robyn

from database import BlogPost, Session, User
from security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

app = Robyn(__file__)
session = Session()


# Helper 函数：获取并验证 Token
def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        return None, {"status": "error", "message": "请提供认证令牌"}

    decoded = decode_access_token(token)
    if not decoded:
        return None, {"status": "error", "message": "认证失败"}

    user_id = decoded.get("user_id")
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return None, {"status": "error", "message": "用户不存在"}

    return user, None


# 注册用户
@app.post("/register")
async def register(request: Request):
    data = request.json()
    username = data.get("username")
    password = data.get("password")

    if session.query(User).filter_by(username=username).first():
        return {"status": "error", "message": "用户已存在"}

    hashed_password = hash_password(password)
    user = User(username=username, password=hashed_password)
    session.add(user)
    session.commit()
    return {"status": "success", "message": "注册成功"}


# 登录用户
@app.post("/login")
async def login(request: Request):
    data = request.json()
    username = data.get("username")
    password = data.get("password")

    user = session.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.password):
        return {"status": "error", "message": "用户名或密码错误"}

    token = create_access_token({"user_id": user.id})
    return {"status": "success", "token": token}


# 获取文章（分页）
@app.get("/posts")
async def get_posts(request: Request):
    page = int(request.query_params.get("page", "1"))
    per_page = int(request.query_params.get("per_page", "5"))

    posts = session.query(BlogPost).offset((page - 1) * per_page).limit(per_page).all()
    return [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author": post.author.username,
        }
        for post in posts
    ]


@app.get("/posts/:post_id")
async def get_post(request: Request):
    post_id = int(request.path_params["post_id"])
    post = session.query(BlogPost).filter_by(id=post_id).first()
    if not post:
        return {"status": "error", "message": "文章不存在或无权限"}
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": post.author.username,
    }


@app.post("/posts")
async def create_post(request: Request):
    user, error = get_current_user(request)
    if error:
        return error

    data = request.json
    title = data.get("title")
    content = data.get("content")

    post = BlogPost(title=title, content=content, author_id=user.id)
    session.add(post)
    session.commit()
    return {"status": "success", "message": "文章创建成功"}


@app.put("/posts/:post_id")
async def update_post(request: Request):
    user, error = get_current_user(request)
    if error:
        return error

    data = request.json()
    post_id = int(request.path_params["post_id"])
    post = session.query(BlogPost).filter_by(id=post_id, author_id=user.id).first()
    if not post:
        return {"status": "error", "message": "文章不存在或无权限"}

    post.title = data.get("title", post.title)
    post.content = data.get("content", post.content)
    session.commit()
    return {"status": "success", "message": "文章更新成功"}


@app.delete("/posts/:post_id")
async def delete_post(request: Request):
    user, error = get_current_user(request)
    if error:
        return error

    post_id = int(request.path_params["post_id"])
    post = session.query(BlogPost).filter_by(id=post_id, author_id=user.id).first()
    if not post:
        return {"status": "error", "message": "文章不存在或无权限"}

    session.delete(post)
    session.commit()
    return {"status": "success", "message": "文章删除成功"}


if __name__ == "__main__":
    app.start()
