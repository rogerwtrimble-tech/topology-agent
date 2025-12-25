
import asyncio
from src.config import get_settings
from src.dependencies import init_resources, close_resources, get_session_maker
from src.db import vector_client

async def reproduce_error():
    print("Simplified reproduction starting...")
    await init_resources()
    try:
        # Create a dummy list of floats of size 768
        # We use a non-zero vector to calculate distance against the [0,0...] in DB
        embedding = [0.1] * 768

        SessionLocal = get_session_maker()
        async with SessionLocal() as session:
            rows = await vector_client.search_comment_embeddings(
                session, embedding=embedding, limit=5
            )
            print(f"Search returned {len(rows)} rows.")
            for r in rows:
                print(f" - {r['comment_id']} (dist: {r['distance']})")
                
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await close_resources()

if __name__ == "__main__":
    asyncio.run(reproduce_error())
