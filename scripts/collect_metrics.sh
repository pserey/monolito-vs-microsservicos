#!/usr/bin/env bash
set -euo pipefail

# ========= EDIT THESE =========
PROM_URL="http://localhost:9090"      # Prometheus endpoint (keep port-forward running)
NAMESPACE="default"
DEPLOYMENT="onlineboutique-monolith-de619ee0-658ecc47"
HPA_NAME="onlineboutique-monolith-de619ee0-658ecc47"
OUT_DIR="./metrics_run"
SCRAPE_WINDOW="5m"                     # same window you tested with
# ==============================

mkdir -p "$OUT_DIR"

ts_now() { date -u +%s; }
append_csv() { local f="$1" h="$2" r="$3"; [[ -s "$f" ]] || echo "$h" > "$f"; [[ -n "$r" ]] && echo "$r" >> "$f"; }
fetch_prom() {
  local q="$1" tag="${2:-debug}"
  local url="${PROM_URL}/api/v1/query?query=$(printf %s "$q" | jq -sRr @uri)"
  local out; out="$(curl -fsS "$url")" || { echo "curl failed for $tag" >&2; echo "{}"; return; }
  echo "$out" > "${OUT_DIR}/_last_${tag}.json"
  echo "$out"
}

NOW="$(ts_now)"

# ---------------- CPU (Deployment) ----------------
# Primary: raw cadvisor (this is what returned a value in your curl)
POD_REGEX="^${DEPLOYMENT}-.*"
CPU_DEPLOY_PRIMARY='sum( rate(container_cpu_usage_seconds_total{pod=~"'"$POD_REGEX"'"}['"$SCRAPE_WINDOW"']) )'

# Secondary (fallback): owner-join (may be empty in some setups)
CPU_Q=$(cat <<'PROM'
sum by (namespace, deployment) (
  (
    sum by (namespace, pod) (
      rate(container_cpu_usage_seconds_total[%SCRAPE_WINDOW%])
    )
  * on (namespace, pod) group_left(owner_name)
    kube_pod_owner{owner_kind="ReplicaSet"}
  * on (namespace, owner_name) group_left(deployment)
    kube_replicaset_owner
  )
)
PROM
)
CPU_Q="${CPU_Q//%SCRAPE_WINDOW%/$SCRAPE_WINDOW}"
CPU_FILTER='kube_deployment_spec_replicas{namespace="'"$NAMESPACE"'",deployment="'"$DEPLOYMENT"'"}'
CPU_DEPLOY_SECONDARY="(${CPU_Q}) and on (namespace, deployment) (${CPU_FILTER})"

echo "[1/4] CPU cores (deployment)"
CPU_JSON="$(fetch_prom "$CPU_DEPLOY_PRIMARY" "cpu_deploy_primary")"
CPU_VAL="$(jq -r '.data.result[0].value[1] // empty' <<< "$CPU_JSON")"
if [[ -z "$CPU_VAL" ]]; then
  CPU_JSON="$(fetch_prom "$CPU_DEPLOY_SECONDARY" "cpu_deploy_secondary")"
  CPU_VAL="$(jq -r '.data.result[0].value[1] // empty' <<< "$CPU_JSON")"
fi
append_csv "${OUT_DIR}/cpu_deployment.csv" "timestamp,cores" "${NOW},${CPU_VAL}"

# ---------------- HPA (max / desired / current) ----------------
HPA_MAX_Q='kube_horizontalpodautoscaler_spec_max_replicas{namespace="'$NAMESPACE'",horizontalpodautoscaler="'$HPA_NAME'"}'
HPA_DES_Q='kube_horizontalpodautoscaler_status_desired_replicas{namespace="'$NAMESPACE'",horizontalpodautoscaler="'$HPA_NAME'"}'
HPA_CUR_Q='kube_horizontalpodautoscaler_status_current_replicas{namespace="'$NAMESPACE'",horizontalpodautoscaler="'$HPA_NAME'"}'

echo "[2/4] HPA replicas (max/desired/current)"
HPA_MAX_JSON="$(fetch_prom "$HPA_MAX_Q" "hpa_max")"
HPA_DES_JSON="$(fetch_prom "$HPA_DES_Q" "hpa_desired")"
HPA_CUR_JSON="$(fetch_prom "$HPA_CUR_Q" "hpa_current")"

HPA_MAX_VAL="$(jq -r '.data.result[0].value[1] // empty' <<< "$HPA_MAX_JSON")"
HPA_DES_VAL="$(jq -r '.data.result[0].value[1] // empty' <<< "$HPA_DES_JSON")"
HPA_CUR_VAL="$(jq -r '.data.result[0].value[1] // empty' <<< "$HPA_CUR_JSON")"

append_csv "${OUT_DIR}/hpa_max.csv"     "timestamp,max_replicas"     "${NOW},${HPA_MAX_VAL}"
append_csv "${OUT_DIR}/hpa_desired.csv" "timestamp,desired_replicas" "${NOW},${HPA_DES_VAL}"
append_csv "${OUT_DIR}/hpa_current.csv" "timestamp,current_replicas" "${NOW},${HPA_CUR_VAL}"

# ---------------- CPU per pod (drill-down) ----------------
# Same raw cadvisor approach, per pod
CPU_POD_Q='sum by (pod) ( rate(container_cpu_usage_seconds_total{pod=~"'"$POD_REGEX"'"}['"$SCRAPE_WINDOW"']) )'
echo "[3/4] CPU per pod (optional)"
CPU_POD_JSON="$(fetch_prom "$CPU_POD_Q" "cpu_pod")"
[[ -s "${OUT_DIR}/cpu_pod_long.csv" ]] || echo "timestamp,pod,cores" > "${OUT_DIR}/cpu_pod_long.csv"
jq -r --arg ts "$NOW" '
  .data.result[]? as $s
  | ($s.metric.pod // empty) as $pod
  | ($s.value[1] // empty) as $val
  | select($pod != "" and $val != "")
  | "\($ts),\($pod),\($val)"
' <<< "$CPU_POD_JSON" >> "${OUT_DIR}/cpu_pod_long.csv"

echo "[4/4] Done. Appended to:"
ls -1 "${OUT_DIR}"