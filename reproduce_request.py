
import asyncio
import os
from src.config import get_settings
from src.dependencies import init_resources, close_resources, get_session_maker
from src.llm.llm_factory import get_comment_embedding_model
from src.db import vector_client

async def test_workflow():
    print("Initializing...")
    await init_resources()
    
    try:
        settings = get_settings()
        print(f"Using Embedding Backend: {settings.embedding_backend}")
        
        # 1. Create Embedding Model
        print("Creating embedding model...")
        embed_model = get_comment_embedding_model(settings)
        print(f"Model created: {type(embed_model)}")

        # 2. Embed Query
        text = "This is a test query"
        print(f"Embedding text: '{text}'...")
        embedding = embed_model.embed_query(text)
        print(f"Embedding generated. Length: {len(embedding)}")
        
        # 3. Search DB
        print("Searching database...")
        SessionLocal = get_session_maker()
        async with SessionLocal() as session:
            rows = await vector_client.search_comment_embeddings(
                session,
                embedding=embedding,
                limit=1
            )
            print(f"Search successful. Found {len(rows)} rows.")
            for row in rows:
                print(row)

    except Exception as e:
        print("\n!!! ERROR CAUGHT !!!")
        print(f"Type: {type(e)}")
        print(f"Message: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_resources()

if __name__ == "__main__":
    asyncio.run(test_workflow())
