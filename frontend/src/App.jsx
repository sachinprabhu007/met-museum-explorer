import { useState } from "react";
import { searchArtworks } from "./api/museum";
import "./App.css";

const SEARCH_BATCH_SIZE = 70;

function App() {
  const [query, setQuery] = useState("");
  const [artworks, setArtworks] = useState([]);
  const [nextOffset, setNextOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSearch(event) {
    event.preventDefault();

    const searchQuery = query.trim();

    if (!searchQuery) {
      return;
    }

    setLoading(true);

    try {
      const data = await searchArtworks(
        searchQuery,
        0
      );

      console.log("Search results:", data);

      setArtworks(data.results ?? []);
      setNextOffset(data.next_offset ?? SEARCH_BATCH_SIZE);
      setHasMore(data.has_more ?? false);
    } catch (error) {
      console.error("Search failed:", error);

      setArtworks([]);
      setNextOffset(0);
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  }

  async function handleLoadMore() {
    if (loading || !hasMore) {
      return;
    }

    setLoading(true);

    try {
      const data = await searchArtworks(
        query,
        nextOffset
      );

      console.log("Load more results:", data);

      setArtworks((current) => [
        ...current,
        ...(data.results ?? []),
      ]);

      setNextOffset(
        data.next_offset ?? nextOffset
      );

      setHasMore(
        data.has_more ?? false
      );
    } catch (error) {
      console.error(
        "Load more failed:",
        error
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header>
        <h1>Met Museum Explorer</h1>

        <form onSubmit={handleSearch}>
          <input
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
            placeholder="Search the collection"
          />

          <button type="submit">
            Search
          </button>
        </form>
      </header>

      {loading && <p>Loading...</p>}

      {!loading &&
        query &&
        artworks.length === 0 && (
          <p>No results found.</p>
        )}

      <section className="gallery">
        {artworks.map((artwork) => (
          <article
            key={artwork.object_id}
            className="card"
          >
            {artwork.image_small_url ? (
              <img
                src={artwork.image_small_url}
                alt={artwork.title}
              />
            ) : (
              <div className="image-placeholder">
                No image available
              </div>
            )}

            <h2>{artwork.title}</h2>

            {artwork.artist && (
              <p>{artwork.artist}</p>
            )}

            {artwork.date && (
              <p>{artwork.date}</p>
            )}
          </article>
        ))}
      </section>

      {hasMore && (
        <button
          className="load-more"
          onClick={handleLoadMore}
          disabled={loading}
        >
          {loading
            ? "Loading..."
            : "Load more"}
        </button>
      )}
    </main>
  );
}

export default App;