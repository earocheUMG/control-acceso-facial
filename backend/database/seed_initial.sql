BEGIN;

-- =============================================
-- 1. VIVIENDA DE PRUEBA
-- =============================================

INSERT INTO viviendas (
    codigo,
    direccion
)
VALUES (
    'CASA-001',
    'Vivienda de prueba'
)
ON CONFLICT (codigo)
DO UPDATE SET
    direccion = EXCLUDED.direccion;


-- =============================================
-- 2. PERSONA 001
-- =============================================

INSERT INTO personas (
    codigo_biometrico,
    nombre_completo,
    tipo,
    activo
)
VALUES (
    '001',
    'Eduardo Aroche',
    'RESIDENTE',
    TRUE
)
ON CONFLICT (codigo_biometrico)
DO UPDATE SET
    nombre_completo = EXCLUDED.nombre_completo,
    tipo = EXCLUDED.tipo,
    activo = EXCLUDED.activo;


-- =============================================
-- 3. PERSONA 002
-- IMPORTANTE:
-- Cambia NOMBRE PERSONA 002 por el nombre real
-- antes de ejecutar el script.
-- =============================================

INSERT INTO personas (
    codigo_biometrico,
    nombre_completo,
    tipo,
    activo
)
VALUES (
    '002',
    'Esther Flores',
    'RESIDENTE',
    TRUE
)
ON CONFLICT (codigo_biometrico)
DO UPDATE SET
    nombre_completo = EXCLUDED.nombre_completo,
    tipo = EXCLUDED.tipo,
    activo = EXCLUDED.activo;


-- =============================================
-- 4. VINCULAR 001 CON LA VIVIENDA
-- =============================================

INSERT INTO persona_vivienda (
    persona_id,
    vivienda_id,
    relacion,
    es_responsable_notificacion
)
SELECT
    p.id,
    v.id,
    'RESIDENTE',
    TRUE
FROM personas p
JOIN viviendas v
    ON v.codigo = 'CASA-001'
WHERE p.codigo_biometrico = '001'
ON CONFLICT (
    persona_id,
    vivienda_id,
    relacion
)
DO UPDATE SET
    activo = TRUE;


-- =============================================
-- 5. VINCULAR 002 CON LA VIVIENDA
-- =============================================

INSERT INTO persona_vivienda (
    persona_id,
    vivienda_id,
    relacion,
    es_responsable_notificacion
)
SELECT
    p.id,
    v.id,
    'RESIDENTE',
    FALSE
FROM personas p
JOIN viviendas v
    ON v.codigo = 'CASA-001'
WHERE p.codigo_biometrico = '002'
ON CONFLICT (
    persona_id,
    vivienda_id,
    relacion
)
DO UPDATE SET
    activo = TRUE;


-- =============================================
-- 6. BIOMETRÍA 001
-- =============================================

INSERT INTO biometria (
    persona_id,
    modelo,
    template_path,
    cantidad_muestras
)
SELECT
    id,
    'MobileFaceNet',
    'data/templates/001.npy',
    10
FROM personas
WHERE codigo_biometrico = '001'
ON CONFLICT (persona_id)
DO UPDATE SET
    modelo = EXCLUDED.modelo,
    template_path = EXCLUDED.template_path,
    cantidad_muestras = EXCLUDED.cantidad_muestras,
    activo = TRUE;


-- =============================================
-- 7. BIOMETRÍA 002
-- =============================================

INSERT INTO biometria (
    persona_id,
    modelo,
    template_path,
    cantidad_muestras
)
SELECT
    id,
    'MobileFaceNet',
    'data/templates/002.npy',
    10
FROM personas
WHERE codigo_biometrico = '002'
ON CONFLICT (persona_id)
DO UPDATE SET
    modelo = EXCLUDED.modelo,
    template_path = EXCLUDED.template_path,
    cantidad_muestras = EXCLUDED.cantidad_muestras,
    activo = TRUE;


-- =============================================
-- 8. PUNTO DE ACCESO
-- =============================================

INSERT INTO puntos_acceso (
    nombre,
    ubicacion
)
SELECT
    'Entrada principal',
    'Acceso principal de la vivienda'
WHERE NOT EXISTS (
    SELECT 1
    FROM puntos_acceso
    WHERE nombre = 'Entrada principal'
);

COMMIT;