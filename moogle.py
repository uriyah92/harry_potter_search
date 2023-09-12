import bs4
import sys
import urllib.parse
import requests
import pickle
import html.parser
import collections
import argparse

# create a pickle file that will contain the connection between html files
#  that are the data base for your harry potter search


def crawl():
    base_url = args[2]
    index_file = args[3]
    file_out = args[4]
    f = open(index_file, 'r')
    list_html = []
    for line in f.readlines():
        list_html.append(line.strip('\n'))
    traffic_dict = {}
    for target in list_html:
        temp_url = urllib.parse.urljoin(base_url, target)
        response_temp = requests.get(temp_url)
        html_temp = response_temp.text
        soup_temp = bs4.BeautifulSoup(html_temp, 'html.parser')
        dict = {}
        for j in soup_temp.find_all("p"):
            for link_temp in j.find_all("a"):
                target_temp = link_temp.get("href")
                if target_temp in list_html:
                    if target_temp in dict:
                        sum = dict[target_temp]+1
                        temp = {target_temp: sum}
                        dict.update(temp)
                    else:
                        dict[target_temp] = 1
        traffic_dict[target] = dict
    f.close()
    with open(file_out, 'wb') as f:
        pickle.dump(traffic_dict, f)

# will create a pickle document that will contain page ranking for each key word,
#  from most realevant to least realevant


def page_rank():
    iterations = int(args[2])
    dict_file = args[3]
    out_file = args[4]
    with open(dict_file, 'rb') as f:
        dict_temp = pickle.load(f)
    r = {}
    for html in dict_temp:
        r[html] = 1
    list_totals = {}
    for html in dict_temp:
        total_num = 0
        for link in dict_temp[html]:
            total_num += dict_temp[html][link]
        list_totals[html] = total_num
    while iterations >= 1:
        new_r = {}
        for html in dict_temp:
            new_r[html] = 0
        for html in dict_temp:

            for html2 in dict_temp:
                for link in dict_temp[html2]:
                    if link == html:
                        sum = float(dict_temp[html2][link])
                        temp = new_r[html]
                        new_r[html] = temp + \
                            float(r[html2])*sum/float(list_totals[html2])

                    else:
                        continue
        r = new_r
        iterations -= 1
    with open(out_file, 'wb') as f:
        pickle.dump(r, f)

# creat a pickle file that contain a dictionary. for each key it keeps the realevant harry potter related reference
#  which are keys for the realevant htmls from the database


def words_dict():
    base_url = args[2]
    index_file = args[3]
    out_file = args[4]
    f = open(index_file, 'r')
    list_html = []
    for line in f.readlines():
        list_html.append(line.strip('\n'))
    word_dict = {}
    for target in list_html:
        temp_url = urllib.parse.urljoin(base_url, target)
        response_temp = requests.get(temp_url)
        html_temp = response_temp.text
        soup_temp = bs4.BeautifulSoup(html_temp, 'html.parser')
        for t in soup_temp.find_all("p"):
            html_text = t.text
            text = html_text.split()
            for word in text:
                if word in word_dict:
                    if target in word_dict[word]:
                        word_dict[word][target] += 1
                    else:
                        word_dict[word][target] = 1
                else:
                    temp_dict = {}
                    temp_dict[target] = 1
                    word_dict[word] = temp_dict
    f.close()
    with open(out_file, 'wb') as f:
        pickle.dump(word_dict, f)

# use the recourses to search for your required reference


def search():
    query = args[2]
    ranking_file = args[3]
    words_file = args[4]
    max_results = int(args[5])
    with open(ranking_file, 'rb') as f:
        ranking_dict = pickle.load(f)
    with open(words_file, 'rb') as f:
        words_dict = pickle.load(f)
    quert_text = query.split()
    results = {}
    for word in quert_text:
        results_temp = []
        if word in words_dict:

            for link in words_dict[word]:
                if link in ranking_dict:
                    results_temp.append((ranking_dict[link], link))
                    results_temp.sort(reverse=True)
                    results[word] = results_temp

    for word in results:
        if len(results[word]) < max_results:
            max_results = len(results[word])
    printed = []
    result_print = list()
    for word in results:
        for i in range(len(results[word])):
            if max_results == 0:
                break
            link = results[word][i][1]
            if link in printed:
                continue
            sum = 0
            for word2 in results:
                for j in range(len(results[word2])):
                    if link == results[word2][j][1]:
                        sum += 1
            if sum == len(results):
                max_results -= 1
                printed.append(link)
                min = 100000
                for word_min in results:
                    if words_dict[word_min][link] <= min:
                        min = words_dict[word_min][link]
                score = float(ranking_dict[link]*min)
                result_print.append((score, link))
                result_print.sort(reverse=True)
    f = open("results.txt", 'a')
    for i in range(len(result_print)):
        print(result_print[i][1]+" "+str(result_print[i][0]))

        f.write(result_print[i][1]+" "+str(result_print[i][0])+"\n")
    f.write("*"*10+"\n")
    f.close()


if __name__ == '__main__':
    args = sys.argv
    func = args[1]
    if func == "crawl":
        crawl()
    elif func == "page_rank":
        page_rank()
    elif func == "words_dict":
        words_dict()
    elif func == "search":
        search()
