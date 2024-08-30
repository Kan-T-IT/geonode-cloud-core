#!/bin/bash

# Ejecutar el script adicional
/usr/src/geonode/entrypoint.sh

CELERY_BIN=${CELERY_BIN:-"$(which celery||echo celery)"}
CELERY_APP=${CELERY_APP:-"geonode.celery_app:app"}
CELERY_STATE_DB=${CELERY_STATE_DB:-"/mnt/volumes/statics/worker@%h.state"}
CELERY_MAX_MEMORY_PER_CHILD=${CELERY_MAX_MEMORY_PER_CHILD:-"200000"}
CELERY_AUTOSCALE_VALUES=${CELERY_AUTOSCALE_VALUES:-"15,10"}
CELERY_MAX_TASKS_PER_CHILD=${CELERY_MAX_TASKS_PER_CHILD:-"10"}
CELERY_OPTS=${CELERY_OPTS:-"--without-gossip --without-mingle -Ofair -E"}
CELERY_BEAT_SCHEDULE=${CELERY_BEAT_SCHEDULE:-"celery.beat:PersistentScheduler"}
CELERY_LOG_LEVEL=${CELERY_LOG_LEVEL:-"INFO"}
CELERY_LOG_FILE=${CELERY_LOG_FILE:-"/var/log/celery.log"}
CELERY_WORKER_NAME=${CELERY_WORKER_NAME:-"worker1@%h"}
CELERY_WORKER_CONCURRENCY=${CELERY_WORKER_CONCURRENCY:-"4"}

echo "-----------------------------------------------------"
echo "Start celery beat"
echo "-----------------------------------------------------"

nohup ${CELERY_BIN} -A ${CELERY_APP} beat \
    --statedb=${CELERY_STATE_DB} \
    --scheduler=${CELERY_BEAT_SCHEDULE} \
    --loglevel="DEBUG" -f ${CELERY_LOG_FILE} &>/dev/null &

echo "-----------------------------------------------------"
echo "Start celery worker"
echo "-----------------------------------------------------"

nohup ${CELERY_BIN} -A ${CELERY_APP}  worker --autoscale=${CELERY_AUTOSCALE_VALUES} \
    --max-memory-per-child=${CELERY_MAX_MEMORY_PER_CHILD} ${CELERY_OPTS} \
    --statedb=${CELERY_STATE_DB} --scheduler=${CELERY_BEAT_SCHEDULE} \
    --loglevel=${CELERY_LOG_LEVEL} -n ${CELERY_WORKER_NAME} -f ${CELERY_LOG_FILE} \
    --concurrency=${CELERY_WORKER_CONCURRENCY} --max-tasks-per-child=${CELERY_MAX_TASKS_PER_CHILD} &>/dev/null &

echo "-----------------------------------------------------"
echo "Start celery flower"
echo "-----------------------------------------------------"

nohup ${CELERY_BIN} -A ${CELERY_APP}  --broker=${BROKER_URL} flower --auto_refresh=True --debug=False --basic_auth=${ADMIN_USERNAME}:${ADMIN_PASSWORD} --address=0.0.0.0 --port=5555 &>/dev/null &

# Mantener el contenedor en ejecución
tail -f /dev/null