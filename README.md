## Project Description
Item Catalog - The second project in Udacity's Full Stack Web Developer Nanodegree Program. We are required to create a modern web applications perform a variety of functions.

This project also provides 3rd part OAuth using Github.

## Requirements
1. VirtualBox and Vagrant installed.
2. Udacity's Vagrant [settings](https://github.com/udacity/fullstack-nanodegree-vm)
3. Python 3.5 or above.
4. All the packages included in the `requirements.txt` file.

##  How to run the website?
 1. Bring the server up by typing `vagrant up` in your terminal, and inside the vagrant folder located in the settings file above (might take a couple of minutes while it downloads the required files).
 2. After you finish downloading everything, you need to run the server by typing `vagrant ssh`.
 3. Enter your shared folder by typing `cd /vagrant` (the same folder from step 1), and then copy the project files here.
 4. First run the `create_database.py` file to prepare the database, and populate it by running the `populate_database.py` file.
 5. Run the `app.py` file, and hopefully it will present you with the needed results when you connect to `localhost:5000`.