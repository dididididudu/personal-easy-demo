from langchain_community.document_loaders import TextLoader
import os

from pydantic import StrictStr


def load_data_train():
    process_all_files("../knowledge_base", ['.txt'])


def process_all_files(folder_path, file_extensions=None):
    """
    处理文件夹中所有指定类型的文件

    Parameters:
    - folder_path: 文件夹路径
    - file_extensions: 要处理的文件扩展名列表，如 ['.txt', '.csv']
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 如果有文件类型限制，检查扩展名
            if file_extensions:
                _, ext = os.path.splitext(file)
                if ext.lower() not in file_extensions:
                    continue

            file_path = os.path.join(root, file)

            try:
                # 处理文件
                print(f"正在处理: {file_path}")
                process_file(file_path)



            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")
                continue


# 使用示例：只处理txt和csv文件

def process_file(file_path):
    #读取单个文件
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    from langchain_text_splitters import CharacterTextSplitter
    # 切分文件
    text_split = CharacterTextSplitter(chunk_size=200, chunk_overlap=0, separator='\n\n', keep_separator='True')
    segments = text_split.split_documents(documents)
    print("切割份数",len(segments))
    for segment in segments:
        print(segment.page_content)
        print("----------")
    from langchain_community.embeddings import DashScopeEmbeddings
    # 安全获取API密钥
    def _get_api_key() -> str:
        """安全获取API密钥"""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("OPENAI_API_KEY")
    os.environ["DASHSCOPE_API_KEY"] = _get_api_key()
    #对文件进行词嵌入
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v1",
    )
    redis_url = "redis://:@127.0.0.1:6379/0"
    print("111111")
    from langchain_redis import RedisConfig, RedisVectorStore
    config = RedisConfig(
        index_name="faq-index",
        redis_url=redis_url)
    print("222222")
    vector_store = RedisVectorStore(embeddings=embeddings, config=config)
    vector_store.add_documents(documents=segments)
    print(f"{file_path}文件处理完毕")

if __name__ == '__main__':
    load_data_train()