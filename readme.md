 # Python decentralized chat

##### What it can do:
- You can write a direct message using the IP of another user that runs this app too.
    -   Message can be simply plaintext or ciphertext.
    -   Default is ciphertext
- Encryption 
    - This app uses a public RSA key to encrypt messages to you.
    - Each message signs using your private key of RSA, so the receiver can verify that you send this message using your public key.
- Chat
    - Since its system is decentralized chat information is stored in each member of chat separately. You can think of it as a list of recipients. 
    - Each chat has admins in any chat first admin is the creator of chat 
    - You can add admin by sending an invitation to be an admin if the user accepts it information about it is sent to everyone, and everyone counts this user as one more admin. 
    - It has opportunity to ban members of chat. That is how it held:
        - The admin sends a message to everyone in a certain chat that the user was banned and the time when to unban him can be unlimited. After this member of chat just ignoring messages that banned user sends in this chat and not sending messages to banned users when they are writing to the chat 

## How to run it:
1. Copy this repository to youc computer
2. Install requirentments.txt  using ```pip install -r requirentments.txt```
3. Crate database to store messages, chats, members, banned users and admins using ```python create_db.py```
4. Run the app and enjoy terminal chat 🤤🤤🤤 you can ```python main.py```

## Environment variables
It is recommended to specify environment variables:
```DB_URI``` - Path to database file (you can leave its default value)
```USERNAME``` - How other users will see your name

Feel free to contact me about this project and chat securely!❤️
