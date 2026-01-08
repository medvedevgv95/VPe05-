#!/usr/bin/env python3
"""
CLI эмиттер логов для Loki: симуляция криптобиржи
Использование:
    python loki_crypto_emitter.py
    python loki_crypto_emitter.py --loki-url http://89.111.153.43:3100/loki/api/v1/push
"""

import argparse
import time
import random
import requests
from datetime import datetime

# ==============================
# 🔧 Конфигурация
# ==============================

CURRENCIES = ["BTC", "ETH", "SOL", "USDT", "XRP", "DOT", "ADA"]
ACTIONS = ["buy", "sell", "deposit", "withdraw", "login", "api_call", "order_cancel"]
LEVELS = ["info", "warn", "error"]
SERVICES = ["trading-engine", "wallet-service", "auth-service", "market-data", "risk-monitor"]

def send_log_to_loki(loki_url: str, message: str, labels: dict):
    """Отправляет лог в Loki"""
    try:
        timestamp_ns = str(int(time.time() * 1_000_000_000))  # наносекунды
        payload = {
            "streams": [
                {
                    "stream": labels,
                    "values": [[timestamp_ns, message]]
                }
            ]
        }
        response = requests.post(loki_url, json=payload, timeout=5)
        if response.status_code == 204:
            print(f"✅ Отправлено: {message[:60]}...")
        else:
            print(f"⚠️  Ошибка Loki ({response.status_code}) при отправке в {loki_url}")
    except Exception as e:
        print(f"❌ Не удалось отправить в Loki ({loki_url}): {e}")

def generate_log_entry():
    """Генерирует один лог-запись"""
    user_id = f"user_{random.randint(10000, 99999)}"
    currency = random.choice(CURRENCIES)
    action = random.choice(ACTIONS)
    service = random.choice(SERVICES)
    level = random.choices(LEVELS, weights=[12, 3, 1], k=1)[0]

    if action == "login":
        ip = f"192.168.{random.randint(0,255)}.{random.randint(1,254)}"
        message = f"User {user_id} logged in from {ip}"
    elif action in ("buy", "sell"):
        amount = round(random.uniform(0.001, 10.0), random.randint(2, 6))
        price = round(random.uniform(10000, 70000), 2)
        message = f"{action.upper()} {amount} {currency} at ${price:.2f}"
    elif action == "deposit":
        amount = round(random.uniform(50, 20000), 2)
        message = f"Deposit of ${amount} received for {currency}"
    elif action == "withdraw":
        amount = round(random.uniform(30, 10000), 2)
        message = f"Withdrawal of ${amount} initiated for {currency}"
    elif action == "api_call":
        endpoint = random.choice(["/v1/ticker", "/v1/order", "/v1/balance", "/v2/trades"])
        message = f"API call to {endpoint} by {user_id}"
    elif action == "order_cancel":
        order_id = f"ord_{random.randint(100000, 999999)}"
        message = f"Order {order_id} cancelled by {user_id}"
    else:
        message = f"Action '{action}' performed"

    if level == "error":
        reasons = ["Timeout", "Insufficient balance", "Invalid API key", "Rate limit", "Network failure"]
        message = f"ERROR: {message} | {random.choice(reasons)}"

    labels = {
        "service": service,
        "level": level,
        "currency": currency,
        "user_id": user_id,
        "action": action
    }

    return message, labels

def main():
    parser = argparse.ArgumentParser(description="Эмиттер логов криптобиржи в Loki")
    parser.add_argument(
        "--loki-url",
        default="http://89.111.153.43:3100/loki/api/v1/push",  # ✅ ИСПРАВЛЕНО: дефолт — ваш сервер
        help="URL эндпоинта Loki (по умолчанию: http://89.111.153.43:3100/loki/api/v1/push)"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=3.0,
        help="Интервал между логами в секундах (по умолчанию: 3.0)"
    )
    parser.add_argument(
        "--max-logs",
        type=int,
        default=0,
        help="Макс. число логов (0 = бесконечно, по умолчанию: 0)"
    )
    args = parser.parse_args()

    print(f"🚀 Запуск эмиттера логов...")
    print(f"   Loki URL: {args.loki_url}")
    print(f"   Интервал: {args.interval} сек")
    print(f"   Макс. логов: {'бесконечно' if args.max_logs == 0 else args.max_logs}")
    print("-" * 50)

    log_count = 0
    try:
        while True:
            message, labels = generate_log_entry()
            send_log_to_loki(args.loki_url, message, labels)
            log_count += 1

            if args.max_logs > 0 and log_count >= args.max_logs:
                print(f"✅ Отправлено {log_count} логов. Завершение.")
                break

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\n🛑 Остановлено пользователем. Всего отправлено: {log_count} логов.")

if __name__ == "__main__":
    main()