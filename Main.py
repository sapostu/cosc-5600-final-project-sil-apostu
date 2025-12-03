from Service.spider.SpiderService import SpiderService
from Service.bird.BirdService import BirdService
from Util.CommonUtil import CommonUtil


def main():
    
    # Sil here! I am going to be commenting a lot on the "algorithmic" parts I code/implement
    #
    # running llm calls on thousands of items is expensive
    #
    # I could implement with thread pools and concurrency and premium llm keys
    #
    # expensive
    #
    # This costs too much, the point is to show I implemented a system from the project paper
    #
    # I loaded only $10 worth of llm calls for testing and demo purposes
    #
    # if you want to run on all ~9000, put your api key in config.json or env var and change the number below
    #
    # note: you must premium llm keys, otherwise API will rate limit and block
    NUM_ITEMS_TO_TEST = 25

    # Insert whatever string you want
    SEED = "fall-2025-cosc-5600-graduate-project-sapostu"

    LLM_API_KEY = CommonUtil._get_api_key()
    
    
    # PLEASE ONLY TEST ONE AT A TIME
    #
    # Uncomment the one you want to test; comment the other

    # BirdService.test_algo_on_bird_dataset(LLM_API_KEY, NUM_ITEMS_TO_TEST, SEED)

    SpiderService.test_algo_on_spider_dataset(LLM_API_KEY, NUM_ITEMS_TO_TEST, SEED)
    
    

if __name__ == "__main__":
    main()
