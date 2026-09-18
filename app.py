import os
from flask import Flask, jsonify
import redis

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
APP_ENV = os.getenv("APP_ENV", "production")

# Redis connection
client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD or None,
    decode_responses=True,
)


@app.route("/healthz", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route("/ready", methods=["GET"])
def readiness_check():
    try:
        client.ping()
        return jsonify({"status": "ready", "redis": "connected"}), 200
    except redis.ConnectionError:
        return jsonify({"status": "unready", "redis": "disconnected"}), 503


@app.route("/", methods=["GET"])
def index():
    hits = client.incr("page_views")
    return jsonify(
        {
            "message": "Welcome to the Kubernetes API Project!",
            "environment": APP_ENV,
            "total_views": hits,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)