<p align="center">
  <img alt="Icon of Rhbbitica bot" src="img/icon.png">
</p>

<h2 align="center">
  Rhabbitica
</h3>

## Introduction
I am Rhabbit, your loyal assistant who will be joining you on your journey of self improvement.

Together, we will explore the world of Rhabbitica and quest for the ancient scrolls of Habitica and Telegram.

Check out the wonderful stickers made!
[t.me/addstickers/hnr2020](https://t.me/addstickers/hnr2020)

Remember to bring your friends along too!

## Getting Started
This telegram bot is made using Python 3+ as well as several libraries that you would need to install before starting.

1. Install directly from the pipfile: `pipenv install --dev` or individually:
    * Python 3.8 (recommended)
    * python-telegram-bot
    * requests
    * python-dotenv
    * autopep8
    * pylint (dev)

2. Set up the .env file by getting ready these:
    * Telegram bot api key
    * Habitica User ID and token KEY

3. Fill up the `.env.example` file and rename to `.env`

4. You may begin by running the program from `main.py`

## About
This project is forked from the [original Rhabbitica Github project](https://github.com/ElasticBottle/hackAndRoll2020) created during the Hack&Roll 2020 event.

I have cleaned up the code significantly and made several changes that deviate slightly from the original package.

They include splitting the codebase into multiple files specially based on their function instead of having everything in a single file as well as cleaning up the API calls for `/view` and `/create` commands.

However, I have removed the scheduled reminders asking users about the completion status of their outstanding tasks. This is because after the migration of scheduling to using **jobs** from `python-telegram-bot`, there are concerns about the scalability of such function to multiple users.

## Contributing
There are a few ways to contribute to this project and will always be welcomed:
1. You can report new bugs by submitting a new [issue](https://github.com/wonyk/Rhabbitica/issues)

2. Improve the documentation by creating or improving the [Wiki](https://github.com/wonyk/Rhabbitica/wiki)

3. Making a [pull request](https://github.com/wonyk/Rhabbitica/pulls) to add in new functions

## Credits
I would like to thank my teammates during Hack&Roll 2020 for working closely to come out with the original repo.

Thank you to Eleanor for the wonderful ideas, stickers and graphics that made this project lively and beautiful.

Also, I am grateful to Winston for coming out with this basic idea and guiding me through Python which is not my main programming language.
