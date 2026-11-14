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


interface CameraDeviceOption {
  deviceId: string;
  label: string;
}


interface RecognitionResponse {
  estado:
    | "SIN_ROSTRO"
    | "MULTIPLES_ROSTROS"
    | "SIN_BIOMETRIAS"
    | "RECONOCIDO"
    | "DESCONOCIDO";

  autorizado: boolean;

  similitud:
    number | null;

  threshold: number;

  persona:
    RecognitionPerson
    | null;
}


interface LivenessResponse {
  estado:
    | "OK"
    | "SIN_ROSTRO"
    | "MULTIPLES_ROSTROS";

  frontal: boolean;

  giro_detectado: boolean;

  direccion:
    string | null;

  yaw_score:
    number | null;

  frontal_threshold: number;

  turn_threshold: number;
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

  evidencia:
    string | null;

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


type LivenessPhase =
  | "IDLE"
  | "PREPARING"
  | "TURN"
  | "PASSED";


const REQUIRED_CONFIRMATIONS =
  5;

const REQUIRED_MISSING_FRAMES =
  15;

const REQUIRED_LIVENESS_FRAMES =
  2;

const LIVENESS_TIMEOUT_MS =
  12000;


function ControlAccesoPage() {

  // ==========================================
  // CAMARA
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
  // RECONOCIMIENTO
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
  // LIVENESS
  // ==========================================

  const livenessPreparingRef =
    useRef(false);

  const livenessActiveRef =
    useRef(false);

  const livenessProcessingRef =
    useRef(false);

  const livenessPersonIdRef =
    useRef<number | null>(
      null
    );

  const livenessSuccessRef =
    useRef(0);

  const livenessStartedAtRef =
    useRef(0);

  const confirmedFrameRef =
    useRef<Blob | null>(
      null
    );


  // ==========================================
  // ESTADOS
  // ==========================================

  const [
    cameraReady,
    setCameraReady
  ] =
    useState(false);

  const [
    cameraDevices,
    setCameraDevices
  ] =
    useState<CameraDeviceOption[]>([]);

  const [
    selectedCameraId,
    setSelectedCameraId
  ] =
    useState("");

  const [
    cameraSwitching,
    setCameraSwitching
  ] =
    useState(false);

  const [
    recognitionActive,
    setRecognitionActive
  ] =
    useState(true);

  const [
    result,
    setResult
  ] =
    useState<RecognitionResponse | null>(
      null
    );

  const [
    error,
    setError
  ] =
    useState<string | null>(
      null
    );

  const [
    confirmationCount,
    setConfirmationCount
  ] =
    useState(0);

  const [
    missingFrames,
    setMissingFrames
  ] =
    useState(0);

  const [
    accessDecision,
    setAccessDecision
  ] =
    useState<AccessDecision | null>(
      null
    );

  const [
    doorOpen,
    setDoorOpen
  ] =
    useState(false);

  const [
    eventProcessing,
    setEventProcessing
  ] =
    useState(false);

  const [
    livenessPhase,
    setLivenessPhase
  ] =
    useState<LivenessPhase>(
      "IDLE"
    );

  const [
    livenessProgress,
    setLivenessProgress
  ] =
    useState(0);

  const [
    livenessMessage,
    setLivenessMessage
  ] =
    useState<string | null>(
      null
    );

  const [
    livenessYaw,
    setLivenessYaw
  ] =
    useState<number | null>(
      null
    );


  // ==========================================
  // RESET CONFIRMACION
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
  // RESET LIVENESS
  // ==========================================

  const resetLiveness =
    () => {

      livenessPreparingRef.current =
        false;

      livenessActiveRef.current =
        false;

      livenessProcessingRef.current =
        false;

      livenessPersonIdRef.current =
        null;

      livenessSuccessRef.current =
        0;

      livenessStartedAtRef.current =
        0;

      confirmedFrameRef.current =
        null;

      setLivenessPhase(
        "IDLE"
      );

      setLivenessProgress(
        0
      );

      setLivenessMessage(
        null
      );

      setLivenessYaw(
        null
      );

    };


  // ==========================================
  // REARMAR
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

      resetLiveness();

    };


  // ==========================================
  // CAMARA
  // ==========================================

  const refreshCameraDevices =
    async (
      activeDeviceId?: string
    ) => {

      const devices =
        await navigator
          .mediaDevices
          .enumerateDevices();


      const cameras =
        devices
          .filter(
            (device) =>
              device.kind
              === "videoinput"
          )
          .map(
            (
              device,
              index
            ) => ({
              deviceId:
                device.deviceId,

              label:
                device.label
                ||
                `Cámara ${index + 1}`,
            })
          );


      setCameraDevices(
        cameras
      );


      if (
        activeDeviceId
        &&
        cameras.some(
          (camera) =>
            camera.deviceId
            === activeDeviceId
        )
      ) {

        setSelectedCameraId(
          activeDeviceId
        );

      } else if (
        cameras.length > 0
        &&
        !selectedCameraId
      ) {

        setSelectedCameraId(
          cameras[0].deviceId
        );

      }

    };


  const openCamera =
    async (
      deviceId?: string
    ) => {

      setCameraReady(
        false
      );


      streamRef.current
        ?.getTracks()
        .forEach(
          (track) =>
            track.stop()
        );


      streamRef.current =
        null;


      const videoConstraints:
        MediaTrackConstraints =
        deviceId
          ? {
              deviceId: {
                exact:
                  deviceId,
              },

              width: {
                ideal:
                  1280,
              },

              height: {
                ideal:
                  720,
              },
            }
          : {
              facingMode:
                "user",

              width: {
                ideal:
                  1280,
              },

              height: {
                ideal:
                  720,
              },
            };


      const stream =
        await navigator
          .mediaDevices
          .getUserMedia(
            {
              video:
                videoConstraints,

              audio:
                false,
            }
          );


      streamRef.current =
        stream;


      const video =
        videoRef.current;


      if (!video) {

        stream
          .getTracks()
          .forEach(
            (track) =>
              track.stop()
          );


        streamRef.current =
          null;


        throw new Error(
          "No se encontró el elemento "
          + "de video de la cámara."
        );

      }


      video.srcObject =
        stream;


      await video.play();


      const activeDeviceId =
        stream
          .getVideoTracks()[0]
          ?.getSettings()
          .deviceId;


      await refreshCameraDevices(
        activeDeviceId
      );


      setCameraReady(
        true
      );

    };


  const changeCamera =
    async (
      deviceId: string
    ) => {

      if (
        !deviceId
        ||
        deviceId
        === selectedCameraId
        ||
        cameraSwitching
      ) {

        return;

      }


      setCameraSwitching(
        true
      );


      setError(
        null
      );


      rearmSystem();


      try {

        await openCamera(
          deviceId
        );


        setSelectedCameraId(
          deviceId
        );


      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            "No fue posible cambiar "
            + "la cámara. "
            + err.message
          );

        }


      } finally {

        setCameraSwitching(
          false
        );

      }

    };


  useEffect(() => {

    let cancelled =
      false;


    const startCamera =
      async () => {

        try {

          await openCamera();


          if (
            !cancelled
          ) {

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

            setCameraReady(
              false
            );


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

      cancelled =
        true;


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
  // CAPTURAR FRAME
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
  // LLAMAR LIVENESS
  // ==========================================

  const analyzeLiveness =
    async (
      frame: Blob
    ): Promise<LivenessResponse> => {

      const formData =
        new FormData();


      formData.append(
        "imagen",
        frame,
        "liveness.jpg"
      );


      const response =
        await apiFetch(
          "http://127.0.0.1:8000/api/control-acceso/liveness",
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
                "No fue posible realizar "
                + "la prueba de vida."
              )
        );

      }


      return (
        data as LivenessResponse
      );

    };


  // ==========================================
  // INICIAR PRUEBA DE VIDA
  // ==========================================

  const startLiveness =
    async (
      recognition:
        RecognitionResponse,

      frame:
        Blob
    ) => {

      if (
        livenessPreparingRef.current
        ||
        livenessActiveRef.current
        ||
        !recognition.persona
      ) {

        return;

      }


      livenessPreparingRef.current =
        true;


      setLivenessPhase(
        "PREPARING"
      );


      setLivenessMessage(
        "Mantenga el rostro de frente."
      );


      try {

        const liveness =
          await analyzeLiveness(
            frame
          );


        setLivenessYaw(
          liveness.yaw_score
        );


        if (
          liveness.estado
          !== "OK"
        ) {

          setLivenessMessage(
            "Mantenga solamente un rostro "
            + "frente a la cámara."
          );

          resetConfirmation();

          return;

        }


        if (
          !liveness.frontal
        ) {

          setLivenessMessage(
            "Mire directamente a la cámara "
            + "para iniciar la prueba de vida."
          );

          resetConfirmation();

          return;

        }


        confirmedFrameRef.current =
          frame;


        livenessPersonIdRef.current =
          recognition.persona.id;


        livenessSuccessRef.current =
          0;


        livenessStartedAtRef.current =
          Date.now();


        livenessActiveRef.current =
          true;


        setLivenessPhase(
          "TURN"
        );


        setLivenessProgress(
          0
        );


        setLivenessMessage(
          "Gire la cabeza hacia un lado "
          + "y manténgala un momento."
        );


      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        }


        resetLiveness();


      } finally {

        livenessPreparingRef.current =
          false;

      }

    };


  // ==========================================
  // VALIDAR GIRO
  // ==========================================

  const checkTurnLiveness =
    async (
      frame: Blob
    ) => {

      if (
        !livenessActiveRef.current
        ||
        livenessProcessingRef.current
      ) {

        return;

      }


      if (
        Date.now()
        -
        livenessStartedAtRef.current
        >
        LIVENESS_TIMEOUT_MS
      ) {

        resetLiveness();

        resetConfirmation();

        setLivenessMessage(
          "La prueba de vida expiró. "
          + "Mire nuevamente a la cámara."
        );

        return;

      }


      livenessProcessingRef.current =
        true;


      try {

        const liveness =
          await analyzeLiveness(
            frame
          );


        setLivenessYaw(
          liveness.yaw_score
        );


        if (
          liveness.estado
          !== "OK"
        ) {

          livenessSuccessRef.current =
            0;

          setLivenessProgress(
            0
          );

          return;

        }


        if (
          liveness.giro_detectado
        ) {

          livenessSuccessRef.current =
            Math.min(
              livenessSuccessRef.current
              + 1,
              REQUIRED_LIVENESS_FRAMES
            );


          setLivenessProgress(
            livenessSuccessRef.current
          );


          if (
            livenessSuccessRef.current
            >=
            REQUIRED_LIVENESS_FRAMES
          ) {

            livenessActiveRef.current =
              false;


            decisionLockedRef.current =
              true;


            setLivenessPhase(
              "PASSED"
            );


            setLivenessMessage(
              "Prueba de vida superada."
            );


            const eventFrame =
              confirmedFrameRef.current
              ??
              frame;


            void processAccessEvent(
              eventFrame
            );

          }


        } else {

          livenessSuccessRef.current =
            0;


          setLivenessProgress(
            0
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


      } finally {

        livenessProcessingRef.current =
          false;

      }

    };


  // ==========================================
  // PROCESAR EVENTO
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
              *
              1000
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


        decisionLockedRef.current =
          false;


        resetConfirmation();

        resetLiveness();


      } finally {

        eventProcessingRef.current =
          false;


        setEventProcessing(
          false
        );

      }

    };


  // ==========================================
  // PROCESAR RECONOCIMIENTO
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
            >=
            REQUIRED_MISSING_FRAMES
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
      // PRUEBA DE VIDA ACTIVA
      // ======================================

      if (
        livenessActiveRef.current
      ) {

        if (
          recognition.estado
          === "RECONOCIDO"
          &&
          recognition.persona
          &&
          recognition.persona.id
          ===
          livenessPersonIdRef.current
        ) {

          void checkTurnLiveness(
            frame
          );

        } else {

          livenessSuccessRef.current =
            0;

          setLivenessProgress(
            0
          );

        }


        return;

      }


      if (
        livenessPreparingRef.current
      ) {

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
      // MULTIPLES
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
      // CONFIRMACION
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
        >=
        REQUIRED_CONFIRMATIONS
      ) {

        resetConfirmation();


        // Persona reconocida:
        // ahora exige prueba de vida.
        if (
          recognition.estado
          === "RECONOCIDO"
          &&
          recognition.persona
        ) {

          void startLiveness(
            recognition,
            frame
          );


          return;

        }


        // Persona desconocida:
        // se rechaza directamente.
        decisionLockedRef.current =
          true;


        void processAccessEvent(
          frame
        );

      }

    };


  // ==========================================
  // LOOP DE RECONOCIMIENTO
  // ==========================================

  useEffect(() => {

    if (
      !cameraReady
      ||
      !recognitionActive
    ) {

      return;

    }


    let cancelled =
      false;


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
        700
      );


    return () => {

      cancelled =
        true;


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


      if (
        livenessPhase
        === "PREPARING"
      ) {

        return (
          "PREPARANDO PRUEBA DE VIDA"
        );

      }


      if (
        livenessPhase
        === "TURN"
      ) {

        return (
          "PRUEBA DE VIDA"
        );

      }


      if (
        livenessPhase
        === "PASSED"
      ) {

        return (
          "PRUEBA DE VIDA SUPERADA"
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
  // PERSONA
  // ==========================================

  const displayedPerson =
    accessDecision?.persona
    ??
    result?.persona
    ??
    null;


  // ==========================================
  // SIMILITUD
  // ==========================================

  const displayedSimilarity =
    accessDecision
      ? accessDecision.similitud
      : result?.similitud
        ?? null;


  return (

    <div className="control-access-page">

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


      {
        error
        && (

          <div className="error-message">
            {error}
          </div>

        )
      }


      <section className="control-access-grid">


        {/* CAMARA */}

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


            {
              !cameraReady
              && (

                <div className="camera-loading">
                  {
                    cameraSwitching
                      ? "Cambiando cámara..."
                      : "Iniciando cámara..."
                  }
                </div>

              )
            }


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


          {
            cameraDevices.length > 0
            && (

              <div
                style={{
                  display: "grid",
                  gap: "0.45rem",
                  padding: "0.85rem 1rem 1rem",
                }}
              >

                <label
                  htmlFor="camera-selector"
                  style={{
                    fontSize: "0.78rem",
                    fontWeight: 700,
                    letterSpacing: "0.04em",
                    textTransform: "uppercase",
                  }}
                >
                  Cámara activa
                </label>


                <select
                  id="camera-selector"
                  value={
                    selectedCameraId
                  }
                  disabled={
                    cameraSwitching
                    ||
                    eventProcessing
                  }
                  onChange={
                    (event) => {

                      void changeCamera(
                        event.target.value
                      );

                    }
                  }
                  style={{
                    width: "100%",
                    minHeight: "42px",
                    padding: "0.65rem 0.8rem",
                    borderRadius: "10px",
                    border: "1px solid var(--border-color, #d7dee8)",
                    background: "var(--surface, #ffffff)",
                    color: "inherit",
                    font: "inherit",
                    cursor:
                      cameraSwitching
                        ? "wait"
                        : "pointer",
                  }}
                >

                  {
                    cameraDevices.map(
                      (
                        camera,
                        index
                      ) => (

                        <option
                          key={
                            camera.deviceId
                          }
                          value={
                            camera.deviceId
                          }
                        >
                          {
                            camera.label
                            ||
                            `Cámara ${index + 1}`
                          }
                        </option>

                      )
                    )
                  }

                </select>

              </div>

            )
          }

        </div>


        {/* RESULTADO */}

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
                    : livenessPhase
                      === "TURN"
                      ? "↔"
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
                      "Registrando el evento..."
                    )
                    : accessDecision
                      ? (
                        "La persona no está "
                        + "registrada en el sistema."
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


          {/* PRUEBA DE VIDA */}

          {
            livenessMessage
            &&
            !accessDecision
            && (

              <div className="recognition-confirmation">

                {
                  livenessMessage
                }

                {
                  livenessPhase
                  === "TURN"
                  && (

                    <strong>

                      {
                        livenessProgress
                      }
                      /
                      {
                        REQUIRED_LIVENESS_FRAMES
                      }

                    </strong>

                  )
                }

              </div>

            )
          }


          {
            livenessPhase
            === "TURN"
            &&
            livenessYaw
            !== null
            && (

              <div className="recognition-threshold">

                Movimiento facial:{" "}

                <strong>
                  {
                    Math
                      .abs(
                        livenessYaw
                      )
                      .toFixed(3)
                  }
                </strong>

              </div>

            )
          }


          {/* CONFIRMACION IDENTIDAD */}

          {
            !accessDecision
            &&
            !eventProcessing
            &&
            livenessPhase
            === "IDLE"
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


          {/* EVENTO */}

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


          {/* PUERTA */}

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


          {/* NOTIFICACIONES */}

          {
            accessDecision
            && (

              <div className="recognition-threshold">

                Notificaciones:{" "}

                <strong>

                  {
                    accessDecision
                      .notifications
                      .detalle
                    ??
                    (
                      accessDecision
                        .notifications
                        .enviadas
                      + " enviadas"
                    )
                  }

                </strong>

              </div>

            )
          }


          {/* EVIDENCIA */}

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


          {/* REARME */}

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
                ??
                0.45
              }

            </strong>

          </div>


          <div className="recognition-preview-note">

            Terminal conectada a PostgreSQL,
            notificaciones y control físico
            mediante USB/Serial + ESP32.

          </div>

        </div>

      </section>

    </div>

  );

}


export default ControlAccesoPage;
