# market_sentimentalism

ETL tool to extract news and social data mostly about stocks but can work for anything. Initial implementation was for extracting news data, generating sentiments, predicting tomorrow's opening price of a stock and plotting some charts to understand how a stock is performing, etc.

This is not complete and is elementary at the moment but can be a great start for total beginners in building web apps in general or in python/flask/jinja, etc.

To get started all you have to do is clone this repo cd into the project directory and install the required libraries as follows,

```shell

pip install -r requirements.txt

```

requirements.txt has listed all the libraries that you'd want install to get started.

Once you install the required libraries, you can run the app by executing the following in your terminal:

```shell

python marketsentimentalism2.py 

```

This will run your localhost server which will allow you to make http requests from your browser as follows. For example to see the dashboard, go to the address, http://localhost:5000/dashboard/.


