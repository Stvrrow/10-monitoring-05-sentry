#!/usr/bin/env python3
"""Отправка тестовых событий в Sentry. DSN берётся из переменной окружения SENTRY_DSN."""
import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    environment="homework",
    release="netology-sentry@1.0.0",
    traces_sample_rate=1.0,  # транзакции тоже уходят в Sentry (лимит Free — 10k)
    integrations=[LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)],
)
sentry_sdk.set_user({"id": "42", "username": "student"})
sentry_sdk.set_tag("homework", "10-monitoring-05")


def divide(a, b):
    return a / b


with sentry_sdk.start_transaction(op="task", name="homework-run"):
    # 1. необработанное деление на ноль, пойманное и отправленное вручную
    try:
        divide(1, 0)
    except ZeroDivisionError as e:
        sentry_sdk.capture_exception(e)

    # 2. сообщение с уровнем warning и дополнительным контекстом
    sentry_sdk.set_context("order", {"id": 1001, "amount": 250})
    sentry_sdk.capture_message("Order total looks suspicious", level="warning")

    # 3. logging.error превращается в событие через LoggingIntegration
    logging.info("breadcrumb: about to read config")  # попадёт в breadcrumbs
    logging.error("Config file not found: /etc/app.yml")

    # 4. KeyError с другим тегом
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("component", "billing")
        try:
            {}["missing_key"]
        except KeyError as e:
            sentry_sdk.capture_exception(e)

sentry_sdk.flush()
print("events sent")
