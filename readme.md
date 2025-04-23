ELASTICSERACH INTEGRATION WITH ARIADNE(GRAPHQL LIBRARY)

1. Clone the repository to your local machine
2. In the terminal be in the `AriadneGraphQL-Elasticsearch-DemoApplication` folder
3. Create a new virtual environment with the following command
    ```
    python -m venv myvenv
    ```
4. Activate the virtual environment by running the following command<br>
   On windows
   ```
   myvenv\scripts\activate
    ```
   on macOS or Linux
   ```
   myvenv/bin/activate
   ```
5. Install the required dependencies using `pip install -r requirements.txt`
3. Set up the elasticsearch
4. Once the Elasticsearch setup is done, you can check the connection through http://localhost:9200/
5. Run the application using "uvicorn server:app --reload"