# importing yt subtitle extractor library:
from youtube_transcript_api import YouTubeTranscriptApi
import time
# user_input yt link:
link = input('Enter Youtube Video Link here:')

# slicing video_id from the yt link:
if '&' in link:
    end_index = link.index('&')
else:
    end_index = None
video_id = link[link.index('v=')+2:end_index]
    
# calling subtitle extractorlibrary:
yt_api = YouTubeTranscriptApi()

# fetching the subtitile through video_id:
transcript_list = yt_api.fetch(video_id, languages=['en','en-IN','hi'])

# storing the subtitle in string-type:
full_text = ' '.join([d['text'] for d in transcript_list.to_raw_data()])

# importing os and creating a virtual enviornment:
import os
from dotenv import load_dotenv
load_dotenv()

import googleapiclient.discovery
import re 

api_key = os.getenv('GOOGLE_API_KEY')
youtube = googleapiclient.discovery.build('youtube','v3',developerKey=api_key)


request = youtube.videos().list(
    part = 'snippet',
    id = video_id
)

response = request.execute()

if 'items' in response and len(response['items'])>0:
    video_snippet = response['items'][0]['snippet']

    title = video_snippet.get('title','Video Summary')

    description = video_snippet.get('description','')

    thumbnails = video_snippet.get('thumbnails',{})
    thumbnail_url = thumbnails.get('maxres',{}).get('url','') or thumbnails.get('standard',{}).get('url','') or thumbnails.get('high','').get('url','') 

    link_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    extracted_links = re.findall(link_pattern, description)

    links_list = ' '.join(extracted_links)

# importing a google model GenAI:
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash-lite')

# prompt for creating summary of the subtitle fetched:
prompt1 = f'Create a concise, well-structured, and attractive summary of the following text{full_text}. The summary should be organized into clear sections or bullet points to enhance readability and highlight the key takeaways. The tone should be engaging and the style should be attractive to the reader.'
result = model.invoke(prompt1)

# storing the summary:
summary = result.content

# prompt for generating html code using the summary:
prompt2 = f"""Convert the following content into a single, beautifully designed HTML file. The website must be a complete, self-contained file with a dark, modern theme, using Tailwind CSS for styling. The page should be fully responsive and include the provided summary.
- The main topic of the page should be: "{title}".
- **IMPORTANT:** Display the following image as a prominent hero/main image using an `<img>` tag with `src="{thumbnail_url}"`. Apply Tailwind classes like `w-full h-64 object-cover mb-8 rounded-lg` to ensure it displays correctly.
- The website must include the following links from the video description: {links_list}.
- The entire output must be only the HTML code, do not add any extra text outside the code block.
- Do not use ```html``` symbols.
- Here is the summary text to be converted: "{summary}"
"""

output = model.invoke(prompt2)

# storing the html code:
html_code = output.content



# creating the html file:
file_name = f"project_{time.time()}.html"
with open(file_name,'w',encoding='utf-8') as f:
    f.write(html_code)
    
    