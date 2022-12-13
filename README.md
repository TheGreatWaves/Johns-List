# Johns-List
Database class project

Team name: John!
Members: Leah, Praew, Ochawin

# Introduction

Our project is an anime and manga list-keeping website called John's List. Keeping track of what anime and/or manga have been watched or read easily become more of a hassle as the number of series grow. This is where our website comes in as a user-friendly media monitoring service. The primary objective is letting users keep record of anime and manga, as well as related information. Users can keep two lists, watch and completed. The service also lets users rate their series and allow filtering by tags.

The secondary objective is to promote interactions within communities of friends. For this we let users join groups where shared content lists can be kept. This is to support list-keeping of group watching or reading acitvities.

If there is no anime or manga on the site, users can add and edit the content entries freely. This is inspired by AniDB system, so users can play an active part in editting and updating the contents in a similar way to a wikia. 

# Diagram

Our ER diagram is as followed. We decided to put anime and manga together in the same table and call it as content because if we separate them there'd be a lot of similar repeated relation involving them. This would clutter the diagram and almost double the number of relations. 


![ER diagram](/doc/ER_diagram.png)


# User Interface

This is the homepage. On this page three samples of the contents are shown, randomised, top ranking, and most popular. Users can click on any of the posters to go directly to the corresponding content page.

## Home Page


![Home page](/doc/homepage.png)


Scroll down to get these.


![Home page](/doc/homepage2.png)

![Home page](/doc/homepage3.png)


At the top of every page is the nav bar. On the leftmost is the site's name that user can click to return to the home page. On the rightmost is the sign up and sign in. If a user is signed in, the sign in will be replaced with the username nad sign out instead.


## Navbar

![Navbar](/doc/navbar.png)


The About next to John's List takes user to the about page which contain some information about the site as well as an FAQs.


![About](/doc/about.png)


Next to that on the nav bar are the Community drop down where users can create and search for groups and users, and the Content drop down where users can add and search for contents.


![About](/doc/create-search-group.png)

![About](/doc/add-search-content.png)


## Sign up / Sign in / Sign out

Users can sign up to get access to lists, make groups and edit pages. Availibility of username and email will be checked, and users will need to retype password to avoid mistake. The password entired by the user is hashed before storing in the database for security and privacy. Foreign key is used to make sure that the sequel and prequel are content that have already existed in the content table.


![Sign up](/doc/signup.png)


After successfully signing in new users will be directd to the sign in page. Users can use either email or username for signing in.


![Sign in](/doc/signin.png)


As the nav bar is available on every page users can sign out at any time.


## Searching

Users can type in the search bar to search for the things they want. The keyword is not case sensitive and the result will return any entry with the string it is. The users are not requried to type an exact match. If the search button is clicked on while the bar is left blank it will return all the items in the category in alphabetical order. 

For the community search there is a drop down next to the search bar for determining whether the search is for users or for groups.


![Search user and group](/doc/search-user-group.png)

![Search content](/doc/search-content.png)


## Creating


Users can either add content, which they need to fill in the title and whether it's an anime or a manga. Then the page will switch to the newly created content page where further info can be edited. For creating group only the name need to be provided. The user is then again directed to the newly created group page. 

These can be accessed from the nav bar.


![create content](/doc/create-content.png)

![create group](/doc/create-group.png)


## Content

The content page contains 
- content ID
- the poster image of the content
- Synopsis
- type of content (aniem or manga)
- status (completed, ongoing, or unspecified if no user have edited)
- score by the users, and the number of users who scored
- ranking of the content based on the score.
- prequel / sequel / adaptation
- tags


![Content page](/doc/content-info.png)

![Info column](/doc/anime-info-side.png)


There are several actions a user can take.

They can add the content to their personal list, or the list of a group they are in. If the user add the content to their personal list it will automatically go to the watch list. If the add to group is selected, there will be a prompt asking which of the group the user belongs to they want to add the content to.


![add to list](/doc/add-content-to-list.png)


![add to group list](/doc/add-to-list.png)


They can also rate the content by clicking the set rating on the top right. When clicked a rating module will show up with a slider that user can pick a score off from 1 to 10. After submitted, they will see the update to the rating right away.
 
![rating](/doc/rating.png)


They can also edit the information on the content page as shown. Notable things to mention is that the tags are input by separating different tags with commas. The poster can be changed by adding a link of the image. The user click on the save button to save the changes of the edit. It should be noted that the title is not allowed to be left blank.


![edit](/doc/content-edit.png)


Finally the user can click on any of the tags. This will leaed them to a page that list all the contents with that tag assigned to them.


![tag](/doc/tag.png)


## User profile page and list


Users can access their profile page by clicking on their username in the nav bar. It will lead them to a page where they see their

- profile picture
- bio
- groups they joined or created

 There is also the create and search buttons for group for quick access.
 
 User can click on the edit button on top right to edit the profile picture and bio similar to the content page. Below is the default profile picutre of user before they edit. On this page they can change their password which will again requires password confirmation. it will also require that the user provide the current password on top of the new one.

![user page](/doc/user-page.png)

![edit](/doc/user-edit.png)

![default pfp](/doc/default.png)


Here a user can also get accress to their watch and complete lists, which contains the entries that were added from the respective content pages. In the watch list the user can move any of the entries to the complete list, which is used when they are done watching or reading the anime/manga. In the completed list, user can remove the entries in case they put it there by accident.


![watch list](/doc/watch.png)

![complete list](/doc/complete.png)



## Community


User can create groups or join them. Click on the name of a group wherever it appears on a list will take user to the group page which contains

- group name
- group info
- group profile pic
- group watch and complete list
- member list

If a user is not a part of the group, the top right is the button for joining. This is replaced by the edit  button if user is not sign in or is not part of the group. This leads to the edit page where users who joined the group can edit the group name, info, and profile pic. User can again click save to change the group information. Next to the edit button is the leave button which users can use if they don't want to be a part of the group.


![group page](/doc/group-info.png)

![edit](/doc/group-edit.png)


Users can also click on the watch and complete list just like on the user page. The difference is that this list is editable by every member of the group.




# SQL Script

When we made the schema for the project we used SQLAlchemy for convenient and to protect against SQL injection. While they look different the logic behind them are basically the same. Generally we assign interger ID for entities like user, group, content etc., which act as the primary key. Other that that we also use just the name, as in the case of genre.

The entirety of the table creation schema using SQLAlchemy is available in **init_schema.py** of this repository. Note that there are some unused tables of things we haven't implemented into the website due to time constraint.

Similarly, sample data for populating the table is available in **populate.py**

init_schema.py
populate.py

Link to Github repository:
https://github.com/TheGreatWaves/Johns-List

Link to video:
https://www.youtube.com/watch?v=Xt_cYK-hVhg