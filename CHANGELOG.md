# Change Log

## Kan GeoNode 4.0.2.0

### Install GeoNode MapStore Client as a Submodule requirement.
- Make GeoNode to avoid using `django-geonode-mapstore-client` python module.
- Make GeoNode to import [GeoNode MapStore Client](https://git.kan.com.ar/kan/geoexpressportal/geonode-mapstore-client) as submodule.
- Make GeoNode MapStore Client submodule build with GeoNode.

### Create dinamics submodules import capability.
- Added `EXTRA_CONTRIB_APPS` and `EXTRA_CONTRIB_URLS` fields to `.env.sample`.
- Modify `./geonode/settings.py` to load `EXTRA_CONTRIB_APPS` from `os.environ` in runtime.
- Modify `./geonode/urls.py` to load `EXTRA_CONTRIB_URLS` from `os.environ` in runtime.

### Added GeoNode LogStash Contrib
- Added GeoNode LogStash Contrib as requirement.
- Enable capability to use custom data types for logstash in `./geonode/settings.py`.

### Add Flower integration
- Add Flower python module to `./requirements.txt`
- Add Flower integration to the custom `./entrypoint-celery.sh`.

### Fix dead Celery schedule
- Add custom `./entrypoint-celery.sh`.
- Change `./Dockerfile` and `./docker-compose.yml` to use the new entrypoint.

### Add VectorTiles plugin for GeoServer
- Add community VectorTiles plugin `.jar` files.
- Create new `./Dockerfile-vectortiles`  to always build GeoServer with VectorTiles plugin.
- Modify `./docker-compose.yml` to use `./Dockerfile-vectortiles`.

### Add ArgenMap optional use as basemap
- Add ArgenMap statics.
- Create `USE_ARGENMAP_BASE_MAP` variable in `.env.sample` toogle ArgenMap usage.
- Modify `./geonode/settings.py` to load `USE_ARGENMAP_BASE_MAP` from `os.environ` in runtime.

## [Original GeoNode/geonode 4.0.2 changelog](https://github.com/GeoNode/geonode/blob/4.2.4/CHANGELOG.md) (2022-12-20)