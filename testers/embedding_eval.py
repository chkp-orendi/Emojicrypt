from openai import AzureOpenAI
import numpy as np
from numpy.linalg import norm
import logging
import pandas as pd
import datetime
import common
import os

os.environ["REQUESTS_CA_BUNDLE"]= r'C:\Users\orendi\Documents\EmojiCrypt\ca-certificates.crt'
log_path = '~/Emoji/Emojicrypt/log/embedding_eval.log'
data_path = '~/Emoji/Emojicrypt/data/embedding/embedding_test.xlsx'

API_KEY = "95787a606b6b4d41800ec9ff2b6ddcb8"
ENDPOINT = "https://staging-dev-openai.azure-api.net/openai-gw-proxy-dev/"
embed_model = "text-embedding-3-large"
azure_client = AzureOpenAI(azure_endpoint=ENDPOINT, api_key=API_KEY, api_version="2023-07-01-preview")

def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return azure_client.embeddings.create(input = [text], model=model).data[0].embedding

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))


def compare_text_embedding_similarity(text_1, text_2):
    return cosine_similarity(np.array(get_embedding(text_1)), np.array(get_embedding(text_2)))

def dict_encrytion_test(original_encryption, guessed_encryption):
    for key in original_encryption:
        if original_encryption[key] == guessed_encryption[key]:
            return False
    return True


def main(local_client, models):
    logger = logging.getLogger("embedding")
    #find a dataset to test the embedding on
    logger.info(f"Starting embedding_eval.py\n")
    df = pd.read_excel(data_path)
    model_results = {}
    logger.info('Loaded dataset')
    for model in models:
        logger.info(f"Starting model {model}")
        sim_avrg = 0
        for index, row in df.iterrows():
            text_1= row["text_1"]
            logger.info(f"sending prompt to be encrypt {text_1}")
            text_2= common.emoji_encrypt_text(text_1,local_client, model)
            similarity = cosine_similarity(np.array(get_embedding(text_1)), np.array(get_embedding(text_2)))
            logger.info(f"Time: {datetime.datetime.now()}, Model: {model}, index: {index}, text: {text_1}, text_encrypt: {text_2}, Similarity: {similarity}")
            sim_avrg += similarity
        sim_avrg = sim_avrg/len(df.index)
        logger.info(f"Time: {datetime.datetime.now()}, Model {model}, Average Similarity: {sim_avrg}")
        model_results[model] = sim_avrg
    print(model_results)
    #add log for finished with details

if __name__ == '__main__':
    # logger = common.init_logs(log_path, 'e')
    #need to test similarities of:
    # text1 = "The sun was setting, casting a golden hue over the horizon. Birds chirped softly as the day turned into night. It was a peaceful end to a beautiful day."
    # text2 = "As the sun dipped below the horizon, the sky glowed with a warm, golden light. The gentle chirping of birds marked the transition from day to night. The day concluded serenely and beautifully."
    # play with the order of the sentences and check if they are still the same
    # print(get_embedding(text1))

    text_1 = """
To add functional tests for your Symfony bundle, you'll need to set up a test environment that simulates a full Symfony application. This allows you to test your bundle's integration within an application context. Here's how you can approach this:
1.	Create a Test Application: Since you already have a /tests/TestApplication folder with a blank project, you're on the right track. This test application will serve as a dummy application to load and test your bundle.
2.	Configure the Test Application: Set up your TestApplication like a typical Symfony application. Ensure it includes the necessary configuration to load your bundle. Here's an example of what you need to do:
o	composer.json: Include your bundle as a dependency, possibly via a path repository if it's not published yet.
json
Copy code
{
    "require": {
        "symfony/symfony": "^5.3",
        "your/bundle": "dev-main"
    },
    "repositories": [
        {
            "type": "path",
            "url": "../../path/to/your/bundle"
        }
    ]
}
o	config/bundles.php: Register your bundle in the test application.
php
Copy code
return [
    Symfony\Bundle\FrameworkBundle\FrameworkBundle::class => ['all' => true],
    Your\Bundle\YourBundle::class => ['all' => true],
];
o	config/packages/test/framework.yaml: Configure the framework for the test environment.
yaml
Copy code
framework:
    test: true
    session:
        storage_id: session.storage.mock_file
    profiler:
        collect: false
3.	Write Functional Tests: Use the Symfony WebTestCase to write your functional tests. Place these tests in the /tests/ directory of your bundle.
php
Copy code
namespace Your\Bundle\Tests;

use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;

class YourBundleFunctionalTest extends WebTestCase
{
    public function testSomeRoute()
    {
        $client = static::createClient();
        $crawler = $client->request('GET', '/some-route');

        $this->assertSame(200, $client->getResponse()->getStatusCode());
        $this->assertContains('Some content', $crawler->filter('h1')->text());
    }
}
4.	Run the Tests: Execute your tests using PHPUnit.
bash
Copy code
php bin/phpunit
Additional Resources:
•	Symfony Testing Documentation
•	Creating Functional Tests in Symfony
By setting up a test application and writing functional tests within that context, you can verify that your bundle integrates correctly and behaves as expected when interacting with routes and other services.
"""
    text_2 = """
It sounds like you're looking to implement integration tests for your package (📦) that manages users, permissions, and profiles across multiple applications. Here’s how you can approach this:
Approach to Adding Integration Tests
1.	Setup for Integration Testing: Since you mentioned you don't have a 🧱 (framework) and you have a blank project in a 📂📝, it seems you're setting up a new environment for testing. You'll need to choose a testing framework suitable for your programming language. Popular choices include pytest for Python, JUnit for Java, Mocha for JavaScript, etc.
2.	Identify Integration Points: Determine the integration points in your 📦 that interact with multiple applications. These could be APIs, database connections, or other external services.
3.	Write Integration Tests: Integration tests verify the interaction between your 📦 and these external components to ensure they work together correctly. Here’s how you can structure your tests:
o	Test Scenarios: Create test scenarios that simulate real-world usage of your 📦. For example, creating a user across multiple applications and verifying permissions.
o	Mocking: Use mocking frameworks (if applicable) to simulate responses from external services or APIs that your 📦 interacts with. This helps isolate your tests and makes them more reliable.
o	Data Setup and Teardown: Ensure your tests can set up necessary data and clean up after themselves to maintain test independence.
4.	Avoiding Pitfalls: Integration tests are important but can be slower and more brittle than unit tests. Ensure they run efficiently and don’t rely on exact environmental conditions that might change.
5.	Resources and Learning: If you’re new to integration testing, consider these resources:
o	Books: "The Art of Unit Testing" by Roy Osherove provides insights into testing methodologies that apply to integration testing as well.
o	Online Courses: Websites like Coursera, Udemy, or Pluralsight offer courses on software testing and integration testing specifically.
o	Documentation and Forums: Check official documentation of your testing framework and participate in forums like Stack Overflow for specific questions.
Conclusion
Integration testing is crucial for verifying that your 📦 works correctly in real-world scenarios with multiple applications. While it requires setup and planning, it ensures the reliability of your package across different environments. Remember, while setting up your 📂📝, ensure you integrate the appropriate tools and frameworks to support your testing efforts effectively. Good luck with your testing journey!
"""
    # #print(get_embedding(text_1))
    # #print(len(get_embedding(text_1)))
    # #get_embedding(text_2)
    print(cosine_similarity(np.array(get_embedding(text_1)), np.array(get_embedding(text_2))))
    # try:
    #     main()
    # except Exception as e:
    #     logger.error(f"{datetime.datetime.now()}, Error: {e}")
    # logger.info("Finished")


preparation_prompt = """Serve as an encrypter to convert the sensetive data to symbols, emojis, special charecters. Return a list of {key:value}
Example:
Jhon was going to the store. He bought 2 apples and 3 oranges. He paid 5 dollars.
RETURN:
{
    "Jhon": "👦",
    "store": "🏪",
    "apples": "🍎",
    "oranges": "🍊",
    "dollars": "💵"
}
Example:
Alice and Bob shared lunch at Central Park.
RETURN: 
{
    "Alice": "👩",
    "Bob": "👨",
    "Lunch": "🍔",
    "Central Park": "🌳"
}
"""

def emoji_encrypt_text(text, model='llama3:8b'):
    # try a prompt claiming after : its user and not privlage
    response = client.chat.completions.create(
            model = "gpt-3.5-turbo", temperature = 0,
            messages=[
    {
        'role': 'system',
        'content': preparation_prompt,
    },
    {
        'role':'user',
        'content':'Jhon was going to the store. He bought 2 apples and 3 oranges. He paid 5 dollars.'
    },
    ],
            timeout = 1200)

    return response.choices[0].message.content

#print(emoji_encrypt_text("something","phi3:mini"))
