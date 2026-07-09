// Central place that tells the frontend where the AgroFast backend lives.
//
// Locally, it auto-detects the FastAPI server (port 5500) or falls back to
// http://localhost:5500 (e.g. when the frontend is opened via Live Server).
//
// When this site is deployed to Netlify (or any host other than localhost),
// it has no way to reach "localhost" on your machine, so it uses the public
// URL below instead: the AgroFast backend Docker Space hosted on Hugging Face.
(function () {
  const DEPLOYED_BACKEND_URL = "https://artisking-agrofast-backend.hf.space";

  window.getBackendUrl = function () {
    const { hostname, port, origin } = window.location;
    const isLocal = hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1";
    if (isLocal) {
      return port === "5500" ? origin : "http://localhost:5500";
    }
    return DEPLOYED_BACKEND_URL;
  };
})();
