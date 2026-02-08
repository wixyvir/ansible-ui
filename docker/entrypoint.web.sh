#!/bin/sh
set -e

cat > /var/www/html/frontend/config.js <<EOF
window.ANSIBEAU_CONFIG = {
  backendUri: "${BACKEND_URI:-}"
};
EOF

exec nginx -g 'daemon off;'
