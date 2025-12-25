
import asyncio
from sqlalchemy import text
from src.dependencies import init_resources, close_resources, get_session_maker

async def check_data():
    print("Checking data...")
    await init_resources()
    try:
        SessionLocal = get_session_maker()
        async with SessionLocal() as session:
            # Check row count
            result = await session.execute(text("SELECT count(*) FROM comment_embeddings"))
            count = result.scalar()
            print(f"Row count in 'comment_embeddings': {count}")

            if count > 0:
                # Show one row
                r = await session.execute(text("SELECT comment_id, metadata, substring(embedding::text, 1, 50) as emb_start FROM comment_embeddings LIMIT 1"))
                row = r.fetchone()
                print(f"Sample row: {row}")
            else:
                print("Table is empty. You need to run the INSERT statement from dbscript.sql.")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await close_resources()

if __name__ == "__main__":
    asyncio.run(check_data())
