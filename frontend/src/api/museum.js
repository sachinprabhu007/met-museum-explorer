const API_BASE_URL = "http://localhost:8000";

export async function searchArtworks(
  query,
  offset = 0
) {
  const params = new URLSearchParams({
    q: query,
    offset: offset.toString(),
  });

  const response = await fetch(
    `${API_BASE_URL}/search?${params}`
  );

  if (!response.ok) {
    throw new Error(
      "Search request failed"
    );
  }

  return response.json();
}