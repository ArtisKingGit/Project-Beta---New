async function scanCrop(){
  const file = document.getElementById("imageInput").files[0];
  if(!file) return alert("Take a photo first 📸");

  loader.style.display="flex";

  const formData = new FormData();
  formData.append("image", file);

  const getApiUrl = () => {
    if (window.location.port === "8000" || window.location.hostname === "localhost") {
      return "";
    }
    return "http://localhost:8000";
  };

  const res = await fetch(`${getApiUrl()}/predict`, {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  crop.textContent = data.crop;
  disease.textContent = data.disease;
  treatment.textContent = data.treatment;
  confidence.textContent = data.confidence;

  loader.style.display="none";
}
