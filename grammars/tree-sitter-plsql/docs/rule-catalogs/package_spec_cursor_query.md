# Consultas estructuradas en cursores de especificacion de paquete

## Regla y alcance

`cursor_definition` representa `CURSOR nombre [(parametros)] [RETURN tipo] IS SELECT ...;` y la variante cuya consulta comienza con `WITH`. La consulta debe conservar sus nodos `with_clause`, `sql_statement_select`, `order_by_clause` y `ref_call`. El punto y coma cierra el cursor, de modo que la siguiente declaracion del paquete sea un nodo independiente.

La regla se aplica a especificaciones de paquete. Los cuerpos y los bloques PL/SQL conservan su alternativa `legacy_cursor_definition_blob` para consultas heredadas que todavia no se descomponen sin recuperacion; ese token permanece limitado por `;` y se audita por separado.

## Formas cubiertas

- `WITH` con varias subconsultas, `ORDER BY` dentro de una de ellas y `ORDER BY` en el SELECT final.
- Llamadas calificadas dentro de una subconsulta, como `app.workday(1)`.
- Comentarios `--` que contienen `ORDER BY` y `;` sin cerrar la consulta.
- Cursores y declaraciones que siguen a un cursor con `WITH`.
- Consultas con subconsultas escalares y `ORDER BY` final.

No se infiere que un identificador sea una llamada sin parentesis. Los errores de fuente y la validez semantica en Oracle quedan fuera del parser.

## Defecto retirado

`legacy_package_spec_cursor_select_blob` era un token de expresion regular que competia con el SQL estructurado. Podia consumir comentarios con punto y coma y continuar hasta un `ORDER BY` posterior, ocultando cursores, declaraciones y llamadas sin producir `ERROR` ni `MISSING`. Ya no forma parte de la gramatica generada.

## Evidencia

Baseline: commit `d8ce21f37dcfb3bdae4bd53e34fb7bc5cab1635d`, extension publica `FastParser.Language.Plsql 0.1.6`. Corpus: `Package spec cursor with commented order by semicolon` y `Package spec CTE order by keeps calls and following cursor`.

Se analizaron los mismos 11,079 archivos del inventario con la extension publica y con la correccion. Los dos reportes JSON guardan codificacion, hash de fuente, diagnosticos y conteos por archivo.

| Metrica | Antes | Despues |
|---|---:|---:|
| Archivos con `ERROR`/`MISSING` | 0/0 | 0/0 |
| Cursores opacos de especificacion | 26 en 15 archivos | 0 |
| `cursor_definition` | 17,570 | 17,669 |
| `with_clause` | 263 | 289 |
| `ref_call` | 666,623 | 667,214 |

Solo cambiaron esos 15 archivos; ninguno perdio nodos de los tres tipos estructurales. En `PKGCOREBURSATILBETA.pks`, `curConstruyePosicion` vuelve a terminar en la linea 226, las seis llamadas `PkgCoreBursatil.BDiaHabil`/`FHabilProxima` aparecen en las lineas 124, 146, 149, 152, 155 y 158, y los cursores de las lineas 361 y 372 quedan independientes. `curProrrateoPaquete` en `PKGCAPITALES.pks` cubre solo las lineas 677-760.

Los 33 nodos `legacy_cursor_definition_blob` de cuerpos/bloques no cambiaron. Son un limite conocido de estructura, distinto de la regresion de especificaciones de paquete.
