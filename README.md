<h1 align="center">
  <br>
   📢 Downtime Detector 📢
  <br>
</h1>
<p align="center">A simple discord bot to notify you whenever another discord bot goes offline!</p>

## ❗ Features  
* 🔐 All commands are admin only 
* 🔍 Monitor any discord bot  
* 🤖 Alerts in DMs or channels 

## ❓ How to use it?
0. First, you'll need to host a mysql database somewhere, [here's an helpful guide to host it on ubuntu linux](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04)
1. Create a .env file and copy paste the contents of .env.example
2. Fill all the variables with required details
  - BOT_TOKEN is the discord bot's token, get it from the [developer portal](https://discord.com/developers/applications)
  - RDS_HOST is the ip address of the mysql database, use 127.0.0.1 if you're hosting the database locally
  - RDS_PORT is the port of mysql database, by default it is 3306 in most cases
  - RDS_USERNAME is the user that has access to the database you're going to use
  - RDS_PASSWORD is the password of the user
  - RDS_DATABASE is the database's name that you're using
3. Now run main.py and you should be good to go

Feel free to reach out to [me](https://discord.com/users/821306636605718548) on my [discord server](https://discord.gg/3rEAjXm8gb) if you need any help. 

## 📖 License
Released under the MIT license.


Consider giving the repository a 🌟 if it was helpful!
