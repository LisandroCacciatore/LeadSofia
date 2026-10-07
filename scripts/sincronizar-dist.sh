#!/usr/bin/env bash
# Sincroniza la distribucion (skill) desde el motor, que es la fuente.
#
# El motor (~/motor-leads) es la plantilla viva; la skill de distribucion y el
# perfil instalado del bot son copias. Cuando divergen, los leads nuevos salen
# con un motor viejo: paso ya (los 5 scripts del estandar no llegaban al lead).
#
# Uso:  bash sincronizar-dist.sh            # muestra que haria
#       bash sincronizar-dist.sh --aplicar  # lo hace
set -u

M="/c/Users/Torso/motor-leads"
S="/c/Users/Torso/dist-auditor/skills/auditoria-propuesta"
# LOCALAPPDATA viene con barras invertidas (C:\Users\...): bash no las traga.
LA="$(printf '%s' "$LOCALAPPDATA" | tr '\\' '/')"
P="$LA/hermes/profiles/auditor/skills/auditoria-propuesta"
APLICAR=0
[ "${1:-}" = "--aplicar" ] && APLICAR=1

hacer() {  # hacer <descripcion> <comando...>
  local desc="$1"; shift
  if [ "$APLICAR" = "1" ]; then
    echo "  ✔ $desc"
    "$@" >/dev/null 2>&1 || echo "      ⚠ fallo: $*"
  else
    echo "  · $desc"
  fi
}

sync_destino() {  # sync_destino <raiz-de-la-skill>
  local D="$1"
  echo "--- $D ---"
  hacer "scripts/*.py y *.sh ($(ls "$M"/scripts/*.py "$M"/scripts/*.sh | wc -l) archivos)" \
        cp -f "$M"/scripts/*.py "$M"/scripts/*.sh "$D/scripts/"
  rm -f "$D"/scripts/*.pyc 2>/dev/null
  rm -rf "$D"/scripts/__pycache__ 2>/dev/null
  hacer "templates/ → plantilla/templates/"       cp -f "$M"/templates/* "$D/plantilla/templates/"
  hacer "brand/ completo (incluye assets/fonts)"  cp -rf "$M"/brand "$D/plantilla/"
  hacer ".github/ → plantilla/.github/"           cp -rf "$M"/.github "$D/plantilla/"
  hacer ".gitignore → plantilla/"                 cp -f "$M"/.gitignore "$D/plantilla/"
  # Las .md y el config.ejemplo van a references/, que es donde la skill los lee.
  # entrada-del-cliente.md es propio de la skill: no se toca.
  hacer "SPEC-*.md → references/"  cp -f "$M"/SPEC-editorial.md "$M"/SPEC-workflow-audit-propuesta.md "$D/references/"
  hacer "config.ejemplo.json → references/"       cp -f "$M"/config.ejemplo.json "$D/references/"
}

echo "=== sincronizar distribucion desde el motor ==="
[ "$APLICAR" = "1" ] && echo "MODO: aplicar" || echo "MODO: dry-run (agregá --aplicar)"
echo
sync_destino "$S"
echo
sync_destino "$P"

if [ "$APLICAR" = "1" ]; then
  echo
  echo "=== verificacion posterior ==="
  echo "scripts en la skill: $(ls "$S/scripts" | wc -l)"
  echo "scripts en el perfil: $(ls "$P/scripts" | wc -l)"
  echo "fuentes en el brand: $(ls "$S/plantilla/brand/assets/fonts" 2>/dev/null | wc -l)"
  echo "--- quedan diferencias script por script? ---"
  dif=0
  for f in "$M"/scripts/*; do
    n=$(basename "$f")
    [ -d "$f" ] && continue          # __pycache__ y compañía no son scripts
    case "$n" in *.pyc) continue ;; esac
    [ -f "$S/scripts/$n" ] || { echo "  FALTA $n"; dif=$((dif+1)); continue; }
    diff -q "$f" "$S/scripts/$n" >/dev/null || { echo "  DISTINTO $n"; dif=$((dif+1)); }
  done
  [ "$dif" = "0" ] && echo "  ninguno: la skill reproduce el motor script por script"
fi
