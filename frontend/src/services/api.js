const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function analyzeResume({
  jobTitle,
  companyName,
  jobDescription,
  file,
}) {
  const formData = new FormData();

  formData.append("job_description", jobDescription);
  formData.append("job_title", jobTitle);
  formData.append("company_name", companyName || "");
  formData.append("file", file);

  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Resume analysis failed");
  }

  return data;
}


export async function shortlistCandidates({
  jobTitle,
  companyName,
  jobDescription,
  threshold,
  files,
}) {
  const formData = new FormData();

  formData.append("job_description", jobDescription);
  formData.append("job_title", jobTitle);
  formData.append("company_name", companyName || "");
  formData.append("threshold", threshold);

  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch(`${API_URL}/shortlist`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Candidate screening failed");
  }

  return data;
}


export async function getAnalyses(sessionId) {
  const response = await fetch(
    `${API_URL}/analyses/${sessionId}`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Could not load analyses");
  }

  return data;
}


export async function getShortlisted(sessionId) {
  const response = await fetch(
    `${API_URL}/shortlisted/${sessionId}`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Could not load shortlisted candidates");
  }

  return data;
}


export async function checkBackendHealth() {
  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error("Backend is offline");
  }

  return response.json();
}