import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from modules.pdfExtractor import PdfConverter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# model = SentenceTransformer(
#     "thenlper/gte-base", # switch to en/zh for English or Chinese
#     trust_remote_code=True
# )
# model.save(os.path.join(os.getcwd(), "embeddingModel"))


def contextChunks(document_text, chunk_size, chunk_overlap):
    document = Document(page_content=document_text)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    text_chunks = text_splitter.split_documents([document])
    text_content_chunks = [chunk.page_content for chunk in text_chunks]
    return text_content_chunks


def contextEmbedding(model, text_content_chunks):
    text_contents_embeddings = [model.encode([text]) for text in text_content_chunks]
    return text_contents_embeddings

def contextEmbeddingChroma(model, text_content_chunks, db_client, db_path):

    text_contents_embeddings = [model.encode([text])[0] for text in text_content_chunks]
    ids = [f"id_{i}" for i in range(len(text_content_chunks))]

    collection = db_client.get_or_create_collection("embeddings_collection")
    
    collection.add(
        documents=text_content_chunks,
        embeddings=text_contents_embeddings,
        ids=ids  # Include the generated IDs
    )

    return text_contents_embeddings


def retrieveEmbeddingsChroma(db_client):
    collection_name = "embeddings_collection"
    collection = db_client.get_collection(collection_name)

    records = collection.get()
    embeddings = []
    text_chunks = []

    if records and "documents" in records and "embeddings" in records:
        text_chunks = records["documents"] or []  
        embeddings = records["embeddings"] or [] 
    else:
        print("No documents or embeddings found in the collection.")

    return embeddings, text_chunks  


def ragQuery(model, query):
    return model.encode([query])

def similarity(query_embedding, text_contents_embeddings, text_content_chunks, top_k):
    similarities = [(text, cos_sim(embedding, query_embedding[0])) 
                    for text, embedding in zip(text_content_chunks, text_contents_embeddings)]
    
    similarities_sorted = sorted(similarities, key=lambda x: x[1], reverse=True)
    top_k_texts = [text for text, _ in similarities_sorted[:top_k]]

    return "\n".join(f"Text Chunk <{i + 1}>\n{element}" for i, element in enumerate(top_k_texts))


def similarityChroma(query_embedding, db_client, top_k):
    collection = db_client.get_collection("embeddings_collection")
    results = collection.get(include=["documents", "embeddings"])
    
    text_content_chunks = results["documents"]
    text_contents_embeddings = np.array(results["embeddings"])

    text_contents_embeddings = text_contents_embeddings.astype(np.float32)
    query_embedding = query_embedding.astype(np.float32)

    similarities = [
        (text, cos_sim(embedding.reshape(1, -1), query_embedding.reshape(1, -1))[0][0]) 
        for text, embedding in zip(text_content_chunks, text_contents_embeddings)
    ]
    
    similarities_sorted = sorted(similarities, key=lambda x: x[1], reverse=True)
    
    top_k_texts = [text for text, _ in similarities_sorted[:top_k]]

    return "\n".join(f"Text Chunk <{i + 1}>\n{element}" for i, element in enumerate(top_k_texts))




# pdf_file = os.path.join(os.getcwd(), "pdfs", "test2.pdf")
# converter = PdfConverter(pdf_file)
# document_text = converter.convert_to_markdown()

# chunk_size, chunk_overlap, top_k = 2000, 200, 5
# query = "what metric used in this paper for performance evaluation?"

# text_content_chunks = contextChunks(document_text, chunk_size, chunk_overlap)
# text_contents_embeddings = contextEmbedding(model, text_content_chunks)
# query_embedding = ragQuery(model, query)
# top_k_matches = similarity(query_embedding, text_contents_embeddings, text_content_chunks, top_k)
# print(top_k_matches[1])