#!/usr/bin/env python3
"""Собирает Happ-диплинк из routing_profile.json.

Happ ждёт ссылку вида:  happ://routing/add/<base64(JSON)>
где <base64> — стандартный base64 (с padding) от компактного JSON-профиля.

Использование:
    python3 tools/make_deeplink.py                       # из ../routing_profile.json
    python3 tools/make_deeplink.py path/to/profile.json  # из указанного файла
    python3 tools/make_deeplink.py -o routing_deeplink.txt

Скопируй итоговую строку целиком и открой на устройстве — Happ предложит
добавить профиль маршрутизации.
"""
import argparse
import base64
import json
import os
import sys

PREFIX = "happ://routing/add/"


def build_deeplink(profile_path: str) -> str:
    with open(profile_path, "r", encoding="utf-8") as fh:
        profile = json.load(fh)  # заодно валидируем JSON
    # separators без пробелов после ':' и ',' — так делает сам Happ при экспорте
    raw = json.dumps(profile, ensure_ascii=False).encode("utf-8")
    encoded = base64.b64encode(raw).decode("ascii")
    return PREFIX + encoded


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    default_profile = os.path.join(os.path.dirname(here), "routing_profile.json")

    parser = argparse.ArgumentParser(description="Генератор Happ-диплинка")
    parser.add_argument(
        "profile",
        nargs="?",
        default=default_profile,
        help="путь к routing_profile.json (по умолчанию — в корне репозитория)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="записать диплинк в файл (по умолчанию — печать в stdout)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.profile):
        print(f"Не найден профиль: {args.profile}", file=sys.stderr)
        return 1

    link = build_deeplink(args.profile)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(link + "\n")
        print(f"Диплинк записан в {args.output}")
    else:
        print(link)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
