import os

admin_token = os.getenv("ADMIN_TOKEN")
print(f"{admin_token = !r}")

webhook_secret = os.getenv("WEBHOOK_SECRET")
assert webhook_secret, "env var WEBHOOK_SECRET is not set"
webhook_path = f"/tg/wh{webhook_secret}"
print(f"{webhook_path = !r}")

bot_token = os.getenv("TG_BOT_TOKEN")
assert bot_token, "env var TG_BOT_TOKEN is not set"
bot_url = f"https://api.telegram.org/bot{bot_token}"
print(f"{bot_url = !r}")


class Settings:
    admin_token = admin_token
    bot_token = bot_token
    bot_url = bot_url
    webhook_path = webhook_path
    webhook_secret = webhook_secret


settings = Settings()