const API_BASE_URL = import.meta.env.VITE_API_URL;

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

export async function askMuseumGuide(prompt) {
  const response = await fetch(
    `${API_BASE_URL}/museum-guide`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Museum guide request failed"
    );
  }

  return response.json();
}