# Auditoria de cursores de especificacion de paquete

## Causa y correccion

La extension publica `FastParser.Language.Plsql 0.1.6` usaba `legacy_package_spec_cursor_select_blob` en ciertos cursores con `WITH` y `ORDER BY`. El token podia abarcar declaraciones posteriores y devolver cero `ERROR`/`MISSING` mientras ocultaba llamadas. Se retiro esa alternativa de la especificacion de paquete. `cursor_definition` y las reglas SQL existentes descomponen los mismos archivos sin agregar reglas lexicales nuevas.

Baseline de codigo: commit `d8ce21f37dcfb3bdae4bd53e34fb7bc5cab1635d`. La extension publica 0.1.6 y el candidato se analizaron con los mismos bytes de los 11,079 archivos de `parser_lab_inventory.sqlite`, convertidos a UTF-8 en memoria cuando correspondia. Los 11,079 SHA-256 del inventario coincidieron en ambas corridas; 9,780 fuentes ya eran UTF-8 y 1,299 se decodificaron con Windows-1252.

| Metrica | 0.1.6 | Candidato |
|---|---:|---:|
| Fallos de ejecucion | 0 | 0 |
| Archivos con `ERROR` | 0 | 0 |
| Nodos `ERROR` | 0 | 0 |
| Nodos `MISSING` | 0 | 0 |
| Bytes de error | 0 | 0 |
| Cursores opacos de especificacion | 26 en 15 archivos | 0 |
| `cursor_definition` | 17,570 | 17,669 |
| `with_clause` | 263 | 289 |
| `ref_call` | 666,623 | 667,214 |

Solo esos 15 archivos cambiaron en los conteos auditados. Ninguno perdio `cursor_definition`, `with_clause` ni `ref_call`; los incrementos son 99, 26 y 591 respectivamente. Permanecen 33 `legacy_cursor_definition_blob` en 20 archivos de otros contextos, sin cambios en esta ronda.

## Reproducciones

- `monex/pks/PKGCOREBURSATILBETA.pks`: `curConstruyePosicion` ahora ocupa lineas 114-226; antes se extendia hasta la 414. Reaparecen `PkgCoreBursatil.BDiaHabil` en 124 y `PkgCoreBursatil.FHabilProxima` en 146, 149, 152, 155 y 158. `curCbEmisora` y `curCbEmisoraPrecio` son nodos separados en 361-369 y 372-384.
- `monex/pks/PKGCAPITALES.pks`: `curProrrateoPaquete` es un `cursor_definition` de lineas 677-760. El archivo recupera cuatro definiciones y 32 llamadas.
- Fixture del assessment `nuget-016-opaque-cursor.sql`: el cursor principal deja de absorber los cursores posteriores; los nodos `ref_call` son visibles.

Pruebas: `tree-sitter generate`, `tree-sitter test --rebuild` (170/170), prueba nativa de FastParse, auditoria binaria MessagePack con 8 hilos, y candidato local `FastParser.Language.Plsql 0.1.7-candidate` validado desde un consumidor C# con `FastParser 0.1.4`. La prueba de paquete exige dos cursores y las dos llamadas internas, ademas de cero diagnosticos.

Datos: [baseline](cursor_inventory_0_1_6_before_20260930.json) y [candidato](cursor_inventory_candidate_20260930.json). Ambos son JSON compactos por archivo; no se conservaron AST completos ni copias normalizadas de los fuentes. El parser generado y el corpus quedan en el repositorio; el commit baseline conserva el estado anterior.

Limite: cero `ERROR` no certifica equivalencia semantica con Oracle. La auditoria demuestra los nodos recuperados y la ausencia de regresiones en los contadores medidos, no la correccion de todos los extractores que consumen esos nodos.
