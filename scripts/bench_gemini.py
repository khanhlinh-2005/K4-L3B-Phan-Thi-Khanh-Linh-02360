from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from src.embeddings import GeminiEmbedder
from src.models import Document
from src.store import EmbeddingStore


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / 'data' / 'return-refund-policy' / 'return-refund-policy'

queries = [
    'Người mua có thể yêu cầu trả hàng trong những trường hợp nào, và thời hạn gửi yêu cầu là bao lâu?',
    'Người mua cần thực hiện những bước nào để gửi yêu cầu trả hàng trực tiếp từ trang đơn hàng?',
    'Nếu chọn “Tự sắp xếp” để trả hàng, người mua phải trả phí và điều kiện để được Shopee hỗ trợ hoàn phí là gì?',
    'Với thẻ tín dụng/ghi nợ, tiền hoàn được trả về đâu và trong bao lâu?',
    'Khi khiếu nại hàng lỗi, cần chuẩn bị video bằng chứng như thế nào và phải bổ sung trong bao lâu nếu Shopee yêu cầu?',
]


def main() -> None:
    embedder = GeminiEmbedder()
    store = EmbeddingStore(collection_name='gemini_bench', embedding_fn=embedder)

    for file_path in sorted(DOCS_DIR.glob('*.md')):
        text = file_path.read_text(encoding='utf-8')
        store.add_documents([
            Document(
                id=file_path.stem,
                content=text,
                metadata={
                    'doc_id': file_path.stem,
                    'audience': 'buyer',
                    'category': 'returns-policy',
                    'language': 'vi',
                    'source_url': str(file_path),
                },
            )
        ])

    print(f'Loaded {store.get_collection_size()} documents in EmbeddingStore')

    for index, query in enumerate(queries, start=1):
        results = store.search(query, top_k=3)
        print(f'\n=== Query {index} ===')
        print(query)
        for rank, result in enumerate(results, start=1):
            content = result['content'][:220].replace('\n', ' ')
            print(f'{rank}. {result["metadata"].get("doc_id")} | score={result["score"]:.4f} | {content}')

    print('\n=== Metadata filter check ===')
    q = 'Thẻ tín dụng/ghi nợ hoàn tiền trong bao lâu?'
    unfiltered = store.search(q, top_k=3)
    filtered = store.search_with_filter(q, top_k=3, metadata_filter={'category': 'returns-policy', 'audience': 'buyer'})
    print('unfiltered:')
    for rank, result in enumerate(unfiltered, start=1):
        print(f'{rank}. {result["metadata"].get("doc_id")} | score={result["score"]:.4f}')
    print('filtered:')
    for rank, result in enumerate(filtered, start=1):
        print(f'{rank}. {result["metadata"].get("doc_id")} | score={result["score"]:.4f}')


if __name__ == '__main__':
    main()
