# GeoSetting-for-st

Собственные гео-файлы (`geosite.dat` + `geoip.dat`) и профиль маршрутизации для
[**VPN-клиентов**] — заточенный под жизнь в России, с упором на
**разработку** и **нейросети**.

Репозиторий — это *источник* правил: GitHub Actions собирает `geosite.dat` и
`geoip.dat` из [апстрима v2fly](https://github.com/v2fly/domain-list-community)
с наложенными кастомными списками и публикует их в ветку [`release`](../../tree/release),
откуда Happ забирает их по стабильным ссылкам jsDelivr.

---

## Чем отличается от готовых решений

Референс — репозитории [hydraponique](https://github.com/hydraponique) и
[Loyalsoldier/geoip](https://github.com/Loyalsoldier/geoip). Ключевая разница:

- hydraponique **выбрасывает весь апстрим v2fly** (`rm -rf community/data`) и
  оставляет ~23 своих категории. Здесь наоборот — кастомные списки
  **накладываются поверх полного апстрима**, так что доступны разом и все
  ~1500 категорий v2fly (`geosite:openai`, `geosite:steam`, …), и наши
  тематические (`geosite:category-ai`, `geosite:category-dev-proxy`, …).
- Акцент на **dev/AI**: две большие ручные категории под разработку и нейросети,
  где статусы блокировок выверены на «сейчас».
- Оба `.dat` (site + ip) собираются **одним workflow**, свежие реестр РКН и
  IP Discord подтягиваются автоматически дважды в неделю.

---

## Структура

```
.
├── data/                     # исходники geosite (формат v2fly domain-list-community)
│   ├── category-ai           #   → ПРОКСИ: нейросети (OpenAI, Anthropic, Gemini, Grok, MJ…)
│   ├── category-dev-proxy    #   → ПРОКСИ: dev-вендоры, режущие РФ (Docker, Terraform, Gradle…)
│   ├── category-ru-blocked   #   → ПРОКСИ: заблокированные РКН сервисы и соцсети
│   ├── category-direct-extra #   → ДИРЕКТ: pypi/npm/crates, HuggingFace, зеркала Linux…
│   ├── category-geoblock-ru  #   → ПРОКСИ: сайты, режущие функционал по IP  (© hydraponique)
│   ├── whitelist             #   → ДИРЕКТ: госы, банки, чекеры IP            (© hydraponique)
│   ├── win-spy               #   → БЛОК:   телеметрия Windows                (© hydraponique)
│   ├── torrent               #   → ДИРЕКТ: торрент-трекеры/DHT               (© hydraponique)
│   └── twitch-ads            #   → БЛОК:   реклама Twitch                    (© hydraponique)
├── geoip/
│   └── config.json           # конфиг сборщика Loyalsoldier/geoip (private, ru, ru-blocked, discord)
├── .github/workflows/
│   └── build.yml             # сборка обоих .dat + публикация в ветку release + релиз-тег
├── tools/
│   └── make_deeplink.py      # генератор happ://-диплинка из профиля
├── routing_profile.json      # профиль маршрутизации Happ (правится на routing.happ.su)
└── routing_deeplink.txt      # готовый диплинк (импорт в один тап)
```

---

## Логика маршрутизации

Профиль: `GlobalProxy=true`, `RouteOrder = block → proxy → direct`
(при пересечении списков **выигрывает более ранний** — block важнее proxy,
proxy важнее direct).

| Назначение | geosite | geoip |
|---|---|---|
| **BLOCK** | `category-ads`, `win-spy`, `twitch-ads` | — |
| **PROXY** | `category-ai`, `category-dev-proxy`, `category-ru-blocked`, `category-geoblock-ru`, `category-porn`, `youtube`, `telegram`, `google-play` | `ru-blocked`, `discord` |
| **DIRECT** | `private`, `category-ru`, `whitelist`, `category-direct-extra`, `github`, `microsoft`, `apple`, `steam`, `epicgames`, `riot`, `escapefromtarkov`, `faceit`, `origin`, `twitch`, `pinterest`, `torrent` | `private`, `ru` |

Тонкости, заложенные специально:

- **GitHub — в директ** (как просил), но `geosite:github` включает `github-copilot`,
  а Copilot режет РФ и лежит в `category-ai` (proxy). Поскольку proxy важнее direct,
  сам GitHub идёт напрямую, а Copilot — через прокси. То, что нужно.
- **HuggingFace / DeepSeek — в директ** (`category-direct-extra`), а не в `category-ai`:
  качать модели через прокси больно и незачем.
- **Торренты — в директ, не в блок.** Через прокси их гонять нельзя (забанят сервер),
  а в блоке они просто отвалятся.
- **Discord** — домены в `category-ru-blocked` (proxy), плюс голосовые серверы ходят
  по «чистым» IP без DNS, поэтому `geoip:discord` тоже в `ProxyIp` — иначе звонки
  не заработают.
- **`geoip:ru-blocked` в ProxyIp** — страховка: если РКН-заблокированный ресурс
  резолвится в IP мимо доменных списков, он всё равно уйдёт в прокси.
- **DNS:** для прокси-трафика DoH Google (`8.8.8.8`), для директа DoH Яндекса
  (`77.88.8.8`); `nalog.ru` прибит хардкодом в `DnsHosts` (у них вечные проблемы с резолвом).

---

## Категории под разработку и нейросети

**`category-ai`** (→ прокси). Через `include:` подключены апстрим-списки OpenAI,
Anthropic, Gemini/DeepMind, Perplexity, Poe, GitHub Copilot, Cursor, ElevenLabs;
доменами добавлены Grok/x.ai, Midjourney, Stable Diffusion, Leonardo, Ideogram,
Civitai, Runway, Pika, Luma, HeyGen, Synthesia, Suno, Udio, Mistral, OpenRouter,
Replicate, Together, Groq, Fireworks, Cohere, Fal, Modal, Baseten, Codeium/Windsurf,
Tabnine, Phind, Lovable, Bolt, Character.AI, Jasper, Gamma и др.

**`category-dev-proxy`** (→ прокси) — вендоры, режущие РФ: Docker Hub, HashiCorp/
Terraform, Oracle, Intel, NVIDIA, MongoDB, Atlassian/Bitbucket, Unity, Adobe,
Gradle, Grafana, Elastic, Datadog, Sentry, CircleCI, JFrog, Snyk, Red Hat и др.

**`category-direct-extra`** (→ директ) — то, что из РФ работает и через прокси
гнать глупо: pypi, npm, crates, rubygems, maven, go, nuget, GitLab, Cloudflare,
Vercel, Netlify, Railway, Render, Fly, Supabase, JetBrains, Figma, VS Code,
HuggingFace, DeepSeek, Kaggle, зеркала Arch/Debian/Ubuntu/Fedora, Wikipedia,
Reddit, StackOverflow.

> Статусы блокировок собраны на момент создания и меняются в обе стороны.
> Если сервис заработал/сломался — это правка одной строки в `data/` и `git push`,
> сборка пересоберётся сама.

---

## Как собрать и опубликовать

1. Залей содержимое репозитория на GitHub (публичный репозиторий, чтобы работал jsDelivr).
2. **Actions → «Build geo files» → Run workflow** — первый запуск вручную.
   Дальше workflow сам запускается при пуше в `data/`/`geoip/` и по расписанию
   (пн и чт, 04:00 UTC).
3. Workflow соберёт `geosite.dat` и `geoip.dat`, зальёт их в ветку `release` и
   создаст тег-релиз. Стабильные ссылки:

   ```
   https://cdn.jsdelivr.net/gh/nochnik-git/GeoSetting-for-st@release/geosite.dat
   https://cdn.jsdelivr.net/gh/nochnik-git/GeoSetting-for-st@release/geoip.dat
   ```

> Ссылки в `routing_profile.json` уже указывают на `nochnik-git/GeoSetting-for-st@release`.
> Если репозиторий/аккаунт назван иначе — поправь `Geoipurl`/`Geositeurl` в профиле
> (регистр важен для jsDelivr) и перегенерируй диплинк.

---

## Как подключить в Happ

**Вариант 1 — диплинк (в один тап).** Скопируй строку целиком из
[`routing_deeplink.txt`](routing_deeplink.txt) и открой на устройстве — Happ
предложит добавить профиль.

**Вариант 2 — вручную.** Открой [routing.happ.su](https://routing.happ.su/ru),
вставь `routing_profile.json`, при желании правь списки.

После правки профиля пересобери диплинк:

```bash
python3 tools/make_deeplink.py -o routing_deeplink.txt
```

> Выключи **Per-App Proxy**, если включал: иначе трафик до правил маршрутизации
> просто не дойдёт, и профиль ничего не решит.

---

## Источники данных

- [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) — база доменных категорий (geosite).
- [Loyalsoldier/geoip](https://github.com/Loyalsoldier/geoip) — генератор `geoip.dat`.
- [ipverse/rir-ip](https://github.com/ipverse/rir-ip) — CIDR-диапазоны РФ (`geoip:ru`).
- [1andrevich/Re-filter-lists](https://github.com/1andrevich/Re-filter-lists) — реестр РКН (`geoip:ru-blocked`) и IP Discord (`geoip:discord`).
- [hydraponique](https://github.com/hydraponique) — списки `whitelist`, `category-geoblock-ru`, `win-spy`, `torrent`, `twitch-ads`.

## Лицензия

[MIT](LICENSE). Проприетарные списки доменов принадлежат их авторам (см. «Источники»).
