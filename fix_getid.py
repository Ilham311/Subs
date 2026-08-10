with open("plugins/getid.py", "r") as f:
    content = f.read()

content = content.replace(
    '_id += "<b>👤 User ID</b>: <code>{message.from_user.id}</code>"',
    '_id += f"<b>👤 User ID</b>: <code>{message.from_user.id}</code>"',
)

with open("plugins/getid.py", "w") as f:
    f.write(content)
