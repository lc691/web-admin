#!/usr/bin/env bash
#
# restore_static_v3.sh
#
# Restore seluruh vendor static project
# Aman dijalankan berkali-kali
#

set -Eeuo pipefail

ROOT="/opt/web-admin/static"

echo
echo "============================================="
echo " Restore Static Assets v3"
echo "============================================="
echo

##############################################################################
# UTIL
##############################################################################

need() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "ERROR: '$1' belum terinstall."
        exit 1
    }
}

need curl
need git

mkdir -p "$ROOT"

download() {

    local url="$1"
    local file="$2"

    mkdir -p "$(dirname "$file")"

    if [ -f "$file" ]; then
        echo "✓ $(realpath --relative-to="$ROOT" "$file")"
        return
    fi

    echo "↓ $(realpath --relative-to="$ROOT" "$file")"

    curl \
        --fail \
        --location \
        --silent \
        --show-error \
        "$url" \
        -o "$file"
}

##############################################################################
# STRUKTUR
##############################################################################

echo "== Membuat Struktur =="

mkdir -p "$ROOT/bootstrap/css"
mkdir -p "$ROOT/bootstrap/js"

mkdir -p "$ROOT/tabler/css"
mkdir -p "$ROOT/tabler/js"
mkdir -p "$ROOT/tabler/icons"

mkdir -p "$ROOT/vendor"

mkdir -p "$ROOT/vendor/apexcharts"
mkdir -p "$ROOT/vendor/chartjs"
mkdir -p "$ROOT/vendor/datatables/css"
mkdir -p "$ROOT/vendor/datatables/js"
mkdir -p "$ROOT/vendor/htmx"
mkdir -p "$ROOT/vendor/jquery"
mkdir -p "$ROOT/vendor/popper"
mkdir -p "$ROOT/vendor/select2"
mkdir -p "$ROOT/vendor/moment"
mkdir -p "$ROOT/vendor/luxon"

mkdir -p "$ROOT/fontawesome"

mkdir -p "$ROOT/css"
mkdir -p "$ROOT/js"
mkdir -p "$ROOT/img"
mkdir -p "$ROOT/fonts"

##############################################################################
# BOOTSTRAP
##############################################################################

echo
echo "== Bootstrap =="

download \
https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css \
$ROOT/bootstrap/css/bootstrap.min.css

download \
https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js \
$ROOT/bootstrap/js/bootstrap.bundle.min.js

##############################################################################
# TABLER
##############################################################################

echo
echo "== Tabler =="

download \
https://cdn.jsdelivr.net/npm/@tabler/core@latest/dist/css/tabler.min.css \
$ROOT/tabler/css/tabler.min.css

download \
https://cdn.jsdelivr.net/npm/@tabler/core@latest/dist/js/tabler.min.js \
$ROOT/tabler/js/tabler.min.js

##############################################################################
# TABLER ICONS
##############################################################################

echo
echo "== Tabler Icons =="

TMP=$(mktemp -d)

git clone \
    --depth=1 \
    https://github.com/tabler/tabler-icons.git \
    "$TMP/icons" >/dev/null 2>&1

mkdir -p "$ROOT/tabler/icons"

cp \
"$TMP/icons/packages/icons-webfont/dist/tabler-icons.min.css" \
"$ROOT/tabler/icons/" || true

cp -R \
"$TMP/icons/packages/icons-webfont/dist/fonts" \
"$ROOT/tabler/icons/" || true

rm -rf "$TMP"

##############################################################################
# FONT AWESOME
##############################################################################

echo
echo "== Font Awesome =="

if [ ! -d "$ROOT/fontawesome/css" ]; then

TMP=$(mktemp -d)

git clone \
    --depth=1 \
    https://github.com/FortAwesome/Font-Awesome.git \
    "$TMP/fa" >/dev/null 2>&1

cp -R "$TMP/fa/css" "$ROOT/fontawesome/"
cp -R "$TMP/fa/js" "$ROOT/fontawesome/"
cp -R "$TMP/fa/webfonts" "$ROOT/fontawesome/"
cp -R "$TMP/fa/svgs" "$ROOT/fontawesome/"
cp -R "$TMP/fa/sprites" "$ROOT/fontawesome/"
cp -R "$TMP/fa/metadata" "$ROOT/fontawesome/"

rm -rf "$TMP"

else

echo "✓ Font Awesome"

fi

##############################################################################
# JQUERY
##############################################################################

echo
echo "== jQuery =="

download \
https://code.jquery.com/jquery-3.7.1.min.js \
$ROOT/vendor/jquery/jquery.min.js

##############################################################################
# POPPER
##############################################################################

echo
echo "== Popper =="

download \
https://cdn.jsdelivr.net/npm/@popperjs/core@2/dist/umd/popper.min.js \
$ROOT/vendor/popper/popper.min.js

##############################################################################
# HTMX
##############################################################################

echo
echo "== HTMX =="

download \
https://unpkg.com/htmx.org/dist/htmx.min.js \
$ROOT/vendor/htmx/htmx.min.js

##############################################################################
# DATATABLES
##############################################################################

echo
echo "== DataTables =="

download \
https://cdn.datatables.net/2.3.2/css/dataTables.dataTables.min.css \
$ROOT/vendor/datatables/css/dataTables.dataTables.min.css

download \
https://cdn.datatables.net/2.3.2/js/dataTables.min.js \
$ROOT/vendor/datatables/js/dataTables.min.js

##############################################################################
# SELECT2
##############################################################################

echo
echo "== Select2 =="

download \
https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css \
$ROOT/vendor/select2/select2.min.css

download \
https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js \
$ROOT/vendor/select2/select2.min.js

##############################################################################
# APEXCHARTS
##############################################################################

echo
echo "== ApexCharts =="

download \
https://cdn.jsdelivr.net/npm/apexcharts/dist/apexcharts.min.js \
$ROOT/vendor/apexcharts/apexcharts.min.js

##############################################################################
# CHART.JS
##############################################################################

echo
echo "== Chart.js =="

download \
https://cdn.jsdelivr.net/npm/chart.js/dist/chart.umd.min.js \
$ROOT/vendor/chartjs/chart.umd.min.js

##############################################################################
# MOMENT
##############################################################################

echo
echo "== Moment =="

download \
https://cdn.jsdelivr.net/npm/moment/min/moment.min.js \
$ROOT/vendor/moment/moment.min.js

##############################################################################
# LUXON
##############################################################################

echo
echo "== Luxon =="

download \
https://cdn.jsdelivr.net/npm/luxon/build/global/luxon.min.js \
$ROOT/vendor/luxon/luxon.min.js

##############################################################################
# FAVICON
##############################################################################

echo
echo "== Favicon =="

if [ ! -f "$ROOT/favicon.ico" ]; then

touch "$ROOT/favicon.ico"

fi

##############################################################################

echo
echo "============================================="
echo " Vendor selesai dipulihkan"
echo "============================================="
echo

tree -L 3 "$ROOT"

echo
echo "============================================="
echo " File custom yang masih harus dipulihkan:"
echo
echo "static/css/*.css"
echo "static/js/*.js"
echo "============================================="