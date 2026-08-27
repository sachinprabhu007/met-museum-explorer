import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import Artwork
from service import get_artwork, search_artist_artworks


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


app = FastAPI(title="Met Museum Explorer")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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