from search_download_pdf import search_download
from reader_pdf import read_file_pdf
from easygoogletranslate import EasyGoogleTranslate
import re




def append_full_text(pages):
    text = ""
    for page in pages:
        text += page
    return text

def split_text_by_sentences(text, max_length=4000):
    parts = []
    current_part = ""
    
    # Используем регулярное выражение для нахождения конца предложения
    sentences = re.split(r'(\.|\?|\!)\s', text)
    # Воссоздаем предложения, разделенные регулярным выражением
    sentences = ["".join(sentences[i:i+2]) for i in range(0, len(sentences)-1, 2)]
    
    for sentence in sentences:
        if len(current_part) + len(sentence) < max_length:
            current_part += sentence
        else:
            parts.append(current_part)
            current_part = sentence
    if current_part:
        parts.append(current_part)
    
    return parts

class PromptTranslatorEnRu:
    def __init__(self):
        """
        Initialize the PromptTranslatorRuEn class.
        """

        self.model  = EasyGoogleTranslate(
            source_language='en',
            target_language='ru',
            timeout=10
        )

    def translate_big_text(self, text):
        
        res_rus = ""
        parts = split_text_by_sentences(text)
        for i, part in enumerate(parts):

            #print(f"Часть {i+1}:\n\n")
            
            if len(part) > 5000:
                
                continue
            res = self.run(part)
            #print(res)
            res_rus+= res

        return res_rus




    def run(self, input_prompt: str) -> str:
        """
        Preprocesses the input text prompt and returns the processed output.

        Args:
            input_prompt (str): The input text prompt.

        Returns:
            str: The preprocessed text prompt.
        """
        # Implementation logic for prompt preprocessing
        super().__init__()

       
        result = self.model.translate(input_prompt)
        
        #print(result)
        return result


translator = PromptTranslatorEnRu()

def en_pdf_to_ru_txt(path_pdf):
    
    pages = read_file_pdf(path_pdf)
        
    text = append_full_text(pages)
    
    rus_text = translator.translate_big_text(text)

    path_save_txt = path_pdf[:-3] + 'txt'
    with open(path_save_txt, 'w', encoding='utf-8') as file:
        file.write(rus_text)
    print("write file ok!")

    return path_save_txt


if __name__ == "__main__":
    res = search_download("./h1" ,"text to image", count = 1)
    print(res)
    translator = PromptTranslatorEnRu()
    #text = translator.run(message.text)

    transleted_text = []
    for path_pdf in res:

        pages = read_file_pdf(path_pdf)
        
        text = append_full_text(pages)

        rus_text = translator.translate_big_text(text)
        with open(path_pdf[:-3] + 'txt', 'w', encoding='utf-8') as file:
            file.write(rus_text)
        break



        #res = translator.run(text)
        #print(res)
        break
        for page in pages:
            res = translator.run(page)
            print(res)

        
        #text = append_full_text(pages)
        #print(text)
        #translated = GoogleTranslator(source='auto', target='russian').translate(text)

        for page in pages:
            translated = GoogleTranslator(source='auto', target='russian').translate_file(path_pdf)
            print(translated)
            break
        #    print(page)

            # res = clean_text_nltk(page)
            # print("\n\n\n\nRES:\n")
            # print(res)
            # break
            # res = translate_extracted(page)
            # print(res)
            # break

            # #translated = GoogleTranslator(source='auto', target='russian').translate_file(path_pdf)
            # translated = GoogleTranslator(source='auto', target='russian').translate(page)
            
            
            # print(translated)
            # transleted_text.append(translated)