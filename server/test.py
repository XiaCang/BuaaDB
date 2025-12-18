import requests
import random
import string
import time

# 配置基础 URL
BASE_URL = "http://127.0.0.1:5000/api"

def get_random_string(length=6):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def register_and_login(prefix):
    """注册并登录一个用户，返回 token 和 用户名"""
    username = f"{prefix}_{get_random_string()}"
    password = "password123"
    print(f"👤 正在创建用户: {username} ...")
    
    # 注册
    requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    # 登录
    resp = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    return resp.json().get("token"), username

def run_interaction_test():
    print("====== 开始社交互动模块测试 ======\n")
    
    # 1. 准备角色：卖家 (Seller) 和 互动的买家 (Buyer)
    seller_token, seller_name = register_and_login("seller")
    buyer_token, buyer_name = register_and_login("buyer")
    
    seller_headers = {"Authorization": seller_token}
    buyer_headers = {"Authorization": buyer_token}

    # 2. 卖家先发布一个商品
    print(f"\n📦 {seller_name} 发布商品中...")
    p_resp = requests.post(f"{BASE_URL}/create_product", headers=seller_headers, json={
        "name": "测试互动的商品",
        "price": 100,
        "image_url": "test.png",
        "description": "快来评论收藏我"
    })
    product_id = p_resp.json().get("product_id")
    print(f"✅ 商品发布成功 ID: {product_id}")

    # ==========================================
    # 测试 A: 评论 (Comment)
    # ==========================================
    print("\n💬 [测试 A] 买家正在发表评论...")
    comment_resp = requests.post(f"{BASE_URL}/publish_comment", headers=buyer_headers, json={
        "product_id": product_id,
        "content": "这个东西真的好用吗？",
        "rate": 5
    })
    if comment_resp.status_code == 201:
        print("✅ 评论发布成功")
    else:
        print(f"❌ 评论失败: {comment_resp.text}")

    # 验证评论是否存在
    print("   🔍 正在验证评论列表...")
    comments = requests.get(f"{BASE_URL}/get_comments/{product_id}").json().get("comments", [])
    if len(comments) > 0 and comments[0]['content'] == "这个东西真的好用吗？":
        print(f"   ✅ 验证通过: 查到了 {buyer_name} 的评论")
    else:
        print("   ❌ 验证失败: 没查到评论")


    # ==========================================
    # 测试 B: 收藏 (Favorite)
    # ==========================================
    print("\n❤️ [测试 B] 买家正在收藏商品...")
    fav_resp = requests.post(f"{BASE_URL}/favorite_product/{product_id}", headers=buyer_headers)
    if fav_resp.status_code == 200:
        print("✅ 收藏操作成功")
    else:
        print(f"❌ 收藏失败: {fav_resp.text}")

    # 验证收藏列表
    print("   🔍 正在查看买家的收藏夹...")
    favs = requests.get(f"{BASE_URL}/get_favorites", headers=buyer_headers).json().get("favorites", [])
    # 检查刚才收藏的商品ID是否在列表里
    is_fav = any(f['product_id'] == product_id for f in favs)
    if is_fav:
        print(f"   ✅ 验证通过: 商品已在收藏夹中")
    else:
        print("   ❌ 验证失败: 收藏夹里没找到该商品")


    # ==========================================
    # 测试 C: 私信 (Message)
    # ==========================================
    print("\nwmv [测试 C] 买家给卖家发送私信...")
    msg_resp = requests.post(f"{BASE_URL}/send_msg", headers=buyer_headers, json={
        "receiver_id": seller_name, # 注意：这里是发给卖家
        "content": "老板，可以便宜点吗？"
    })
    if msg_resp.status_code == 201:
        print("✅ 私信发送成功")
    else:
        print(f"❌ 发送失败: {msg_resp.text}")

    # 验证：切换到卖家视角，看能不能收到消息
    print(f"   🔍 正在登录卖家账号 ({seller_name}) 查看收件箱...")
    msgs = requests.get(f"{BASE_URL}/get_msgs", headers=seller_headers).json().get("messages", [])
    
    # 检查是否有那条消息
    has_msg = any(m['content'] == "老板，可以便宜点吗？" for m in msgs)
    if has_msg:
        print(f"   ✅ 验证通过: 卖家成功收到了私信")
    else:
        print("   ❌ 验证失败: 收件箱里没有这条消息")

if __name__ == "__main__":
    try:
        run_interaction_test()
    except Exception as e:
        print(f"\n❌ 测试脚本出错: {e}")
        print("请检查 Flask 是否正在运行，或者 interaction.py 是否已注册到 app.py")