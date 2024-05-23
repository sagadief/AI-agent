orig_token = "NTlkY2MyZmItM2Q4ZC00ZWMzLWE2NjAtNTI3MzZhOTk2ZjQzOjVhZGJiZDQxLTc0YjAtNDQxNi04YjAzLTUxZDVmYTY4NTkwNw=="


## Q-A
from langchain.chat_models.gigachat import GigaChat
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain.chains import RetrievalQA



##summary
from langchain_core.language_models import BaseLanguageModel
from langchain.prompts import load_prompt
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.chat_models import GigaChat as GigaChatv2
from langchain.document_loaders import TextLoader


llm = GigaChat(credentials=orig_token, scope="GIGACHAT_API_CORP",verify_ssl_certs=False,model="GigaChat-Pro")
giga= GigaChatv2(credentials=orig_token, scope="GIGACHAT_API_CORP",verify_ssl_certs=False,model="GigaChat-Pro")


def reading_txt_giga(path_txt):
    loader = TextLoader(path_txt)
    #loader = TextLoader("./text1.txt")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=500,
    )
    documents = text_splitter.split_documents(documents)
    print(f"Total documents: {len(documents)}")


    embeddings = GigaChatEmbeddings(
    credentials=orig_token, verify_ssl_certs=False,scope="GIGACHAT_API_CORP"
    )

    db = Chroma.from_documents(
        documents,
        embeddings,
        client_settings=Settings(anonymized_telemetry=False),
    )

    return db
    docs = db.similarity_search("cделай краткую выжимку",k=100)
    len(docs)

    

    qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

    print(qa_chain({"query": "cделай краткую выжимку"}))
    return db,



def txt_to_summary(path_txt):
    loader = TextLoader(path_txt)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 7000,
        chunk_overlap  = 0,
        length_function = len,
        is_separator_regex = False,
    )
    documents = text_splitter.split_documents(documents)
    print(f"Количество частей книги: {len(documents)}")
    book_map_prompt = load_prompt("lc://prompts/summarize/map_reduce/summarize_book_map.yaml")
    book_combine_prompt = load_prompt("lc://prompts/summarize/map_reduce/summarize_book_combine.yaml")

    chain = load_summarize_chain(giga, chain_type="map_reduce", 
                                map_prompt=book_map_prompt,
                                combine_prompt=book_combine_prompt,
                                verbose=False)
    
    res = chain.invoke({"input_documents": documents, "map_size": "одно предложение", "combine_size": "три предложения"})

    print(res["output_text"].replace(". ", ".\n"))
    return res["output_text"].replace(". ", ".\n")

