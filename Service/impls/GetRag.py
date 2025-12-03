from Service.UniversalRAG import UniversalRAG

class GetRag:
    
    @staticmethod
    def get_bird_rag():

        rag = UniversalRAG(dataset_root="Dataset/bird", dataset_name="bird")
        rag.initialize()

        return rag
    
    @staticmethod
    def get_spider_rag():

        rag = UniversalRAG(dataset_root="Dataset/spider-1.0", dataset_name="spider-1.0")
        rag.initialize()

        return rag