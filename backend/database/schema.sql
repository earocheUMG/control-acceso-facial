-- =============================================
-- SISTEMA DE CONTROL DE ACCESO FACIAL
-- Esquema inicial
-- =============================================

CREATE TABLE viviendas (
    id BIGSERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    direccion TEXT,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE personas (
    id BIGSERIAL PRIMARY KEY,
    codigo_biometrico VARCHAR(20) UNIQUE,
    nombre_completo VARCHAR(150) NOT NULL,

    tipo VARCHAR(20) NOT NULL
        CHECK (
            tipo IN (
                'RESIDENTE',
                'TRABAJADOR',
                'SEGURIDAD'
            )
        ),

    email VARCHAR(150),
    telefono VARCHAR(30),

    activo BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_inicio DATE,
    fecha_fin DATE,

    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE persona_vivienda (
    id BIGSERIAL PRIMARY KEY,

    persona_id BIGINT NOT NULL
        REFERENCES personas(id),

    vivienda_id BIGINT NOT NULL
        REFERENCES viviendas(id),

    relacion VARCHAR(20) NOT NULL
        CHECK (
            relacion IN (
                'RESIDENTE',
                'TRABAJADOR'
            )
        ),

    es_responsable_notificacion BOOLEAN
        NOT NULL DEFAULT FALSE,

    activo BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_inicio DATE,
    fecha_fin DATE,

    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (
        persona_id,
        vivienda_id,
        relacion
    )
);

CREATE TABLE biometria (
    id BIGSERIAL PRIMARY KEY,

    persona_id BIGINT NOT NULL UNIQUE
        REFERENCES personas(id),

    modelo VARCHAR(50)
        NOT NULL DEFAULT 'MobileFaceNet',

    template_path TEXT NOT NULL,

    cantidad_muestras INTEGER
        NOT NULL DEFAULT 10,

    activo BOOLEAN
        NOT NULL DEFAULT TRUE,

    creado_en TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);

CREATE TABLE puntos_acceso (
    id BIGSERIAL PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,

    ubicacion VARCHAR(150),

    activo BOOLEAN
        NOT NULL DEFAULT TRUE,

    creado_en TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);

CREATE TABLE accesos (
    id BIGSERIAL PRIMARY KEY,

    persona_id BIGINT
        REFERENCES personas(id),

    punto_acceso_id BIGINT NOT NULL
        REFERENCES puntos_acceso(id),

    fecha_hora TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    resultado VARCHAR(20) NOT NULL
        CHECK (
            resultado IN (
                'AUTORIZADO',
                'RECHAZADO',
                'REVISION'
            )
        ),

    similitud NUMERIC(7,5),

    metodo VARCHAR(40)
        NOT NULL DEFAULT 'RECONOCIMIENTO_FACIAL',

    puerta_abierta BOOLEAN
        NOT NULL DEFAULT FALSE,

    motivo TEXT,

    captura_path TEXT
);

CREATE TABLE notificaciones (
    id BIGSERIAL PRIMARY KEY,

    acceso_id BIGINT NOT NULL
        REFERENCES accesos(id),

    destinatario_email VARCHAR(150)
        NOT NULL,

    tipo VARCHAR(30) NOT NULL
        CHECK (
            tipo IN (
                'INGRESO',
                'ALERTA_SEGURIDAD'
            )
        ),

    estado VARCHAR(20) NOT NULL
        DEFAULT 'PENDIENTE'
        CHECK (
            estado IN (
                'PENDIENTE',
                'ENVIADA',
                'ERROR'
            )
        ),

    creado_en TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    enviado_en TIMESTAMPTZ,

    error TEXT
);

CREATE TABLE usuarios_sistema (
    id BIGSERIAL PRIMARY KEY,

    usuario VARCHAR(50)
        NOT NULL UNIQUE,

    password_hash TEXT
        NOT NULL,

    rol VARCHAR(20) NOT NULL
        CHECK (
            rol IN (
                'ADMIN',
                'SEGURIDAD'
            )
        ),

    activo BOOLEAN
        NOT NULL DEFAULT TRUE,

    creado_en TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_accesos_fecha
ON accesos(fecha_hora);

CREATE INDEX idx_accesos_persona
ON accesos(persona_id);

CREATE INDEX idx_persona_vivienda_persona
ON persona_vivienda(persona_id);

CREATE INDEX idx_persona_vivienda_vivienda
ON persona_vivienda(vivienda_id);

CREATE INDEX idx_notificaciones_estado
ON notificaciones(estado);