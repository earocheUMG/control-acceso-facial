import {
  useEffect,
  useRef,
  useState,
} from "react";


interface EnrollmentPerson {
  id: number;
  nombre_completo: string;
}


interface EnrollmentModalProps {
  person: EnrollmentPerson;
  onClose: () => void;
  onCompleted: (
    biometricCode: string
  ) => void;
}


const SAMPLE_INSTRUCTIONS = [
  "Mire de frente a la cámara.",
  "Gire ligeramente el rostro hacia la izquierda.",
  "Gire ligeramente el rostro hacia la derecha.",
  "Mire ligeramente hacia arriba.",
  "Mire ligeramente hacia abajo.",
  "Vuelva a mirar de frente.",
  "Incline ligeramente la cabeza hacia la izquierda.",
  "Incline ligeramente la cabeza hacia la derecha.",
  "Mantenga una expresión natural mirando al frente.",
  "Última muestra: mire directamente a la cámara.",
];


function EnrollmentModal({
  person,
  onClose,
  onCompleted,
}: EnrollmentModalProps) {

  // ==========================================
  // REFERENCIAS
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


  // ==========================================
  // ESTADOS
  // ==========================================

  const [
    cameraReady,
    setCameraReady
  ] = useState(false);


  const [
    samples,
    setSamples
  ] = useState<Blob[]>([]);


  const [
    error,
    setError
  ] = useState<string | null>(
    null
  );


  const [
    success,
    setSuccess
  ] = useState<string | null>(
    null
  );


  const [
    sampleMessage,
    setSampleMessage
  ] = useState<string | null>(
    null
  );


  const [
    validatingSample,
    setValidatingSample
  ] = useState(false);


  const [
    uploading,
    setUploading
  ] = useState(false);


  // ==========================================
  // DETENER CAMARA
  // ==========================================

  const stopCamera = () => {

    if (
      streamRef.current
    ) {

      streamRef.current
        .getTracks()
        .forEach(
          (track) =>
            track.stop()
        );


      streamRef.current =
        null;

    }


    setCameraReady(
      false
    );

  };


  // ==========================================
  // INICIAR CAMARA
  // ==========================================

  useEffect(() => {

    let cancelled = false;


    const startCamera =
      async () => {

        try {

          setError(
            null
          );


          setCameraReady(
            false
          );


          if (
            !navigator.mediaDevices
            ||
            !navigator.mediaDevices
              .getUserMedia
          ) {

            throw new Error(
              "El navegador no permite "
              + "acceder a la cámara."
            );

          }


          const stream =
            await navigator
              .mediaDevices
              .getUserMedia(
                {
                  video: {
                    facingMode:
                      "user",

                    width: {
                      ideal: 1280
                    },

                    height: {
                      ideal: 720
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

            stream
              .getTracks()
              .forEach(
                (track) =>
                  track.stop()
              );

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

          if (cancelled) {
            return;
          }


          if (
            err instanceof DOMException
            &&
            err.name === "AbortError"
          ) {

            return;

          }


          if (
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


    startCamera();


    return () => {

      cancelled = true;


      if (
        streamRef.current
      ) {

        streamRef.current
          .getTracks()
          .forEach(
            (track) =>
              track.stop()
          );


        streamRef.current =
          null;

      }

    };

  }, []);


  // ==========================================
  // GENERAR FOTO DESDE VIDEO
  // ==========================================

  const createCameraBlob =
    async (): Promise<Blob> => {

      const video =
        videoRef.current;


      const canvas =
        canvasRef.current;


      if (
        !video
        ||
        !canvas
      ) {

        throw new Error(
          "La cámara todavía "
          + "no está lista."
        );

      }


      if (
        video.videoWidth === 0
        ||
        video.videoHeight === 0
      ) {

        throw new Error(
          "Espere unos segundos "
          + "hasta que la cámara "
          + "esté lista."
        );

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

        throw new Error(
          "No fue posible capturar "
          + "la imagen."
        );

      }


      context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
      );


      const blob =
        await new Promise<
          Blob | null
        >(
          (resolve) => {

            canvas.toBlob(
              resolve,
              "image/jpeg",
              0.92
            );

          }
        );


      if (!blob) {

        throw new Error(
          "No fue posible generar "
          + "la fotografía."
        );

      }


      return blob;

    };


  // ==========================================
  // VALIDAR MUESTRA EN FASTAPI
  // ==========================================

  const validateSample =
    async (
      sample: Blob
    ) => {

      const formData =
        new FormData();


      formData.append(
        "muestra",
        sample,
        "sample.jpg"
      );


      const response =
        await fetch(
          `http://127.0.0.1:8000/api/personas/${person.id}/enrolamiento/validar-muestra`,
          {
            method: "POST",

            body:
              formData,
          }
        );


      const result =
        await response.json();


      if (!response.ok) {

        let message =
          "La muestra facial "
          + "no es válida.";


        if (
          typeof result.detail
          === "string"
        ) {

          message =
            result.detail;

        }


        throw new Error(
          message
        );

      }


      return result;

    };


  // ==========================================
  // CAPTURAR Y VALIDAR
  // ==========================================

  const captureSample =
    async () => {

      if (
        samples.length >= 10
      ) {

        return;

      }


      if (
        validatingSample
        ||
        uploading
      ) {

        return;

      }


      try {

        setError(
          null
        );


        setSampleMessage(
          null
        );


        setValidatingSample(
          true
        );


        // =====================================
        // CAPTURAR IMAGEN
        // =====================================

        const blob =
          await createCameraBlob();


        // =====================================
        // VALIDAR EN BACKEND
        // =====================================

        await validateSample(
          blob
        );


        // =====================================
        // ACEPTAR SOLAMENTE SI ES VALIDA
        // =====================================

        setSamples(
          (current) => [
            ...current,
            blob
          ]
        );


        setSampleMessage(
          `Muestra ${
            samples.length + 1
          } validada correctamente.`
        );


      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        }


      } finally {

        setValidatingSample(
          false
        );

      }

    };


  // ==========================================
  // REINICIAR MUESTRAS
  // ==========================================

  const resetSamples = () => {

    if (
      uploading
      ||
      validatingSample
    ) {

      return;

    }


    setSamples(
      []
    );


    setSuccess(
      null
    );


    setError(
      null
    );


    setSampleMessage(
      null
    );

  };


  // ==========================================
  // COMPLETAR ENROLAMIENTO
  // ==========================================

  const submitEnrollment =
    async () => {

      if (
        samples.length !== 10
      ) {

        setError(
          "Debe capturar "
          + "las 10 muestras."
        );

        return;

      }


      try {

        setUploading(
          true
        );


        setError(
          null
        );


        setSuccess(
          null
        );


        setSampleMessage(
          null
        );


        const formData =
          new FormData();


        samples.forEach(
          (
            sample,
            index
          ) => {

            formData.append(
              "muestras",
              sample,
              `sample_${String(
                index + 1
              ).padStart(
                2,
                "0"
              )}.jpg`
            );

          }
        );


        const response =
          await fetch(
            `http://127.0.0.1:8000/api/personas/${person.id}/enrolamiento`,
            {
              method: "POST",

              body:
                formData,
            }
          );


        const result =
          await response.json();


        if (!response.ok) {

          let message =
            "No fue posible completar "
            + "el enrolamiento.";


          if (
            typeof result.detail
            === "string"
          ) {

            message =
              result.detail;

          }


          throw new Error(
            message
          );

        }


        const biometricCode =
          result.persona
            .codigo_biometrico;


        setSuccess(
          "Enrolamiento completado "
          + "correctamente. "
          + "Código biométrico: "
          + biometricCode
        );


        stopCamera();


        window.setTimeout(
          () => {

            onCompleted(
              biometricCode
            );

          },
          1500
        );


      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        }


      } finally {

        setUploading(
          false
        );

      }

    };


  // ==========================================
  // CERRAR
  // ==========================================

  const handleClose = () => {

    if (
      uploading
      ||
      validatingSample
    ) {

      return;

    }


    stopCamera();


    onClose();

  };


  // ==========================================
  // INSTRUCCION ACTUAL
  // ==========================================

  const currentInstruction =
    SAMPLE_INSTRUCTIONS[
      Math.min(
        samples.length,
        9
      )
    ];


  // ==========================================
  // PORCENTAJE
  // ==========================================

  const progress =
    (
      samples.length
      / 10
    )
    * 100;


  // ==========================================
  // RENDER
  // ==========================================

  return (

    <div className="modal-backdrop">

      <div className="modal enrollment-modal">


        {/* ===================================
            HEADER
        ==================================== */}

        <div className="modal-header">

          <div>

            <h3>
              Enrolamiento facial
            </h3>

            <p>
              {
                person
                  .nombre_completo
              }
            </p>

          </div>


          <button
            type="button"
            className="modal-close"
            onClick={
              handleClose
            }
            disabled={
              uploading
              ||
              validatingSample
            }
          >
            ×
          </button>

        </div>


        {/* ===================================
            BODY
        ==================================== */}

        <div className="modal-body">


          {/* CAMARA */}

          <div className="enrollment-camera">

            <video
              ref={
                videoRef
              }
              className="enrollment-video"
              autoPlay
              muted
              playsInline
            />


            {!cameraReady && !error && (

              <div className="camera-loading">

                Solicitando acceso
                a la cámara...

              </div>

            )}


            {validatingSample && (

              <div className="camera-validating">

                Validando rostro...

              </div>

            )}

          </div>


          <canvas
            ref={
              canvasRef
            }
            className="hidden-canvas"
          />


          {/* ===================================
              PROGRESO
          ==================================== */}

          <div className="enrollment-progress">

            <div className="enrollment-progress-header">

              <strong>
                Muestras válidas
              </strong>


              <span>
                {samples.length}
                {" / "}
                10
              </span>

            </div>


            <div className="progress-bar">

              <div
                className="progress-bar-fill"
                style={{
                  width:
                    `${progress}%`,
                }}
              />

            </div>

          </div>


          {/* ===================================
              INSTRUCCION
          ==================================== */}

          {
            samples.length < 10
            && (

              <div className="enrollment-instruction">

                <strong>
                  Siguiente muestra
                </strong>

                <p>
                  {
                    currentInstruction
                  }
                </p>

              </div>

            )
          }


          {/* ===================================
              10 MUESTRAS LISTAS
          ==================================== */}

          {
            samples.length === 10
            && (

              <div className="form-info">

                <strong>
                  Captura completada
                </strong>

                <p>
                  Las 10 muestras fueron
                  validadas correctamente.
                  Ahora puede completar
                  el enrolamiento biométrico.
                </p>

              </div>

            )
          }


          {/* ===================================
              MENSAJE MUESTRA VALIDA
          ==================================== */}

          {
            sampleMessage
            && !error
            && (

              <div className="sample-valid-message">

                ✓ {sampleMessage}

              </div>

            )
          }


          {/* ===================================
              ERROR
          ==================================== */}

          {error && (

            <div className="error-message enrollment-message">

              {error}

            </div>

          )}


          {/* ===================================
              EXITO FINAL
          ==================================== */}

          {success && (

            <div className="success-message enrollment-message">

              {success}

            </div>

          )}


          {/* ===================================
              NOTA
          ==================================== */}

          <div className="enrollment-note">

            Cada fotografía es validada
            automáticamente. Debe existir
            exactamente un rostro visible,
            con buena iluminación y sin
            obstrucciones.

          </div>

        </div>


        {/* ===================================
            FOOTER
        ==================================== */}

        <div className="modal-footer">

          <button
            type="button"
            className="secondary-button"
            onClick={
              resetSamples
            }
            disabled={
              samples.length === 0
              ||
              uploading
              ||
              validatingSample
            }
          >
            Reiniciar
          </button>


          {
            samples.length < 10
            ? (

              <button
                type="button"
                className="primary-button"
                onClick={
                  captureSample
                }
                disabled={
                  !cameraReady
                  ||
                  validatingSample
                  ||
                  uploading
                }
              >

                {
                  validatingSample
                    ?
                      "Validando..."
                    :
                      "Capturar muestra"
                }

              </button>

            )
            : (

              <button
                type="button"
                className="primary-button"
                onClick={
                  submitEnrollment
                }
                disabled={
                  uploading
                  ||
                  success !== null
                }
              >

                {
                  uploading
                    ?
                      "Procesando..."
                    :
                      "Completar enrolamiento"
                }

              </button>

            )
          }

        </div>

      </div>

    </div>

  );

}


export default EnrollmentModal;