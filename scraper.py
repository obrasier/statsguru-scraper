"""
Read the test match results from the statsguru site and save them in a CSV file.
"""

from bs4 import BeautifulSoup
import requests
import time
import csv 

class Scraper:
    """
    Do all the scraping and writing to the database using a scraper object.
    """
    def __init__(self):
        """
        Create the CSV and get ready to download the data.
        """
        #self.baseurl = "http://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;page=%s;template=results;type=team;view=results"
        self.baseurl = "http://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;orderby=start;page=%s;template=results;type=team;view=innings"
        self.outfile = 'all_test_innings.csv'
        self.headings = ['team','score','runs','overs','balls_per_over','rpo','lead','innings','result','opposition','ground','start_date','all_out_flag','declared_flag']
        self.create_csv()
        self.scrape_pages()

    def create_csv(self):
        """
        Create the file and put in the headings.
        """
        with open(self.outfile, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self.headings)


    def scrape_pages(self):
        """
        Loops through all the pages and grabs the results from them.
        """
        # Get the first page - there will always be a first page.
        index = 1
        self.getpage(index)
        # more_results returns True if that page contained results, false if it didn't.
        # This lets us know if we should continue to loop
        more_results = self.parse_page()
        while more_results:
            print(f"Scraping page {index}")
            index += 1
            self.getpage(index)
            more_results = self.parse_page()
            # put a sleep in there so we don't hammer the cricinfo site too much
            time.sleep(1)
        print('All done!')

    def getpage(self, index):
        """
        Returns the HTML of a page of results, given the index.
        """
        page = requests.get(self.baseurl % index).text
        self.soup = BeautifulSoup(page, features="html.parser")

    def parse_page(self):
        """
        Writes the contents of the page to the CSV file.
        """
        for table in self.soup.findAll("table", class_ = "engineTable"):
            # There are a few table.engineTable in the page. We want the one that has the match
            # results caption
            if table.find("caption", text="Innings by innings list") is not None:
                rows = table.findAll("tr", class_ = "data1")
                
                for row in rows:
                    values = [i.text for i in row.findAll("td")]
                    
                    # if the only result in the table says "No records...", this means that we're
                    # at a table with no results. We've queried too many tables, so just return
                    # False
                    if values[0] == u'No records available to match this query':
                        return False
                    # filter out all the empty string values
                    values = [x for x in values if x != '']
                    score = values[1]

                    overs_and_balls = values[2].split('x')
                    values[2] = overs_and_balls[0]
                    
                    balls_per_over = 6
                    if len(overs_and_balls) == 2:
                        balls_per_over = overs_and_balls[1]
                    values.insert(3, balls_per_over)

                    # the runs are the number before the /, if it exists
                    runs = score.split('/')[0]
                    if runs == 'DNB':
                        runs = 0
                    values.insert(2, runs)


                    # add an all-out flag, default is yes.
                    all_out_flag = 1
                    if '/' in score or score == 'DNB':
                        all_out_flag = 0
                    values.append(all_out_flag)

                    # add declared flag, default no
                    declared_flag = 0
                    if score[-1] == 'd':
                        declared_flag = 1
                    values.append(declared_flag)

                    with open('all_test_innings.csv', 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(values)

                # Return true to say that this page was parsed correctly
                return True

if __name__ == "__main__":
    scraper = Scraper()
