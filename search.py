import logging
from typing import Tuple
from requests import get as requests_get
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL


def search_request(providers: list, query: str, filters: list) -> list:
    provider_results = {}
    # get all results from all selected providers
    total_video_amount = 0
    # TODO: rewrite as match
    for provider in providers:
        if provider == "pornhub":
            temp_query = pornhub_search(query, filters, 1)
            provider_results[provider] = temp_query[0]
            total_video_amount += temp_query[1]
    # combine results into one list
    # Add more logic here for algorithm
    combined_results = []
    provider_counter = 0
    for counter in range(0, total_video_amount):
        combined_results.append(provider_results[providers[provider_counter]][counter])
        provider_counter += 1
        if provider_counter == len(providers):
            provider_counter = 0
    return combined_results


def pornhub_search(query: str, filters: list, page: int) -> Tuple[list, int]:
    logging.info("Querying pornhub with {}".format(query))
    logging.info("Query: " + query)
    logging.info("Filters: " + str(filters))
    logging.info("Page: " + str(page))
    if not query == "":
        request = requests_get("https://www.pornhub.com/video/search?search=" + query + "&page=" + str(page))
        query_type = "videoSearchResult"
    else:
        request = requests_get("https://www.pornhub.com/video")
        query_type = "videoCategory"
    if request.status_code == 200:
        logging.info("Pornhub request successful")
        soup_data = BeautifulSoup(request.text, 'html.parser')
        video_list = soup_data.find(id=query_type).find_all(  # videoCategory
            class_="pcVideoListItem js-pop videoblock videoBox")
        results_dict = []
        video_amount = 0
        for result in video_list:
            logging.info("Found result")
            temp_dict_item = {
                "id": video_amount,
                "provider": "pornhub",
                "page_url": "https://www.pornhub.com/view_video.php?viewkey=" + result["data-video-vkey"],
                "title": result.find(class_="fade fadeUp videoPreviewBg linkVideoThumb js-linkVideoThumb img")["title"],
                "thumbnail": result.find(class_="rotating")["data-thumb_url"],
                "thumbnail_gif": "not yet implemented"
            }
            results_dict.append(temp_dict_item)
            video_amount += 1
        return results_dict, video_amount
    else:
        logging.warning("Could not connect to pornhub")
        return [], 0


def url_to_mp4(url: str) -> Tuple[dict, str]:
    print("The url izzz: " + url)
    with YoutubeDL({'no_warnings': True}) as ydl:
        video_headers = ydl.extract_info(url, download=False)
    print("here is response from ydl: " + str(video_headers))
    logging.info("Youtube-dl response: " + str(video_headers))
    converted_dict = {}
    # TODO: rewrite as match
    for format in video_headers["formats"]:
        if format["format_id"] == "240p":
            converted_dict["240p"] = format["url"]
        elif format["format_id"] == "480p":
            converted_dict["480p"] = format["url"]
        elif format["format_id"] == "720p":
            converted_dict["720p"] = format["url"]
        elif format["format_id"] == "1080p":
            converted_dict["1080p"] = format["url"]
        elif format["format_id"] == "1440p":
            converted_dict["1440p"] = format["url"]
        elif format["format_id"] == "2160p":
            converted_dict["2160p"] = format["url"]
    print(converted_dict)
    return converted_dict, video_headers["thumbnail"]


if __name__ == "__main__":
    print("Do not run this file directly, run main.py")
