# limoncHello
limoncHello is a TCP chat application programmed in Python based on OO programing and uses an encryption technique to maintain privacy and security of messages sent between users

## Authors
Created by Martin MOULIN, Morgan TONGLET, Antoine TRILLET, Gilles THEUNISSEN

## Features
 - User commands (`/help`, `/online`, `/quit`, `/join`, `/display`, `/room`, `/roommates`, `/mp`, `/conv`, `/lobby` and `/load`)
 - Message encryption for user privacy purposes
 - Multiple client support

## Installation & Setup
Download this file (`ChatApp`) and check if the `pyDH` and `cryptography` packages are already installed in your python IDE. If it is not the case, just run `pip install pyDH` and/or `pip install cryptography` in your IDE's terminal.

## Usage
Hereafter will now be detailed the user guide to use our chat app **limoncHello**:

After downloading the file, go to its src directory and run `chat-server.py` to start the server-side application and/or `chat-client.py` to start the client-side application. In order for **limoncHello** to run properly, the `chat-server.py` should be started before `chat-client.py`. `chat-server.py` is responsible for managing the conversations between users, while `chat-client.py` will be used when a user wants to chat on **limoncHello**. Hence, users of the chat app will only run `chat-client.py`.


Once you have started the client-side appplication (`chat-client.py`) the chat app will request you to choose between two options:

 **1. Login (/l):** The server will request from the user a _`username`_, if the inserted username is not in the database then server wil throw an error and ask the user to try again. If the username is correct, the server will then ask for the password linked to the account (again an error message will be sent if the password is incorrect).

 **2. Subscribe (/s):** The server will request the user to input a _`username`_, if the chosen username is unexistent in the database then the server will ask for a password. However, if the _`username`_ is already taken the server will ask the user to choose a new username until it is valid.
 
After subscription or login, the user will be taken to the `lobby` (aka Room 0). This is the general conversation to which every user has access. Every user can receive and send messages in the lobby, as well as use commands incorporated in the aplication. These different commands have been cited above in the features section and will be described here below.

 - **/help:** Shows all available commands that the user can benefit from
 - **/online:** Indicates which users are online
 - **/mp:** Creates a conversation with another user. Type `/mp`and then **ENTER**, the server will then request the user to input the username of the user they which to reach.
 - **/conv:** Creates a conversation with as many people the user wishes. Type `/conv` followed by the **ENTER** key, the server will then give the user indications in order to add users to the conversation.
 - **/roommates:** Indicates the users which are in the same room as the user (online & offline)
 - **/room:** Indicates the room in which the user is currently in
 - **/join:** Enables the user to join any room that the user has access to. Type `/join` followed by the **ENTER** key, the server will then ask for the room number the user wishes to enter. If the user does not have access to the chosen room, the server will notify the user with an error.
 - **/display:** Displays the rooms to which the user has access.
 - **/lobby:** Shortcut to access the lobby (or Room 0) from any other room/conversation
 - **/load:** Loads the the rooms message history
 - **/quit:** Logs out the user from the application and renders him offline.

**Note:** The aforementioned commands are available in every room, not just the lobby.

When inside a conversation, the user just needs to type the message desired and then press the **ENTER** key to send it. The other users inside the same conversation will receive the message but not the users which don't have access to the specific conversation.


## Serialisation
In the src repository, there is a serialisation file whose sole purpose is to save data, the server side of the chat app is responsible of this. The user information is stored to a text file (`users.txt`) in the form of the username and password for each user. The history of every conversation is saved as well, also in a text file (`conv#.txt`) where **#** is replaced with the conversation number (e.g message history of the lobby is stored in `conv0.txt`). Each message is saved with its sent time, authort and of course the message itself. As noted before, there is an encryption system for each conversation. This means that the messages saved in the `conv#.txt` are encrypted and, hence, indecipherable. All the conversation text files are regrouped in a single file named `Conversations`.
