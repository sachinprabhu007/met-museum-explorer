import asyncio

import httpx

from schemas import Artwork


BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

HEADERS = {
    "User-Agent": "Met-Museum-Explorer/1.0"
}

SEARCH_BATCH_SIZE = 70
OBJECT_BATCH_SIZE = 20
MAX_CONCURRENT_REQUESTS = 5
BATCH_DELAY = 0.5


search_cache: dict[str, list[int]] = {}
artwork_cache: dict[int, Artwork] = {}


def build_artwork(data: dict) -> Artwork:
    return Artwork(
        object_id=data["objectID"],
        title=data["title"],
        artist=data.get("artistDisplayName", ""),
        artist_role=data.get("artistRole", ""),
        artist_nationality=data.get("artistNationality", ""),
        date=data.get("objectDate", ""),
        medium=data.get("medium", ""),
        image_url=data.get("primaryImage"),
        image_small_url=data.get("primaryImageSmall"),
        dimensions=data.get("dimensions"),
        department=data.get("department"),
        gallery=data.get("GalleryNumber"),
        tags=[
            tag["term"]
            for tag in (data.get("tags") or [])
        ],
    )


async def search_artworks(query: str):
    query_normalized = query.strip().lower()

    if query_normalized in search_cache:
        return search_cache[query_normalized]

    url = f"{BASE_URL}/search"

    params = {
        "q": query,
        "hasImages": "true",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                params=params,
                headers=HEADERS,
            )

            if response.status_code != 200:
                return None

            data = response.json()

            object_ids = data.get("objectIDs") or []

            search_cache[query_normalized] = object_ids

            return object_ids

        except httpx.HTTPError:
            return None


async def get_artwork(object_id: int) -> Artwork | None:

    if object_id in artwork_cache:
        return artwork_cache[object_id]

    url = f"{BASE_URL}/objects/{object_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers=HEADERS,
            )

            if response.status_code != 200:
                return None

            artwork = build_artwork(response.json())

            artwork_cache[object_id] = artwork

            return artwork

        except httpx.HTTPError:
            return None


async def get_artwork_with_client(
    object_id: int,
    client: httpx.AsyncClient,
) -> Artwork | None:

    if object_id in artwork_cache:
        return artwork_cache[object_id]

    url = f"{BASE_URL}/objects/{object_id}"

    try:
        response = await client.get(
            url,
            headers=HEADERS,
        )

        if response.status_code != 200:
            return None

        artwork = build_artwork(response.json())

        artwork_cache[object_id] = artwork

        return artwork

    except httpx.HTTPError:
        return None


async def fetch_object_batch(
    object_ids: list[int],
    client: httpx.AsyncClient,
):
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def fetch(object_id: int):

        if object_id in artwork_cache:
            return artwork_cache[object_id]

        async with semaphore:
            return await get_artwork_with_client(
                object_id,
                client,
            )

    return await asyncio.gather(
        *(fetch(object_id) for object_id in object_ids)
    )


async def search_artist_artworks(
    query: str,
    offset: int = 0,
):
    object_ids = await search_artworks(query)

    if object_ids is None:
        return None

    total = len(object_ids)

    # The FE-visible page is 70 candidates.
    search_batch = object_ids[
        offset:offset + SEARCH_BATCH_SIZE
    ]

    query_normalized = query.strip().lower()

    artworks = []

    async with httpx.AsyncClient() as client:

        # Process those 70 in smaller groups of 20
        # to avoid a large request burst to Met.
        for start in range(
            0,
            len(search_batch),
            OBJECT_BATCH_SIZE,
        ):

            batch = search_batch[
                start:start + OBJECT_BATCH_SIZE
            ]

            results = await fetch_object_batch(
                batch,
                client,
            )

            for artwork in results:

                if artwork is None:
                    continue

                if artwork.artist_role != "Artist":
                    continue

                if not artwork.artist:
                    continue

                artist = artwork.artist.strip().lower()

                if artist.startswith(query_normalized):
                    artworks.append(artwork)

            if (
                start + OBJECT_BATCH_SIZE
                < len(search_batch)
            ):
                await asyncio.sleep(BATCH_DELAY)

    next_offset = offset + len(search_batch)

    return {
        "results": artworks,
        "next_offset": next_offset,
        "has_more": next_offset < total,
    }