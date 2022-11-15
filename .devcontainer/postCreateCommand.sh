pip install -e /workspaces/dispatch
npm install --prefix /workspaces/dispatch/src/dispatch/static/dispatch

export LOG_LEVEL="ERROR"
export STATIC_DIR=""
export DATABASE_HOSTNAME="localhost"
export DATABASE_CREDENTIALS="dispatch:dispatch"
export DISPATCH_ENCRYPTION_KEY="NJHDWDJ3PbHT8h"
export DISPATCH_JWT_SECRET="foo"
dispatch database restore --dump-file /workspaces/dispatch/data/dispatch-sample-data.dump
dispatch database upgrade
