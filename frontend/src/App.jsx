import { useState } from "react";
import { motion } from "framer-motion";
import { searchArtworks, askMuseumGuide } from "./api/museum";
import "./App.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const SEARCH_BATCH_SIZE = 70;

function App() {
  const [query, setQuery] = useState("");
  const [artworks, setArtworks] = useState([]);
  const [nextOffset, setNextOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [guideLoading, setGuideLoading] = useState(false);

  async function handleSearch(event) {
    event.preventDefault();

    const searchQuery = query.trim();

    if (!searchQuery) {
      return;
    }

    setLoading(true);

    try {
      const data = await searchArtworks(searchQuery, 0);

      console.log("Search results:", data);

      setArtworks(data.results ?? []);
      setMessages([]);
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

  async function handleMuseumGuide(event) {
    event.preventDefault();

    const prompt = question.trim();

    if (!prompt) {
      return;
    }

    setGuideLoading(true);

    try {
      const data = await askMuseumGuide(prompt);

      console.log("Museum guide response:", data);

      setMessages((current) => [
        ...current,
        {
          question: prompt,
          answer: data.answer ?? "",
        },
      ]);

      setQuestion("");
    } catch (error) {
      console.error("Museum guide failed:", error);

      setMessages((current) => [
        ...current,
        {
          question: prompt,
          answer: "Unable to get a museum guide response.",
        },
      ]);
    } finally {
      setGuideLoading(false);
    }
  }

  async function handleLoadMore() {
    if (loading || !hasMore) {
      return;
    }

    setLoading(true);

    try {
      const data = await searchArtworks(query, nextOffset);

      console.log("Load more results:", data);

      setArtworks((current) => [...current, ...(data.results ?? [])]);

      setNextOffset(data.next_offset ?? nextOffset);
      setHasMore(data.has_more ?? false);
    } catch (error) {
      console.error("Load more failed:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header>
        <h1>Met Museum Explorer</h1>

        <p className="subtitle">
          Search, explore, and ask questions about artworks from The Met.
        </p>

        <form onSubmit={handleSearch}>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search the collection"
          />

          <button type="submit">Search</button>
        </form>
      </header>

      {loading && <p>Loading...</p>}

      {!loading && query && artworks.length === 0 && <p>No results found.</p>}

      <section className="gallery">
        {artworks.map((artwork) => (
          <motion.article
            key={artwork.object_id}
            className="card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -5 }}
            transition={{ duration: 0.3 }}
            onClick={() =>
              window.open(
                `https://www.metmuseum.org/art/collection/search/${artwork.object_id}`,
                "_blank",
                "noopener,noreferrer",
              )
            }
          >
            {artwork.image_small_url ? (
              <img src={artwork.image_small_url} alt={artwork.title} />
            ) : (
              <div className="image-placeholder">No image available</div>
            )}

            <h2>{artwork.title}</h2>

            {artwork.artist && <p>{artwork.artist}</p>}

            {artwork.date && <p>{artwork.date}</p>}
          </motion.article>
        ))}
      </section>

      {hasMore && (
        <button
          className="load-more"
          onClick={handleLoadMore}
          disabled={loading}
        >
          {loading ? "Loading..." : "Load more"}
        </button>
      )}

      {artworks.length > 0 && (
        <section className="museum-guide">
          <h2>Museum Guide</h2>

          <form onSubmit={handleMuseumGuide}>
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask anything about these artworks"
            />

            <button type="submit" disabled={guideLoading}>
              {guideLoading ? "Thinking..." : "Ask"}
            </button>
          </form>

          {messages.map((message, index) => (
            <div key={index} className="museum-message">
              <p>
                <strong>You:</strong> {message.question}
              </p>

              <div className="museum-answer">
                <strong>Museum Guide:</strong>

                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.answer}
                </ReactMarkdown>
              </div>
            </div>
          ))}
        </section>
      )}

      <footer>
        <p>Made with ❤️ by Sachin Prabhu</p>

        <p>
          <a
            href="https://react.dev/"
            target="_blank"
            rel="noopener noreferrer"
          >
            React
          </a>
          {" · "}
          <a href="https://vite.dev/" target="_blank" rel="noopener noreferrer">
            Vite
          </a>
          {" · "}
          <a
            href="https://fastapi.tiangolo.com/"
            target="_blank"
            rel="noopener noreferrer"
          >
            FastAPI
          </a>
          {" · "}
          <a href="https://groq.com/" target="_blank" rel="noopener noreferrer">
            Groq
          </a>
          {" · "}
          <a
            href="https://metmuseum.github.io/"
            target="_blank"
            rel="noopener noreferrer"
          >
            The Met Collection API
          </a>
        </p>

        <p>
          Deployed on{" "}
          <a
            href="https://vercel.com/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Vercel
          </a>
          {" · "}
          <a
            href="https://render.com/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Render
          </a>
        </p>

        <p>
          <a
            href="https://github.com/sachinprabhu007/met-museum-explorer"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </p>
      </footer>
    </main>
  );
}

export default App;
