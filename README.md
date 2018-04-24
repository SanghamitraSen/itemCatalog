# itemCatalog
FSWD project(Backend)
## Project Description
This Web application allows you to create a catalog system by allowing you to add,edit and delete category and items provided proper authorisation is present after authentication by third party. Viewing the catalog doesnt require authentication
## Pre-Requisites
  * **Python** should be installed. 
    You can get it from:https://www.python.org/downloads/
  * **A terminal like Git Bash.**
    If you don't already have Git installed, download Git from git-scm.com.
  * **VirtualBox.**
    You can download it from https://www.virtualbox.org/wiki/Download_Old_Builds_5_1. Make sure to choose October 2017 version so that it is compatible with vagrant.
  * **Vagrant.**
    You can download it from https://www.vagrantup.com/downloads.html
  * **Google account** is required.Create one here:https://accounts.google.com/signup/v2/webcreateaccount?hl=en&flowName=GlifWebSignIn&flowEntry=SignUp
## Steps to execute the project
  * Clone vagrant repo from udacity-->https://github.com/udacity/fullstack-nanodegree-vm/tree/master/vagrant.
  * Clone this repo and place it inside vagrant folder of above and cd into vagrant folder.
  * Start the virtual machine using command:**vagrant up**
  * Once done,login using **vagrant ssh** and then type **cd /vagrant**
  * To execute the queries run this command: **python project.py**
  * Visit **localhost:5000** and login inorder to add category or item.
## JSON Endpoints

`/category/JSON` - Returns JSON of all categories in catalog

<img src="screenshots/categoryJSON.png" width="1000">

`/category/<int:cid>/list/<int:mid>/JSON` - Returns JSON of selected item in category

<img src="screenshots/particularitemJSON.png" width="1000">

`/category/<int:cid>/list/JSON` - Returns JSON of all items in particular category in catalog

<img src="screenshots/jsonforparticularcategory.png" width="1000">

## Landing Page(not yet logged in)
`/category`

<img src="screenshots/landing.png" width="1000">

## Authentication(Logging in)

`/login` 

<img src="screenshots/authentication.png" width="1000">

## Landing Page(Logged in)

`/login` 

<img src="screenshots/loggedin.png" width="1000">


## Adding New Category
`/category/new` 
<img src="screenshots/newcategory.png" width="1000">

## Adding New Item
While adding info about item, in category list only those categories appear which that user has created
`'/category/item/new/`
<img src="screenshots/newItem.png" width="1000">

## Item List(not authorised)
Example of logged in but not authorised
<img src="screenshots/loggedinbutnotauthorised.png" width="1000">

## Item List(authorised)
Example of logged in & authorised
<img src="screenshots/itemslistwhenloggedinandauthorised.png" width="1000">
