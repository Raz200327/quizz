Quizz CLI App


       ___  _   _ ___ __________
      / _ \| | | |_ _|__  /__  /
     | | | | | | || |  / /  / / 
     | |_| | |_| || | / /_ / /_ 
      \__\_\\___/|___/____/____|

Description:
A simple command-line interface (CLI) app for creating and managing quizzes. This app allows users to create new quizzes, use or delete previous quizzes, access a public quiz database and publish personal quizzes to the public database.

Installation:

       python -m pip install --user pipx
       python -m pipx ensurepath
       pipx install git+https://github.com/Raz200327/quizz.git
       
       
Usage:
- `quizz -nq` or `quizz --new-quiz`: Create a new quiz.
- `quizz -pq` or `quizz --prev-quiz`: Use a previous quiz.
- `quizz -del` or `quizz --delete`: Delete a previous quiz.
- `quizz -pd` or `quizz --pub-quiz`: Access the public quiz database.
- `quizz -pub` or `quizz --publish`: Publish your personal quiz to the public database.
- `quizz -h` or `quizz --help`: View documentation.
- Press `CTRL+C` to exit the application.

Features:
- Create new quizzes.
- Manage and use previous quizzes.
- Delete unwanted quizzes.
- Access a public quiz database.
- Publish personal quizzes to the public database.
- View helpful documentation.

Contributing:
Feel free to contribute to the development of this CLI app by submitting issues or pull requests on the GitHub repository.

License:
This project is licensed under the MIT License - see the LICENSE.md file for details.
