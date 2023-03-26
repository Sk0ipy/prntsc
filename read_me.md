# this project is a school project:
 - it is a website that scans random printscreens from the website "https://prnt.sc/"
 - if the printscreen exists, it will store it in a database and sends a preview in the discord channel

## How does it work:
 - the website is  cloudfare protected, so we need to bypass it
 - so we cant scrape the website pics directly
 - but the pictures are stored in "images.prntscr.com/image/......." so we can scrape them directly
 - the dotes are random, so we need to generate random strings
 - if we get a match we store it in the database and send it to the discord channel

## **How to use**:
 - 
