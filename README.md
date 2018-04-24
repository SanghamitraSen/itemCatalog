# itemCatalog
FSWD project

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
