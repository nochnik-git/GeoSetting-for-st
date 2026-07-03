# GeoSetting-for-st

Кастомные `geosite.dat` / `geoip.dat` и профиль маршрутизации для VPN-клиентов —
под использование в России, с упором на разработку и нейросети.

GitHub Actions собирает обе базы из апстрима
[v2fly](https://github.com/v2fly/domain-list-community) с наложенными
кастомными списками и публикует их в ветку [`release`](../../tree/release).
Клиент загружает базы по URL из профиля.

## Структура

```
data/                      # исходники geosite (формат v2fly domain-list-community)
  category-ai              #   нейросети
  category-dev-proxy       #   dev-сервисы, недоступные из РФ напрямую
  category-direct-extra    #   пакетные реестры и то, что работает напрямую
  category-ru-blocked      #   заблокированные РКН сервисы и соцсети
  category-geoblock-ru     #   сайты, режущие функционал по IP
  whitelist                #   госуслуги, банки, чекеры IP
  win-spy                  #   телеметрия Windows
  torrent                  #   торрент-трекеры и DHT
  twitch-ads               #   реклама Twitch
geoip/config.json          # конфиг сборщика geoip (private, ru, ru-blocked, discord)
.github/workflows/build.yml# сборка обеих баз + публикация в ветку release и релиз-тег
routing_profile.json       # профиль маршрутизации (формат Happ)
routing_deeplink.txt       # диплинк для импорта в один тап
tools/make_deeplink.py     # генератор диплинка из профиля
```

## Маршрутизация

`RouteOrder = block → proxy → direct`. При пересечении списков выигрывает более
ранний уровень.

| Уровень | geosite | geoip |
|---|---|---|
| block | `category-ads`, `win-spy`, `twitch-ads` | — |
| proxy | `category-ai`, `category-dev-proxy`, `category-ru-blocked`, `category-geoblock-ru`, `category-porn`, `youtube`, `telegram`, `google-play` | `ru-blocked`, `discord` |
| direct | `private`, `category-ru`, `whitelist`, `category-direct-extra`, `github`, `microsoft`, `apple`, `steam`, `epicgames`, `riot`, `escapefromtarkov`, `faceit`, `origin`, `twitch`, `pinterest`, `torrent` | `private`, `ru` |

DNS: прокси-трафик — DoH Google, директ — DoH Яндекса. `nalog.ru` задан статикой
в `DnsHosts`.

## Сборка

1. **Actions → «Build geo files» → Run workflow** — первый запуск вручную.
2. Дальше сборка идёт автоматически при изменениях в `data/`/`geoip/` и по
   расписанию (пн и чт).
3. Готовые базы попадают в ветку `release`:

   ```
   https://cdn.jsdelivr.net/gh/nochnik-git/GeoSetting-for-st@release/geosite.dat
   https://cdn.jsdelivr.net/gh/nochnik-git/GeoSetting-for-st@release/geoip.dat
   ```

Эти ссылки уже прописаны в `routing_profile.json` (`Geositeurl` / `Geoipurl`).
Если репозиторий/аккаунт назван иначе — поправь их в профиле (регистр важен для
jsDelivr) и перегенерируй диплинк.

## Использование

- Импортировать `routing_deeplink.txt`, либо вставить `routing_profile.json` на
  [routing.happ.su](https://routing.happ.su/ru).
- После правок профиля пересобрать диплинк:

  ```bash
  python3 tools/make_deeplink.py -o routing_deeplink.txt
  ```

## Редактирование списков

Добавить/убрать домен — правка строки в нужном файле `data/<категория>` и `git push`.
Сборка запустится сама, базы в `release` обновятся.

## Источники

- [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) — база доменных категорий.
- [Loyalsoldier/geoip](https://github.com/Loyalsoldier/geoip) — генератор `geoip.dat`.
- [ipverse/rir-ip](https://github.com/ipverse/rir-ip) — CIDR-диапазоны РФ.
- [1andrevich/Re-filter-lists](https://github.com/1andrevich/Re-filter-lists) — реестр РКН и IP Discord.
- [hydraponique](https://github.com/hydraponique) — списки `whitelist`, `category-geoblock-ru`, `win-spy`, `torrent`, `twitch-ads`.

## Лицензия

[MIT](LICENSE).
