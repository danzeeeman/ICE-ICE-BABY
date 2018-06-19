# LinkedIn members who work for ICE

Browse it here: https://antiboredom.github.io/ice-linkedin/

Please note that this script requires a LinkedIn account with a premium membership

In order to run the code, first clone the repository, then install requirements:

```
pip install -r requirements.txt
```

Next, you'll need to edit `header.py` with info about your linkedin account. This is a bit tedious. 

1. Log in to your linkedin account in Chrome
2. Go to the sales navigator page for ICE: https://www.linkedin.com/sales/search?pivotType=EMPLOYEE&pivotId=533534
3. Open your browser's development tools, and then click on the `network` tab, and then select `XHR`
4. Scroll to the bottom of the page and click the `Next` button
5. You should see a url appear on the network tab. Right click and select `Copy as cURL`
6. Open up https://curl.trillworks.com/ and paste into the `curl command` area
7. Copy everything in between `headers = {}` into `header.py`

Run the script with 

```
python linked_in_scraper.py
```
