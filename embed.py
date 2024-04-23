import pinecone
import openai
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from ratelimiter import RateLimiter

openai.api_key = ''
pinecone_api_key = ''
rate_limiter = RateLimiter(max_calls=3000, period=60)

def get_embedding(text):
    with rate_limiter:
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-3-small",
        )
        if response and response.data:
            embedding_data = response.data[0].embedding
            if embedding_data:
                return embedding_data
            else:
                raise Exception("No data found in response")
        else:
            raise Exception("Failed to get embedding")

def process_job_posting(job_posting, index):
    job_id = job_posting.get('Title')
    job_description = job_posting.get('Job Description')    
    embedding = get_embedding(job_description)


    index.upsert(
        vectors=[
            {
                "id": job_id,
                "values": embedding,
                "metadata": job_posting
            }
        ],
        namespace="job_postings"
    )
    print(f"Processed: {job_id}")

        
# Read job postings from the CSV file
job_postings = []
with open('habib.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        job_postings.append(row)

# Initialize Pinecone

pc = pinecone.Pinecone(api_key=pinecone_api_key)

# Create a Pinecone index if it doesn't exist
index_name = 'jobpostings'
dimension = 1536
metric = 'cosine'

if index_name not in pc.list_indexes().names():
    pc.create_index(name=index_name, dimension=dimension, metric=metric, spec=pinecone.IndexSpec(pods=1))
index = pc.Index(index_name)

# Process job postings using a ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=1) as executor:
    futures = [executor.submit(process_job_posting, job_posting, index) for job_posting in job_postings]
    for future in as_completed(futures):
        future.result()

print('All Done!')