export async function apiFetch(
  input: RequestInfo | URL,
  init: RequestInit = {}
): Promise<Response> {

  const token =
    localStorage.getItem(
      "access_token"
    );


  const headers =
    new Headers(
      init.headers
    );


  if (token) {

    headers.set(
      "Authorization",
      `Bearer ${token}`
    );

  }


  const response =
    await fetch(
      input,
      {
        ...init,
        headers,
      }
    );


  if (
    response.status === 401
  ) {

    localStorage.removeItem(
      "access_token"
    );


    if (
      window.location.pathname
      !== "/login"
    ) {

      window.location.replace(
        "/login"
      );

    }

  }


  return response;
}