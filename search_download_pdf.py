import arxiv
import re
import os


def search_download(path_save:str, find_text:str, count = 5, sort= arxiv.SortCriterion.SubmittedDate):
    """
    Return:
        list withs path in pdf
    """

    client = arxiv.Client()
    search = arxiv.Search(query = find_text, max_results = count, sort_by = sort)

    j = 0

    papers_link = []
    papers_title = []

    list_dict = []

    d_res = {}
    os.system(f"mkdir -p {path_save}")
    paths_pdf = []
    for result in client.results(search):

        d_info = {}
        #print(result.pdf_url)
        url = result.pdf_url
        last_numbers = url.split("/")[-1]
        res_search = arxiv.Search(id_list=[last_numbers])
        paper = next(arxiv.Client().results(res_search))
        

        d_info['link_paper'] = str(paper)
        for res in client.results(res_search):
            print(res.title)
            papers_title.append(res.title)

            d_info['title'] = res.title
            break
        
        papers_link.append(paper)
        path_full = os.path.join(path_save, f"paper-{j}.pdf")
        print(path_full)
        paper.download_pdf(filename=path_full)
        j += 1

        if os.path.exists(path_full):
            paths_pdf.append(path_full)
            d_info['path_pdf'] = path_full
            list_dict.append(d_info)
    return list_dict



if __name__ == "__main__":
    #print(arxiv.SortCriterion)
    #for i in arxiv.SortCriterion:
    #    print(i)
    res = search_download("./h1" ,"text to image",5, arxiv.SortCriterion.Relevance)
    print(res)