This section covers the basics for administering the validation hub. It will include step-by-step instructions, as well as planned upgrades to automate these processes in the future. 

# Manual Method

This is to document how to manually create and update an analysis and its supporting files. While intended for maintaining the early release, use of this method should be deprecated as soon as a functional automated method is implemented, in order to reduce long-term work and human error.

## Adding an Analysis

An analysis is added using the following steps:

* Navigate to https://api.pv-validation-hub.org/admin
* Sign in to the API. Credentials should be shared securely from dashlane, and only to administrators.
* Select "Analysiss"(the extra "s" is not a typo, but a Django-ism), and in the top right corner select "Add Analysis". Type in your analysis name, and hit save.

Once this is complete, your new analysis will show up in the list as "Analysis object (number)". The number in the parentheses is the Analysis ID in the database. This number will be needed in the following section.

## Adding markdown files and images

You will need to clone this repository to complete this section. Create a new branch from develop, and give it a clear name like "add-timeshift-markdown". This lets me know to sync the updated markdown and images to s3 upon merging your PR.

Markdown files are maintained in the frontend/public/assets/{analysis-id} directory. Analyses are tracked in numerical order within the postgres database, and the front-end uses the ID from the database to pull the correct markdown files for the analysis from the corresponding directory in the s3 bucket. 

There is also a "development" directory that is used for local development. You can run a development instance using several simple steps:

* Make sure you have node/npm installed. If you don't have it, follow the ![docs](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
* Change to the frontend directory, which contains the package.json file.
* In your terminal, Run ```npm install``` to install the node dependencies
* Run ```npm run build``` to build the front-end
* Run ```npm start``` to run the frontend

Each filename is important. Below is the dynamic element they correspond to: 

cardCover.png       ==> This is the image that will go on the analysis card, when selecting an analysis.
headingCover.png    ==> This is the banner image across the top of the page. If too small, the image repeats to fill the space.
dataset.md          ==> The markdown file to describle the dataset in the data tab.
longdesc.md         ==> The markdown file used for the overview tab in an analysis.
ruleset.md          ==> The markdown file used for the "Rules" tab, will be renamed to "instructions"
shortdesc.md        ==> The markdown file that is used on the card. Needs work for a cleaner implementation, with defined limits due to card size.

TODO: Add instructions once dynamic image method is implemented and finalized.

Modify the images and text in the "development" directory until you are satisfied, and then copy the files from the development directory over to the numbered directory, corresponding to the analysis number from the last section. If the directory does not exist, create it. 

## Updating markdown and images


This development instance of the frontend can then be used for testing your updated markdown and image files. 
