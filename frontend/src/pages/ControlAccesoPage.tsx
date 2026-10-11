import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  apiFetch
} from "../services/api";


interface RecognitionPerson {
  id: number;
  codigo_biometrico: string;
  nombre_completo: string;
  tipo: string;
}


interface RecognitionResponse {
  estado:
    | "SIN_ROSTRO"
    | "MULTIPLES_ROSTROS"
    | "SIN_BIOMETRIAS"
    | "RECONOCIDO"
    | "DESCONOCIDO";

  autorizado: boolean;

  similitud: number | null;

  threshold: number;

  persona:
    RecognitionPerson
    | null;
}


interface NotificationResult {
  enviadas: number;
  errores: number;
  detalle?: string;
}


interface AccessEventResponse {
  evento_registrado: boolean;

  acceso_id: number;

  resultado:
    | "AUTORIZADO"
    | "RECHAZADO";

  puerta_abierta: boolean;

  puerta_abierta_segundos: number;

  evidencia: string | null;

  reconocimiento:
    RecognitionResponse;

  notificaciones:
    NotificationResult;
}


interface AccessDecision {
  accessId: number;

  autorizado: boolean;

  resultado:
    | "AUTORIZADO"
    | "RECHAZADO";

  persona:
    RecognitionPerson
    | null;

  similitud:
    number | null;

  evidence:
    string | null;

  notifications:
    NotificationResult;
}


const REQUIRED_CONFIRMATIONS = 5;

const REQUIRED_MISSING_FRAMES = 15;


function ControlAccesoPage() {

  // ==========================================
  // REFERENCIAS DE CAMARA
  // ==========================================

  const videoRef =
    useRef<HTMLVideoElement | null>(
      null
    );


  const canvasRef =
    useRef<HTMLCanvasElement | null>(
      null
    );


  const streamRef =
    useRef<MediaStream | null>(
      null
    );


  const processingRef =
    useRef(false);


  // ==========================================
  // CONTROL DEL RECONOCIMIENTO
  // ==========================================

  const pendingIdentityRef =
    useRef<string | null>(
      null
    );


  const consecutiveRef =
    useRef(0);


  const decisionLockedRef =
    useRef(false);


  const eventProcessingRef =
    useRef(false);


  const missingFramesRef =
    useRef(0);


  const doorTimerRef =
    useRef<number | null>(
      null
    );


  // ==========================================
  // ESTADOS
  // ==========================================

  const [
    cameraReady,
    setCameraReady
  ] = useState(false);


  const [
    recognitionActive,
    setRecognitionActive
  ] = useState(true);


  const [
    result,
    setResult
  ] = useState<RecognitionResponse | null>(
    null
  );


  const [
    error,
    setError
  ] = useState<string | null>(
    null
  );


  const [
    confirmationCount,
    setConfirmationCount
  ] = useState(0);


  const [
    missingFrames,
    setMissingFrames
  ] = useState(0);


  const [
    accessDecision,
    setAccessDecision
  ] = useState<AccessDecision | null>(
    null
  );


  const [
    doorOpen,
    setDoorOpen
  ] = useState(false);


  const [
    eventProcessing,
    setEventProcessing
  ] = useState(false);


  // ==========================================
  // REINICIAR CONFIRMACION
  // ==========================================

  const resetConfirmation =
    () => {

      pendingIdentityRef.current =
        null;


      consecutiveRef.current =
        0;


      setConfirmationCount(
        0
      );

    };


  // ==========================================
  // REARMAR SISTEMA
  // ==========================================

  const rearmSystem =
    () => {

      decisionLockedRef.current =
        false;


      eventProcessingRef.current =
        false;


      missingFramesRef.current =
        0;


      setMissingFrames(
        0
      );


      setAccessDecision(
        null
      );


      setDoorOpen(
        false
      );


      setEventProcessing(
        false
      );


      resetConfirmation();

    };


  // ==========================================
  // CAMARA
  // ==========================================

  useEffect(() => {

    let cancelled = false;


    const startCamera =
      async () => {

        try {

          const stream =
            await navigator
              .mediaDevices
              .getUserMedia(
                {
                  video: {
                    facingMode:
                      "user",

                    width: {
                      ideal: 1280,
                    },

                    height: {
                      ideal: 720,
                    },
                  },

                  audio: false,
                }
              );


          if (cancelled) {

            stream
              .getTracks()
              .forEach(
                (track) =>
                  track.stop()
              );

            return;

          }


          streamRef.current =
            stream;


          const video =
            videoRef.current;


          if (!video) {
            return;
          }


          video.srcObject =
            stream;


          await video.play();


          if (!cancelled) {

            setCameraReady(
              true
            );


            setError(
              null
            );

          }


        } catch (err) {

          if (
            !cancelled
            &&
            err instanceof Error
          ) {

            setError(
              "No fue posible abrir "
              + "la cámara. "
              + err.message
            );

          }

        }

      };


    void startCamera();


    return () => {

      cancelled = true;


      streamRef.current
        ?.getTracks()
        .forEach(
          (track) =>
            track.stop()
        );


      streamRef.current =
        null;


      if (
        doorTimerRef.current
        !== null
      ) {

        window.clearTimeout(
          doorTimerRef.current
        );

      }

    };

  }, []);


  // ==========================================
  // CAPTURA DE FRAME
  // ==========================================

  const captureFrame =
    async (): Promise<Blob | null> => {

      const video =
        videoRef.current;


      const canvas =
        canvasRef.current;


      if (
        !video
        ||
        !canvas
        ||
        video.videoWidth === 0
        ||
        video.videoHeight === 0
      ) {

        return null;

      }


      canvas.width =
        video.videoWidth;


      canvas.height =
        video.videoHeight;


      const context =
        canvas.getContext(
          "2d"
        );


      if (!context) {
        return null;
      }


      context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
      );


      return await new Promise<
        Blob | null
      >(
        (resolve) => {

          canvas.toBlob(
            resolve,
            "image/jpeg",
            0.85
          );

        }
      );

    };


  // ==========================================
  // PROCESAR EVENTO REAL
  // ==========================================

  const processAccessEvent =
    async (
      frame: Blob
    ) => {

      if (
        eventProcessingRef.current
      ) {

        return;

      }


      eventProcessingRef.current =
        true;


      setEventProcessing(
        true
      );


      setError(
        null
      );


      try {

        const formData =
          new FormData();


        formData.append(
          "imagen",
          frame,
          "access_event.jpg"
        );


        const response =
          await apiFetch(
            "http://127.0.0.1:8000/api/control-acceso/procesar-evento",
            {
              method: "POST",

              body:
                formData,
            }
          );


        const data =
          await response.json();


        if (!response.ok) {

          throw new Error(
            typeof data.detail
            === "string"
              ? data.detail
              : (
                  "No fue posible "
                  + "registrar el acceso."
                )
          );

        }


        const event =
          data as AccessEventResponse;


        const decision:
          AccessDecision = {

            accessId:
              event.acceso_id,

            autorizado:
              event.resultado
              === "AUTORIZADO",

            resultado:
              event.resultado,

            persona:
              event
                .reconocimiento
                .persona,

            similitud:
              event
                .reconocimiento
                .similitud,

            evidence:
              event.evidencia,

            notifications:
              event.notificaciones,
          };


        setAccessDecision(
          decision
        );


        // ====================================
        // PUERTA
        // ====================================

        if (
          event.puerta_abierta
        ) {

          setDoorOpen(
            true
          );


          if (
            doorTimerRef.current
            !== null
          ) {

            window.clearTimeout(
              doorTimerRef.current
            );

          }


          doorTimerRef.current =
            window.setTimeout(
              () => {

                setDoorOpen(
                  false
                );


                doorTimerRef.current =
                  null;

              },
              event
                .puerta_abierta_segundos
              * 1000
            );

        } else {

          setDoorOpen(
            false
          );

        }


      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        }


        // Si el backend rechaza el evento,
        // permitimos intentar nuevamente.

        decisionLockedRef.current =
          false;


        resetConfirmation();


      } finally {

        eventProcessingRef.current =
          false;


        setEventProcessing(
          false
        );

      }

    };


  // ==========================================
  // PROCESAR RESPUESTA DE RECONOCIMIENTO
  // ==========================================

  const processRecognition =
    (
      recognition:
        RecognitionResponse,

      frame:
        Blob
    ) => {

      // ======================================
      // SISTEMA BLOQUEADO
      // ======================================

      if (
        decisionLockedRef.current
      ) {

        if (
          recognition.estado
          === "SIN_ROSTRO"
        ) {

          missingFramesRef.current +=
            1;


          setMissingFrames(
            missingFramesRef.current
          );


          if (
            missingFramesRef.current
            >= REQUIRED_MISSING_FRAMES
            &&
            !eventProcessingRef.current
          ) {

            rearmSystem();

          }

        } else {

          missingFramesRef.current =
            0;


          setMissingFrames(
            0
          );

        }


        return;

      }


      // ======================================
      // SIN ROSTRO
      // ======================================

      if (
        recognition.estado
        === "SIN_ROSTRO"
      ) {

        resetConfirmation();

        return;

      }


      // ======================================
      // MULTIPLES ROSTROS
      // ======================================

      if (
        recognition.estado
        === "MULTIPLES_ROSTROS"
      ) {

        resetConfirmation();

        return;

      }


      // ======================================
      // SIN BIOMETRIAS
      // ======================================

      if (
        recognition.estado
        === "SIN_BIOMETRIAS"
      ) {

        resetConfirmation();

        return;

      }


      // ======================================
      // IDENTIDAD
      // ======================================

      let identity:
        string;


      if (
        recognition.estado
        === "RECONOCIDO"
        &&
        recognition.persona
      ) {

        identity =
          `PERSONA-${recognition.persona.id}`;

      } else {

        identity =
          "DESCONOCIDO";

      }


      // ======================================
      // CONFIRMACION CONSECUTIVA
      // ======================================

      if (
        pendingIdentityRef.current
        === identity
      ) {

        consecutiveRef.current +=
          1;

      } else {

        pendingIdentityRef.current =
          identity;


        consecutiveRef.current =
          1;

      }


      setConfirmationCount(
        consecutiveRef.current
      );


      // ======================================
      // 5/5
      // ======================================

      if (
        consecutiveRef.current
        >= REQUIRED_CONFIRMATIONS
      ) {

        // Bloqueamos inmediatamente para
        // impedir eventos duplicados.

        decisionLockedRef.current =
          true;


        resetConfirmation();


        void processAccessEvent(
          frame
        );

      }

    };


  // ==========================================
  // RECONOCIMIENTO CONTINUO
  // ==========================================

  useEffect(() => {

    if (
      !cameraReady
      ||
      !recognitionActive
    ) {

      return;

    }


    let cancelled = false;


    const recognize =
      async () => {

        if (
          cancelled
          ||
          processingRef.current
        ) {

          return;

        }


        processingRef.current =
          true;


        try {

          const frame =
            await captureFrame();


          if (!frame) {
            return;
          }


          const formData =
            new FormData();


          formData.append(
            "imagen",
            frame,
            "frame.jpg"
          );


          const response =
            await apiFetch(
              "http://127.0.0.1:8000/api/control-acceso/reconocer",
              {
                method:
                  "POST",

                body:
                  formData,
              }
            );


          const data =
            await response.json();


          if (!response.ok) {

            throw new Error(
              typeof data.detail
              === "string"
                ? data.detail
                : (
                    "Error de "
                    + "reconocimiento."
                  )
            );

          }


          if (!cancelled) {

            const recognition =
              data as RecognitionResponse;


            setResult(
              recognition
            );


            setError(
              null
            );


            processRecognition(
              recognition,
              frame
            );

          }


        } catch (err) {

          if (
            !cancelled
            &&
            err instanceof Error
          ) {

            setError(
              err.message
            );

          }


        } finally {

          processingRef.current =
            false;

        }

      };


    const interval =
      window.setInterval(
        () => {

          void recognize();

        },
        900
      );


    return () => {

      cancelled = true;


      window.clearInterval(
        interval
      );

    };

  }, [
    cameraReady,
    recognitionActive
  ]);


  // ==========================================
  // TITULO
  // ==========================================

  const statusTitle =
    () => {

      if (
        eventProcessing
      ) {

        return (
          "REGISTRANDO ACCESO"
        );

      }


      if (
        accessDecision
      ) {

        return (
          accessDecision.autorizado
            ? "ACCESO AUTORIZADO"
            : "ACCESO RECHAZADO"
        );

      }


      if (!result) {

        return (
          "ESPERANDO ROSTRO"
        );

      }


      switch (
        result.estado
      ) {

        case "RECONOCIDO":

          return (
            "ROSTRO DETECTADO"
          );


        case "DESCONOCIDO":

          return (
            "ROSTRO NO IDENTIFICADO"
          );


        case "MULTIPLES_ROSTROS":

          return (
            "MÚLTIPLES ROSTROS"
          );


        case "SIN_BIOMETRIAS":

          return (
            "SIN BIOMETRÍAS"
          );


        default:

          return (
            "ESPERANDO ROSTRO"
          );

      }

    };


  // ==========================================
  // PERSONA MOSTRADA
  // ==========================================

  const displayedPerson =
    accessDecision?.persona
    ??
    result?.persona
    ??
    null;


  // ==========================================
  // SIMILITUD MOSTRADA
  // ==========================================

  const displayedSimilarity =
    accessDecision
      ? accessDecision.similitud
      : result?.similitud
        ?? null;


  return (

    <>

      <header className="topbar">

        <div>

          <h2>
            Control de acceso
          </h2>

          <p>
            Reconocimiento facial
            en tiempo real
          </p>

        </div>


        <button
          type="button"
          className={
            recognitionActive
              ? "danger-button"
              : "primary-button"
          }
          disabled={
            eventProcessing
          }
          onClick={
            () => {

              setRecognitionActive(
                (current) =>
                  !current
              );


              rearmSystem();

            }
          }
        >

          {
            recognitionActive
              ? "Detener reconocimiento"
              : "Iniciar reconocimiento"
          }

        </button>

      </header>


      {error && (

        <div className="error-message">
          {error}
        </div>

      )}


      <section className="control-access-grid">


        {/* ===================================
            CAMARA
        ==================================== */}

        <div className="control-camera-panel">

          <div className="control-camera">

            <video
              ref={
                videoRef
              }
              className="control-video"
              autoPlay
              muted
              playsInline
            />


            {!cameraReady && (

              <div className="camera-loading">

                Iniciando cámara...

              </div>

            )}


            <div
              className={
                accessDecision
                  ?.autorizado
                  ? "face-guide recognized"
                  : accessDecision
                    ? "face-guide rejected"
                    : "face-guide"
              }
            />

          </div>


          <canvas
            ref={
              canvasRef
            }
            className="hidden-canvas"
          />


          <div className="control-camera-footer">

            <span className="status-dot" />

            {
              recognitionActive
                ? "Reconocimiento activo"
                : "Reconocimiento detenido"
            }

          </div>

        </div>


        {/* ===================================
            RESULTADO
        ==================================== */}

        <div
          className={
            accessDecision
              ?.autorizado
              ? "recognition-result authorized"
              : accessDecision
                ? "recognition-result rejected"
                : "recognition-result"
          }
        >


          <div className="recognition-state">

            {
              eventProcessing
                ? "…"
                : accessDecision
                    ?.autorizado
                  ? "✓"
                  : accessDecision
                    ? "✕"
                    : "◎"
            }

          </div>


          <h3>
            {statusTitle()}
          </h3>


          {
            displayedPerson
            ? (

              <>

                <div className="recognized-person">

                  {
                    displayedPerson
                      .nombre_completo
                  }

                </div>


                <div className="recognized-code">

                  Código:{" "}

                  {
                    displayedPerson
                      .codigo_biometrico
                  }

                </div>


                <div className="recognized-type">

                  {
                    displayedPerson
                      .tipo
                  }

                </div>

              </>

            )
            : (

              <p className="recognition-help">

                {
                  eventProcessing
                    ? (
                      "Registrando el evento "
                      + "y procesando "
                      + "notificaciones..."
                    )
                    : accessDecision
                      ? (
                        "La persona no está "
                        + "registrada "
                        + "en el sistema."
                      )
                      : result?.estado
                        === "MULTIPLES_ROSTROS"
                        ? (
                          "Debe aparecer "
                          + "solamente una "
                          + "persona frente "
                          + "a la cámara."
                        )
                        : (
                          "Coloque su rostro "
                          + "frente a la cámara."
                        )
                }

              </p>

            )
          }


          {
            displayedSimilarity
            !== null
            && (

              <div className="recognition-metric">

                <span>
                  Similitud
                </span>

                <strong>

                  {
                    displayedSimilarity
                      .toFixed(4)
                  }

                </strong>

              </div>

            )
          }


          {/* =================================
              CONFIRMACION
          ================================== */}

          {
            !accessDecision
            &&
            !eventProcessing
            &&
            confirmationCount > 0
            && (

              <div className="recognition-confirmation">

                Confirmando identidad

                <strong>

                  {
                    confirmationCount
                  }
                  /
                  {
                    REQUIRED_CONFIRMATIONS
                  }

                </strong>

              </div>

            )
          }


          {/* =================================
              ID DEL EVENTO
          ================================== */}

          {
            accessDecision
            && (

              <div className="recognition-confirmation">

                Evento registrado

                <strong>

                  Acceso #
                  {
                    accessDecision
                      .accessId
                  }

                </strong>

              </div>

            )
          }


          {/* =================================
              PUERTA
          ================================== */}

          {
            accessDecision
              ?.autorizado
            && (

              <div
                className={
                  doorOpen
                    ? "door-status open"
                    : "door-status closed"
                }
              >

                {
                  doorOpen
                    ? "🔓 PUERTA ABIERTA"
                    : "🔒 PUERTA CERRADA"
                }

              </div>

            )
          }


          {/* =================================
              NOTIFICACIONES
          ================================== */}

          {
            accessDecision
            && (

              <div className="recognition-threshold">

                Notificaciones enviadas:{" "}

                <strong>

                  {
                    accessDecision
                      .notifications
                      .enviadas
                  }

                </strong>

                {" · "}

                Errores:{" "}

                <strong>

                  {
                    accessDecision
                      .notifications
                      .errores
                  }

                </strong>

              </div>

            )
          }


          {/* =================================
              EVIDENCIA
          ================================== */}

          {
            accessDecision
              ?.evidence
            && (

              <div className="recognition-threshold">

                Evidencia guardada:{" "}

                <strong>

                  {
                    accessDecision
                      .evidence
                  }

                </strong>

              </div>

            )
          }


          {/* =================================
              REARME
          ================================== */}

          {
            accessDecision
            && (

              <div className="recognition-rearm">

                Retírese de la cámara
                para rearmar el sistema.

                <strong>

                  {
                    missingFrames
                  }
                  /
                  {
                    REQUIRED_MISSING_FRAMES
                  }

                </strong>

              </div>

            )
          }


          <div className="recognition-threshold">

            Umbral actual:{" "}

            <strong>

              {
                result?.threshold
                ?? 0.45
              }

            </strong>

          </div>


          <div className="recognition-preview-note">

            Control de acceso conectado
            a PostgreSQL y al sistema
            de notificaciones.

          </div>

        </div>

      </section>

    </>

  );

}


export default ControlAccesoPage;