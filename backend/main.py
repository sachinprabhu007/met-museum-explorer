import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import Artwork, AskRequest, EvaluateRequest
from service import get_artwork, search_artist_artworks
from llm_service import ask_llm
from evaluation import evaluate_museum_response


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Met Museum Explorer",
    description=(
        "An AI-powered museum explorer for searching, "
        "exploring, and asking questions about The Met's art collection."
    ),
)

current_artworks: list[Artwork] = []


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://met-museum-explorer.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/search")
async def search(
    q: str,
    offset: int = 0,
):
    logger.info(
        "Search request: q=%s offset=%s",
        q,
        offset,
    )

    result = await search_artist_artworks(
        q,
        offset,
    )

    if result is None:
        logger.error(
            "Search failed: q=%s",
            q,
        )

        raise HTTPException(
            status_code=502,
            detail="Met Museum search failed",
        )

    global current_artworks

    current_artworks = result["results"]

    logger.info(
        "Search response: q=%s matches=%s next_offset=%s has_more=%s",
        q,
        len(result["results"]),
        result["next_offset"],
        result["has_more"],
    )

    return result


@app.get(
    "/artwork/{object_id}",
    response_model=Artwork,
)
async def artwork(object_id: int):

    logger.info(
        "Artwork request: object_id=%s",
        object_id,
    )

    result = await get_artwork(object_id)

    if result is None:
        logger.warning(
            "Artwork not found: object_id=%s",
            object_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Artwork not found",
        )

    logger.info(
        "Artwork found: object_id=%s title=%s",
        object_id,
        result.title,
    )

    return result


@app.post("/museum-guide")
async def museum_guide(request: AskRequest):

    logger.info(
        "Museum guide request: prompt=%s",
        request.prompt,
    )

    try:
        context = "\n\n".join(
            [
                (
                    f"Object ID: {artwork.object_id}\n"
                    f"Title: {artwork.title}\n"
                    f"Artist: {artwork.artist}\n"
                    f"Nationality: {artwork.artist_nationality}\n"
                    f"Date: {artwork.date}\n"
                    f"Medium: {artwork.medium}\n"
                    f"Dimensions: {artwork.dimensions}\n"
                    f"Department: {artwork.department}\n"
                    f"Gallery: {artwork.gallery}\n"
                    f"Tags: {', '.join(artwork.tags)}"
                )
                for artwork in current_artworks
            ]
        )

        result = await ask_llm(
            request.prompt,
            context,
        )

    except Exception:
        logger.exception(
            "Museum guide request failed"
        )

        raise HTTPException(
            status_code=502,
            detail="Museum guide request failed",
        )

    logger.info(
        "Museum guide response generated | fallback_used=%s",
        result.get("fallback_used", False),
    )

    return {
        "answer": result["answer"],
        "context": result["context"],
    }


@app.post("/evaluate")
async def evaluate(request: EvaluateRequest):

    logger.info(
        "Evaluation request: question=%s",
        request.question,
    )

    try:
        result = evaluate_museum_response(
            request.question,
            request.answer,
            request.context,
        )

    except Exception:
        logger.exception(
            "Evaluation request failed"
        )

        raise HTTPException(
            status_code=502,
            detail="Evaluation failed",
        )

    return result